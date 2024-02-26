import asyncio
import asyncpg
import time

QUERIES_NUM = 3000


async def run_benchmark():
    conn = await asyncpg.connect(
        user="postgres",
        password="postgres",
        database="postgres",
        host="localhost",
    )

    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id serial PRIMARY KEY,
            name text
        )
    """
    )

    start_time = time.time()
    for _ in range(QUERIES_NUM):
        await conn.execute("INSERT INTO users(name) VALUES($1)", "Test User")
    duration = time.time() - start_time
    print(f"Pure ORM: {QUERIES_NUM} insert queiries is completed in {duration} seconds.")

    await conn.execute("DELETE FROM users")
    print("Cleanup Ok")

    await conn.close()


if __name__ == "__main__":
    asyncio.run(run_benchmark())
