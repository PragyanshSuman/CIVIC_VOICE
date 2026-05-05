import asyncio
import sys
import os

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from sqlalchemy import select

async def create_test_user():
    async with AsyncSessionLocal() as session:
        # Check if user exists
        result = await session.execute(select(User).filter(User.email == "test@example.com"))
        user = result.scalar_one_or_none()
        
        if user:
            print(f"User test@example.com already exists. ID: {user.id}")
            return
            
        print("Creating test user...")
        new_user = User(
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
            full_name="Test Citizen",
            role=UserRole.CITIZEN,
            is_active=True
        )
        session.add(new_user)
        await session.commit()
        print(f"User created! Email: test@example.com, Password: password123")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(create_test_user())
