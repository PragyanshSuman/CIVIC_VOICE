from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.repositories.user import UserRepository
import math

class GamificationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = UserRepository(db)

    async def award_xp(self, user_id, action_type: str):
        """
        Awards XP to a user and handles level ups.
        Action Types:
        - REPORT: +50
        - VOTE: +1
        - VERIFY: +20
        """
        points_map = {
            "REPORT": 50,
            "VOTE": 1,
            "VERIFY": 20
        }
        
        points = points_map.get(action_type, 0)
        if points == 0:
            return

        user = await self.repo.get(user_id)
        if not user:
            return

        # Add points
        user.karma_points += points
        
        # Check Level Up (Level = sqrt(points) / 5)
        # Example: 100 pts -> sqrt(100)/5 = 2.
        # 2500 pts -> sqrt(2500)/5 = 10.
        new_level = math.floor(math.sqrt(user.karma_points) / 5)
        if new_level < 1: 
            new_level = 1
            
        if new_level > user.level:
            user.level = new_level
            # TODO: Add notification or badge event here
            
        await self.db.commit()
        await self.db.refresh(user)
        return user
