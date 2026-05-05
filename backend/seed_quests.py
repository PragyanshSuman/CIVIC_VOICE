
import asyncio
import sys
import os

# Set up path to allow importing app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from app.models.quest import Quest
from sqlalchemy import select

async def seed_quests():
    async with AsyncSessionLocal() as db:
        print("Checking existing quests...")
        result = await db.execute(select(Quest))
        if result.scalars().first():
            print("Quests already exist. Skipping.")
            return

        print("Seeding default quests...")
        quests = [
            Quest(
                title="Weekend Warrior",
                description="Fix 2 issues in your neighborhood this weekend.",
                xp_reward=100,
                action_type="FIX_ISSUE",
                target_count=2
            ),
            Quest(
                title="Truth Seeker",
                description="Verify 5 reported issues to keep the map clean.",
                xp_reward=50,
                action_type="VERIFY",
                target_count=5
            ),
            Quest(
                title="Social Butterfly",
                description="Join a Neighborhood Hub.",
                xp_reward=25,
                action_type="JOIN_COMMUNITY",
                target_count=1
            )
        ]
        
        db.add_all(quests)
        await db.commit()
        print("✅ Quests seeded successfully!")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(seed_quests())
