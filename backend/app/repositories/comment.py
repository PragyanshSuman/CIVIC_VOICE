from app.repositories.base import BaseRepository
from app.models.comment import Comment
from sqlalchemy import select
from sqlalchemy.orm import selectinload

class CommentRepository(BaseRepository[Comment]):
    def __init__(self, db):
        super().__init__(Comment, db)

    async def get_by_problem(self, problem_id, skip=0, limit=50):
        stmt = select(Comment)\
            .where(Comment.problem_id == problem_id)\
            .options(selectinload(Comment.author))\
            .order_by(Comment.created_at.asc())\
            .offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()
