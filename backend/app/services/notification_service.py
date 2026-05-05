from app.models.notification import Notification
from app.repositories.base import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

class NotificationService:
    def __init__(self, db: AsyncSession):
        self.repo = BaseRepository(Notification, db)

    async def create_notification(self, user_id: UUID, title: str, message: str) -> Notification:
        data = {
            "user_id": user_id,
            "title": title,
            "message": message,
            "is_read": False
        }
        return await self.repo.create(data)

    async def get_user_notifications(self, user_id: UUID):
        # This would require a custom query in repository, simplified here
        return []
