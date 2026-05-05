from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.government_response import GovernmentResponse
from app.repositories.base import BaseRepository
from uuid import UUID

class GovernmentResponseRepository(BaseRepository[GovernmentResponse]):
    def __init__(self, db: AsyncSession):
        super().__init__(GovernmentResponse, db)

    async def get_by_problem_id(self, problem_id: UUID) -> List[GovernmentResponse]:
        stmt = select(GovernmentResponse).where(GovernmentResponse.problem_id == problem_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()
