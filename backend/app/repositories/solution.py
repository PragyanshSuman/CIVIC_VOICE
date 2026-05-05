from typing import List, Optional, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.solution import Solution
from app.repositories.base import BaseRepository
from uuid import UUID

from sqlalchemy.orm import selectinload

class SolutionRepository(BaseRepository[Solution]):
    """
    Solution-specific repository operations.
    """
    def __init__(self, db: AsyncSession):
        super().__init__(Solution, db)

    async def get(self, id: UUID) -> Optional[Solution]:
        stmt = select(Solution).options(selectinload(Solution.media_attachments)).where(Solution.id == id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, obj_in: dict) -> Solution:
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        await self.db.commit()
        # Refresh with relationship
        return await self.get(db_obj.id)

    async def update(self, db_obj: Solution, obj_in: dict | Any) -> Solution:
        await super().update(db_obj, obj_in)
        # Re-fetch with relationship
        return await self.get(db_obj.id)

    async def get_by_problem_id(self, problem_id: UUID) -> List[Solution]:
        """
        Get all solutions for a specific problem, ordered by overall score (descending).
        """
        stmt = select(Solution)\
            .options(selectinload(Solution.media_attachments))\
            .where(Solution.problem_id == problem_id)\
            .order_by(Solution.overall_score.desc())
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
