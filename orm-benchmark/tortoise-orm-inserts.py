import asyncio
from tortoise import fields, Tortoise
from tortoise.models import Model
import time

QUERIES_NUM = 3000

class User(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)

async def run_benchmark():
    await Tortoise.init(
        db_url='postgres://postgres:postgres@localhost:5432/postgres',
        modules={'models': ['__main__']}
    )
    await Tortoise.generate_schemas()

    start_time = time.time()

    for _ in range(QUERIES_NUM):
        await User.create(name='Test User')
    duration = time.time() - start_time
    print(f"Tortoise ORM: {QUERIES_NUM} insert queiries is completed in {duration} seconds.")

    await User.all().delete()
    print("Cleanup OK.")

    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(run_benchmark())

