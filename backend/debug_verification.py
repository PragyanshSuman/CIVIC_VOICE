
import asyncio
import uuid
from app.database import AsyncSessionLocal
from app.models.user import User
from app.models.problem import Problem
from app.models.verification import Verification
from sqlalchemy import select

async def debug_verification():
    async with AsyncSessionLocal() as db:
        print("--- Debugging Crowd Verification ---")
        
        # 1. Get a User and a Problem
        user = await db.scalar(select(User).limit(1))
        problem = await db.scalar(select(Problem).limit(1))
        
        if not user or not problem:
            print("Error: Need user and problem.")
            return

        print(f"User: {user.full_name}")
        print(f"Problem: {problem.title}")
        print(f"Current Karma: {user.karma_points}")

        # 2. Clear existing verification
        existing = await db.scalar(select(Verification).where(
            Verification.user_id == user.id,
            Verification.problem_id == problem.id
        ))
        if existing:
            await db.delete(existing)
            await db.commit()
            print("Cleared existing verification.")

        # 3. Simulate Verify (via Service logic embedded here for test)
        # In real app, we use the API, but let's just insert directly to test model/relationships
        # and maybe manually trigger XP for test
        
        new_ver = Verification(
            user_id=user.id,
            problem_id=problem.id,
            confirms_issue=True
        )
        db.add(new_ver)
        
        # Award XP manually to test DB update
        user.karma_points += 20
        await db.commit()
        await db.refresh(user)
        
        print("Verification submitted.")
        print(f"New Karma: {user.karma_points} (+20)")
        
        # 4. cleanup
        await db.delete(new_ver)
        # Revert karma for cleanliness? Nah, keep the rewards :D
        # Actually user.karma_points -= 20
        user.karma_points -= 20
        await db.commit()
        print("Cleaned up verification and points.")

if __name__ == "__main__":
    asyncio.run(debug_verification())
