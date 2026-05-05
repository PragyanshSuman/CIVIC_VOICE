import asyncio
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash

async def create_contractor():
    async with AsyncSessionLocal() as session:
        # Check if user exists
        stmt = select(User).where(User.email == "city.infra@contractor.com")
        result = await session.execute(stmt)
        if result.scalar_one_or_none():
            print("User already exists.")
            return

        print("Creating contractor user...")
        c_user = User(
            email="city.infra@contractor.com",
            hashed_password=get_password_hash("Contractor123"),
            full_name="City Infra Solutions",
            role=UserRole.CONTRACTOR,
            is_active=True
        )
        session.add(c_user)
        try:
            await session.commit()
            print("Contractor user created successfully!")
        except Exception as e:
            print(f"Error creating user: {e}")
            with open("error_log.txt", "w") as f:
                f.write(str(e))
            await session.rollback()

if __name__ == "__main__":
    asyncio.run(create_contractor())
