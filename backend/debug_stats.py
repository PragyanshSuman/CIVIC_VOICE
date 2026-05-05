import asyncio
import sys
import os
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.repositories.user import UserRepository
from app.api.v1.problems import read_user_problems
from app.models.user import User

async def debug():
    async with AsyncSessionLocal() as db:
        # Get a test user
        user_result = await db.execute(select(User).limit(1))
        user = user_result.scalar_one_or_none()
        
        if not user:
            print("No user found")
            return
            
        print(f"Testing stats for: {user.full_name} ({user.id})")
        
        # Test 1: Get Stats
        repo = UserRepository(db)
        stats = await repo.get_impact_stats(user.id)
        print("\n--- Impact Stats ---")
        print(stats)
        
        # Test 2: Get History (simulating API call logic)
        from app.repositories.problem import ProblemRepository
        prob_repo = ProblemRepository(db)
        problems = await prob_repo.get_by_user(user.id)
        
        print(f"\n--- History ({len(problems)} items) ---")
        for p in problems[:3]:
            print(f"- {p.title} ({p.status})")

if __name__ == "__main__":
    sys.path.append(os.getcwd())
    asyncio.run(debug())
