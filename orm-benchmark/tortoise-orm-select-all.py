import asyncio
from tortoise import Tortoise, fields
from tortoise.models import Model
import time

QUERUES_NUM = 3000

class User(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)

async def prepare_data():
    for _ in range(QUERUES_NUM):
        await User.create(name='Test User')

async def run_benchmark():
    await Tortoise.init(
        db_url='postgres://postgres:postgres@localhost:5432/postgres',
        modules={'models': ['__main__']}
    )
    await Tortoise.generate_schemas()

    await prepare_data()

    start_time = time.time()
    await User.all()
    duration = time.time() - start_time
    print(f"Tortoise ORM: {QUERUES_NUM} select queries is completed in {duration} seconds .")

    await User.all().delete()
    print("Cleanup OK")

    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(run_benchmark())

