import asyncio
import sys
import os

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import configure_mappers
configure_mappers()

import app.models
from app.database import AsyncSessionLocal
from app.models.official import Official
from app.models.user import User
from app.models.problem import Problem
from sqlalchemy import select

async def check_data():
    async with AsyncSessionLocal() as db:
        print("🔍 Checking Database Content...")
        
        # Check Officials
        stmt = select(Official)
        result = await db.execute(stmt)
        officials = result.scalars().all()
        print(f"Number of Officials: {len(officials)}")
        for o in officials:
            print(f" - Official ID: {o.id}, UserID: {o.user_id}, DeptID: {o.department_id}")

        # Check Users
        stmt = select(User).where(User.email == "official@gov.in")
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            print(f"Official User: {user.email}, Role: {user.role}, ID: {user.id}")
        else:
            print("Official User NOT FOUND")

        # Check Problems
        stmt = select(Problem)
        result = await db.execute(stmt)
        problems = result.scalars().all()
        print(f"Number of Problems: {len(problems)}")
        for p in problems:
            print(f" - [{p.status}] {p.title} (Assigned: {p.assigned_official_id})")

if __name__ == "__main__":
    asyncio.run(check_data())
