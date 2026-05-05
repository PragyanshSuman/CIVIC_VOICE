
import asyncio
import uuid
from app.database import AsyncSessionLocal
from app.models.user import User
from app.models.problem import Problem, ProblemStatus
from app.models.action_squad import ActionSquad
from sqlalchemy import select

async def debug_squads():
    async with AsyncSessionLocal() as db:
        print("--- Debugging Action Squads ---")
        
        # 1. Get a User and a Problem
        user = await db.scalar(select(User).limit(1))
        problem = await db.scalar(select(Problem).limit(1))
        
        if not user or not problem:
            print("Error: Need at least one user and one problem.")
            return

        print(f"User: {user.full_name} ({user.id})")
        print(f"Problem: {problem.title} ({problem.id})")
        
        # 2. Clear existing squad membership for this pair
        existing = await db.scalar(select(ActionSquad).where(
            ActionSquad.user_id == user.id,
            ActionSquad.problem_id == problem.id
        ))
        if existing:
            await db.delete(existing)
            await db.commit()
            print("Cleared existing membership.")

        # 3. Join Squad (Manual Insert to simulate API logic, or just test relationship)
        # Testing relationship first
        new_entry = ActionSquad(user_id=user.id, problem_id=problem.id)
        db.add(new_entry)
        await db.commit()
        print("Joined squad.")
        
        # 4. Verify via Relationship
        await db.refresh(problem)
        # Note: loading relationships might need eager load options in real app, but here we can re-query
        squad_members = await db.scalars(select(User).join(ActionSquad).where(ActionSquad.problem_id == problem.id))
        members = squad_members.all()
        
        print(f"Squad Members Count: {len(members)}")
        found = any(u.id == user.id for u in members)
        print(f"User in Squad: {found}")
        
        if found:
            print("SUCCESS: User successfully added to squad.")
        else:
            print("FAILURE: User not found in squad.")

        # 5. Cleanup
        await db.delete(new_entry)
        await db.commit()
        print("Cleaned up.")

if __name__ == "__main__":
    asyncio.run(debug_squads())
