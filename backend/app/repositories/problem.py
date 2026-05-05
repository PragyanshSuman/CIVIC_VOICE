from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.problem import Problem, ProblemStatus
from app.repositories.base import BaseRepository

from sqlalchemy.orm import selectinload

class ProblemRepository(BaseRepository[Problem]):
    """
    Problem-specific repository operations.
    """
    def __init__(self, db: AsyncSession):
        super().__init__(Problem, db)
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Problem]:
        """Get all problems with author and media data."""
        statement = select(Problem).options(
            selectinload(Problem.author),
            selectinload(Problem.media_attachments),
            selectinload(Problem.votes)
        ).order_by(Problem.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(statement)
        return result.scalars().all()

    async def get(self, id) -> Optional[Problem]:
        """Get problem by ID with details."""
        statement = select(Problem).options(
            selectinload(Problem.author),
            selectinload(Problem.media_attachments),
            selectinload(Problem.votes)
        ).where(Problem.id == id)
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()
    
    async def get_by_status(self, status: ProblemStatus, skip: int = 0, limit: int = 100) -> List[Problem]:
        """Get problems filtering by status."""
        statement = select(Problem).options(
            selectinload(Problem.author),
            selectinload(Problem.media_attachments),
            selectinload(Problem.votes)
        ).where(Problem.status == status).offset(skip).limit(limit)
        result = await self.db.execute(statement)
        return result.scalars().all()
    
    async def get_by_category(self, category: str, skip: int = 0, limit: int = 100) -> List[Problem]:
        """Get problems filtering by category."""
        statement = select(Problem).options(
            selectinload(Problem.author),
            selectinload(Problem.media_attachments),
            selectinload(Problem.votes)
        ).where(Problem.category == category).offset(skip).limit(limit)
        result = await self.db.execute(statement)
        return result.scalars().all()

    async def get_by_user(self, user_id, skip: int = 0, limit: int = 100) -> List[Problem]:
        """Get problems submitted by a specific user."""
        statement = select(Problem).options(
            selectinload(Problem.author),
            selectinload(Problem.media_attachments),
            selectinload(Problem.votes)
        ).where(Problem.user_id == user_id).order_by(Problem.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(statement)
        return result.scalars().all()
