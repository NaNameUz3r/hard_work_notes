
Дано, довольно загруженный CRUD сценарий для пользователей:

```python
class Scenario:
    def __init__(self):
        self.db_session = get_db_session()

    async def create_user(self, payload: UserSchema) -> UserModel:
        user_by_email = await user_scenario.get_user_by_email(payload.email)
        if user_by_email:
            raise HTTPException(status_code=400, detail="Email is already taken by another user.")

        hashed_password = hasher.hash(payload.password)
        user_db_entity = UserModel(
            email=payload.email,
            hashed_password=hashed_password,
            username=payload.username,
            # TODO: add email confirmation mechanism
            is_active=True,
        )
        try:
            self.db_session.add(user_db_entity)
            await self.db_session.commit()
        except SQLAlchemyError as error:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=422,
                detail=f"Error while creating user:\n {error}",
            ) from error
        return user_db_entity

    pass
    # and other crud methods
```

Из за максимально простого и наивного использования orm:

```python
engine = create_async_engine(
    url=settings.pg_conn(),
    future=True,
    echo=True,
    pool_size=settings.POSTGRES_MAX_POOLSIZE,
)


get_db_session = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine,
)

# Model

class UserModel(Base):
    __tablename__ = "users"

    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now())

```


Что можно было бы сделать – выделить все что касается ОРМ и фабрику сессий в отдельную асбтракцию:

```Python
class DBSessionManager:
    def __init__(self):
        self._orm_engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker | None = None
        self._settings: Settings = settings

    def init(
        self,
    ):
        self._orm_engine = create_async_engine(
            url=self._settings.pg_conn(),
            future=True,
            echo=True,
            pool_size=self._settings.POSTGRES_MAX_POOLSIZE,
        )
        self._session_factory = async_sessionmaker(
            autocommit=False,
            bind=self._orm_engine,
        )

    async def close_connections(self):
        if self._orm_engine is None:
            raise Exception("Database session manager is not initialized")
        await self._orm_engine.dispose()
        self._orm_engine = None
        self._session_factory = None

    @contextlib.asynccontextmanager
    async def make_connection(self) -> AsyncIterator[AsyncConnection]:
        if self._orm_engine is None:
            raise Exception("Database session manager is not initialized")

        async with self._orm_engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def get_session(self) -> AsyncGenerator:
        if self._session_factory is None:
            raise Exception("Database session manager is not initialized")

        async with self._session_factory() as session:
            yield session
```

И Инкапсулировать в класс модели пользователей весь CRUD:

```python
    @classmethod
    async def create(cls, db: AsyncSession, **kwargs):
        model_object = cls(**kwargs)
        db.add(model_object)
        await db.commit()
        await db.refresh(model_object)
        return model_object

    @classmethod
    async def get_by_id(cls, db: AsyncSession, id: uuid.UUID):
        try:
            model_object = await db.get(cls, id)
        except NoResultFound:
            return None
        return model_object

    @classmethod
    async def get_by_email(cls, db: AsyncSession, email: str):
        return await db.execute(select(cls).where(cls.email == email))

    @classmethod
    async def get_all(cls, db: AsyncSession):
        return (await db.execute(select(cls))).scalars().all()

    @classmethod
    async def delete(cls, db: AsyncSession, id: uuid.UUID):
        return await db.execute(delete(cls).where(cls.id == id))

```

Тогда сценарий будет выглядеть читаемее и короче:

```python
    async def create_user(self, payload: UserSchema) -> UserModel:
        user_by_email = await UserModel.get_user_by_email(payload.email)
        if user_by_email:
            raise HTTPException(status_code=400, detail="Email is already taken by another user.")

        user_payload = payload.model_dump(exclude={"password"})
        hashed_password = hasher.hash(payload.password)
        user_payload["hashed_password"] = hashed_password
        return await UserModel.create(db, **user_payload)

```

Если честно, я не до конца уверен в адекватности инкапсуляции crud в класс модели

---
