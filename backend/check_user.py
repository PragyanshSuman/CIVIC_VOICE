import asyncio
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.user import User

async def check_user():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == "city.infra@contractor.com"))
        user = result.scalar_one_or_none()
        if user:
            print(f"User found: {user.email}, Role: {user.role}, ID: {user.id}")
        else:
            print("User NOT found")

if __name__ == "__main__":
    asyncio.run(check_user())
