import asyncio
import asyncpg
import time

QUERUES_NUM = 3000

async def prepare_data(conn):
    for _ in range(QUERUES_NUM):
        await conn.execute('INSERT INTO users(name) VALUES($1)', 'Test User')

async def run_benchmark():
    conn = await asyncpg.connect(user='postgres', password='postgres', database='postgres', host='localhost')
    
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id serial PRIMARY KEY,
            name text
        )
    ''')

    await prepare_data(conn)

    start_time = time.time()
    await conn.fetch('SELECT * FROM users')
    duration = time.time() - start_time
    print(f"Pure ORM: {QUERUES_NUM} select queries is completed in {duration} seconds .")

    await conn.execute('DELETE FROM users')

    await conn.close()

if __name__ == "__main__":
    asyncio.run(run_benchmark())

