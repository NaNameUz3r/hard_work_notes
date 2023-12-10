### FIRST EXAMPLE

```python
@router.post("", response_model=IdResource)
async def process_queue_data(
    payload: MessagePayload,
    x_request_id: Annotated[str, Header()],
    x_version: Annotated[date, Header()],
    auth_data: Annotated[AuthData | None, Depends(get_auth_data_optional)],
    x_entity_id: Annotated[UUID | None, Depends(get_entity_id_optional)],
    x_service_name: Annotated[str, Depends(get_service_name_from_headers)],
    hide_sensitive_data: Annotated[bool, Header()] = False,
):
    if payload.exchange.type == "fanout" and payload.exchange.name == "amq.direct":
        raise HTTPException(
            status_code=400,
            detail="amq.direct is a predefined RMQ name. It can't be fanout, only direct",
        )

# could be just moved to exchange model root_validator, in schemas module:

FORBIDDEN_FANOUT_NAMES = ["amq.direct"]

class ExchangeTypes(StrEnum):
    direct = enum.auto()
    fanout = enum.auto()


class Exchange(ConfigMixin):
    type: ExchangeTypes
    name: str
    @root_validator
    def forbidden_fanout_names(cls, attributes: dict[str, Any]):
        exchange_type = attributes.get("type")
        exchange_name = attributes.get("name")
        if exchange_type == ExchangeTypes.fanout and exchange_name in FORBIDDEN_FANOUT_NAMES:
            raise ValueError(f"{exchange_name} is a predefined or forbidden RMQ name. It can't be fanout, only direct")

        return attributes

# After this, we just can remove redundant check from the `process_queue_data` method.
```

### SECOND EXAMPLE

```python

# somewhere in code...
    mentions_arr = []

### ... some more code

    await self._validate_mentions(mentions=mentions_arr, group_dict=group_dict)

# then we have this internal method:
async def _validate_mentions(self, mentions: list, group_dict: dict):
    if mentions:
        missed_groups = set(group_dict) - set(self.AVAILABLE_GROUPS)
        if missed_groups:
            raise BusinessLogicError(...)

        for group, ids in group_dict.items():
            if not ids:
                continue
            scenario_class = self.AVAILABLE_GROUPS[group]
            scenario = scenario_class(entity_id=self.entity_id, auth_data=self.auth_data)
            hit_ids = await scenario.check_ids(ids=ids)
            missed_ids = ids - set(hit_ids)
            if missed_ids:
                raise BusinessLogicError(...)

# why we even can pass a generic empty list in the `_validate_mentions`?
# All these look like a request for implementing some local type system,
# because such generic lists (list[Any]) look not okay.
# this is not mentioned in the snippet, but mentions list is filled up with
# dictionary key-vals. So it definitely will look better with some custom types.

# Even that this is internal helper method, it should have some solid "internal" interface.

# Minimum effort we can do here directly is to prohibit passing empty mentions and group_dict
# at least like that:
async def _validate_mentions(self, mentions: list, group_dict: dict):
    if len(mentions) == 0:
        raise ValueError("No mentions to check")
    if len(group_dict) == 0:
        raise ValueError("Can't check mentions with an empty group dictionary")
    ...

# This will enforce the user of this method check values he tries to pass in this function,
# it is always bad to call such a check helper function always in a blind way.
```

### THIRD EXAMPLE

```python
# A completely incomprehensible plot twist with default None in
# rabbitmq worker class' `consume` method

async def consume(
    self,
    batch_size: int | None = None,
    exchange_name: str | None = None,
    exchange_type: str | None = None,
):
    """Start consuming.
    If lost rabbit _connection: put a message in xq and stop consuming
    If an exception occurred: put a message in xq and continue consuming
    """
    if batch_size is None:
        batch_size = self.default_batch_size
    if exchange_name is None:
        exchange_name = self.default_exchange_name
    if exchange_type is None:
        exchange_type = self.default_exchange_type

    if batch_size <= 0:
        raise ValueError("Batch size should be greater than 0")

    self.batch_size = batch_size
    ...

# Yet, we cannot call `self....` in a method argument, but we are not restricted to
# set default values as module constants, thus it goes this way:

async def consume(
    self,
    batch_size: int = DEFAULT_BATCH_SIZE,
    exchange_name: str = DEFAULT_EXCHANGE_NAME,
    exchange_type: str = DEFAULT_EXCHANGE_TYPE,
    ):
    """Start consuming.
    If lost rabbit _connection: put a message in xq and stop consuming
    If an exception occurred: put a message in xq and continue consuming
    """

    if batch_size <= 0:
        raise ValueError("Batch size should be greater than 0")
    self.batch_size = batch_size

# It is obvious that no one can send None in these methods, so why do we even need these checks?
```

