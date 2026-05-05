import asyncio
import sys
import os
from sqlalchemy import select

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from app.models.user import User

async def check_admin():
    async with AsyncSessionLocal() as db:
        stmt = select(User).where(User.email == "admin@civic.com")
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user:
            print(f"✅ FOUND Admin User: {user.email}")
            print(f"   Role: {user.role}")
            print(f"   Active: {user.is_active}")
            print(f"   Hashed Password: {user.hashed_password[:10]}...")
        else:
            print("❌ Admin user NOT found in database.")

if __name__ == "__main__":
    asyncio.run(check_admin())
