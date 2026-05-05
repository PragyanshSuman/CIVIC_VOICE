import asyncio
from sqlalchemy import text
from app.database import engine

async def check_role():
    try:
        async with engine.connect() as conn:
            # Check column type
            res = await conn.execute(text("SELECT column_name, data_type, udt_name FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'role'"))
            info = res.fetchone()
            print(f"Column Info: {info}")
            
            # Check enum labels
            res = await conn.execute(text("SELECT enumlabel FROM pg_enum JOIN pg_type ON pg_enum.enumtypid = pg_type.oid WHERE pg_type.typname = 'userrole'"))
            labels = res.fetchall()
            print(f"Enum Labels: {labels}")
            
            # Check values
            res = await conn.execute(text("SELECT role FROM users LIMIT 5"))
            values = res.fetchall()
            print(f"Values: {values}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_role())
