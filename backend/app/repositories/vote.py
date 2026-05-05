from sqlalchemy import select, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.vote import Vote, VoteType
from app.repositories.base import BaseRepository
from uuid import UUID
from typing import Optional

class VoteRepository(BaseRepository[Vote]):
    def __init__(self, db: AsyncSession):
        super().__init__(Vote, db)

    async def get_user_vote(self, user_id: UUID, solution_id: UUID) -> Optional[Vote]:
        stmt = select(Vote).where(
            and_(
                Vote.user_id == user_id,
                Vote.solution_id == solution_id
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_vote(self, vote_id: UUID):
        stmt = delete(Vote).where(Vote.id == vote_id)
        await self.db.execute(stmt)
