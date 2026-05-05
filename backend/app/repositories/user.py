from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.repositories.base import BaseRepository

class UserRepository(BaseRepository[User]):
    """
    User-specific repository operations.
    """
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email address."""
        statement = select(User).where(User.email == email)
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()
        
    async def get_impact_stats(self, user_id) -> dict:
        """Calculate impact statistics for a user."""
        from app.models.problem import Problem, ProblemStatus
        from sqlalchemy import func
        
        # Count submitted problems
        prob_count = await self.db.scalar(select(func.count(Problem.id)).where(Problem.user_id == user_id)) or 0
        
        # Count resolved problems (where user is author and status is Solved)
        # Note: In future, this could be "solutions offered by user", but for now we track "their problems fixed"
        resolved_count = await self.db.scalar(select(func.count(Problem.id)).where(Problem.user_id == user_id, Problem.status == ProblemStatus.RESOLVED)) or 0
        
        # Determine Rank
        karma = 0 # Need to fetch user karma, or pass user object. For now let's query user.
        user = await self.get(user_id)
        if user:
            karma = user.karma_points
            
        rank = "Citizen"
        if karma > 100: rank = "Scout"
        if karma > 500: rank = "Guardian"
        if karma > 1000: rank = "Hero"
            
        return {
            "reports_submitted": prob_count,
            "issues_resolved": resolved_count,
            "verification_score": 0.95, # Placeholder for Phase 7.3
            "impact_level": rank,
            "volunteered_count": 0 # Placeholder for Phase 7.2
        }
