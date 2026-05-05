import asyncio
from app.database import engine
from sqlalchemy import text

async def check():
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text('SHOW TABLES'))
            tables = result.fetchall()
            if not tables:
                print("Connected, but NO TABLES found. Please run migrations.")
            else:
                print(f"Success! Found {len(tables)} tables: {[t[0] for t in tables]}")
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    asyncio.run(check())