### FOURTH EXAMPLE

```python
async def create_person(self, payload: PersonRequest) -> PersonResponse:
    if not any(
        (
            payload.relationship.representative,
            payload.relationship.owner,
            payload.relationship.executive,
            payload.relationship.director,
        ),
    ):
        raise BusinessLogicError("Please, specify a relationship with the entity.")

# where PersonRequest is:

class BasePerson(BaseModel):
    address: PersonAddress | None = Field(None, description="The person's address")
    date_of_birth: datetime.date | None = Field(None, description="The person's date of birth")
    first_name: str = Field(description="The person's first name")
    last_name: str = Field(description="The person's last name")
    email: EmailStr = Field(description="The person's email address")
    phone: str | None = Field(None, description="The person's phone number")
    relationship: PersonRelationship = Field(description="Describes the person's relationship to the entity")
    id_number: str | None = Field(None, description="The person's ID number, as appropriate for their country")
    ssn_last_4: str | None = Field(None, description="The last four digits of the person's Social Security number")

# and PersonRelationship is:

class PersonRelationship(BaseModel):
    title: str | None = Field(None, description="The person's title (e.g., CEO, Support Engineer)")
    representative: bool = Field(
        default=False,
        description="Whether the person is authorized as the primary representative of the account",
    )
    executive: bool = Field(
        default=False,
        description="Whether the person has significant responsibility to control, manage, or direct the organization",
    )
    director: bool = Field(default=False, description="Whether the person is a director of the account's legal entity")
    owner: bool = Field(default=False, description="Whether the person is an owner of the account's legal entity")
    percent_ownership: float | None = Field(
        None,
        description="The percent owned by the person of the account's legal entity",
        ge=0,
        le=100,
    )

# Regarding the fact that the overall schemas design looks a bit weird and cumbersome,
# the least we can do here (if we cannot easily make changes in schemas hierarchy),
# is to ensure that we have such a precondition in the system:
# "relationship should contain at least one field describing a person's business role"
# If it is so, we just can move checks on the schema validator level:

class PersonRelationship(BaseModel):
    title: str | None = Field(None, description="The person's title (e.g., CEO, Support Engineer)")
    representative: bool = Field(
        default=False,
        description="Does does person authorized as the primary representative of the account",
    )
    executive: bool = Field(
        default=False,
        description="Does the person has significant responsibility to control and manage the organization",
    )
    director: bool = Field(default=False, description="Does the person is an legal director")
    owner: bool = Field(default=False, description="Does the person is an legal owner")
    percent_ownership: float | None = Field(
        None,
        description="The percent owned by this person",
        ge=0,
        le=100,
    )

    @root_validator
    def forbid_create_person_without_business_role(cls, attributes: dict[str, Any]):
        is_representative = attributes.get("representative")
        is_executive = attributes.get("executive")
        is_director = attributes.get("director")
        is_owner = attributes.get("owner")

        if all([is_owner, is_director, is_executive, is_representative]) is False:
            raise ValueError("Person relationship should contain at least one business role")

        return attributes

# So this way we forbid it on the "interface" level, roughly speaking.
# Even though it looks cumbersome, we now get rid of these stupid checks everywhere,
# this validator ensures that every new person contains at least one business role.
```

### FIFTH EXAMPLE

```python
def make_message(event_name: str, func_self: SelfProtocol, data: dict) -> SenderMessage | None:
    if not func_self.auth_data:
        return None

    return SenderMessage(
        id=str(uuid4()),
        name=event_name,
        payload=SenderMessagePayload(
            auth_data=func_self.auth_data,
            entity_id=func_self.entity_id,
            data=data,
        ),
    )

# where SelfProtocol is:

class SelfProtocol(Protocol):
    auth_data: AuthData | None
    entity_id: uuid.UUID

# The solution is pretty simple: Do. Not. Allow. None. Please. Just. DON'T:

class SelfProtocol(Protocol):
    auth_data: AuthData
    entity_id: uuid.UUID
```
