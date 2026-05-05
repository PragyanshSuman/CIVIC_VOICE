from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentResponse
from app.core.deps import get_current_active_user
from app.repositories.comment import CommentRepository
from uuid import UUID

router = APIRouter()

@router.get("/problem/{problem_id}", response_model=List[CommentResponse])
async def read_comments(
    problem_id: UUID,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get comments for a specific problem.
    """
    repo = CommentRepository(db)
    return await repo.get_by_problem(problem_id, skip=skip, limit=limit)

@router.post("/", response_model=CommentResponse)
async def create_comment(
    *,
    comment_in: CommentCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create new comment.
    """
    repo = CommentRepository(db)
    
    # Create comment
    comment_data = comment_in.model_dump()
    comment_data["user_id"] = current_user.id
    
    comment = await repo.create(comment_data)
    
    # Manually attach author for partial response optimization
    # (Avoids re-fetching the user we already have)
    comment.author = current_user
    
    # Notify Problem Author
    if comment_in.problem_id:
        from app.repositories.notification import NotificationRepository
        from app.models.problem import Problem
        from sqlalchemy import select
        
        # Verify problem exists and get author
        stmt = select(Problem).where(Problem.id == comment_in.problem_id)
        result = await db.execute(stmt)
        problem = result.scalar_one_or_none()
        
        if problem and problem.user_id != current_user.id:
            notif_repo = NotificationRepository(db)
            await notif_repo.create({
                "user_id": problem.user_id,
                "title": "New Comment on your Report",
                "message": f"{current_user.full_name} commented: {comment_in.content[:50]}...",
                "resource_id": str(problem.id),
                "resource_type": "problem"
            })

    return comment
