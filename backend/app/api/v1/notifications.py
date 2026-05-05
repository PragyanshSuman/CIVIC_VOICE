from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.schemas.notification import NotificationResponse
from app.core.deps import get_current_active_user
from app.repositories.notification import NotificationRepository
from uuid import UUID

router = APIRouter()

@router.get("/", response_model=List[NotificationResponse])
async def read_notifications(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get current user's notifications.
    """
    repo = NotificationRepository(db)
    return await repo.get_by_user(current_user.id, skip=skip, limit=limit)

@router.post("/{notification_id}/read", response_model=Any)
async def mark_notification_read(
    notification_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Mark a notification as read.
    """
    repo = NotificationRepository(db)
    await repo.mark_as_read(notification_id)
    return {"status": "success"}
