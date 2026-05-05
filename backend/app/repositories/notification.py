from app.repositories.base import BaseRepository
from app.models.notification import Notification
from sqlalchemy import select, update

class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, db):
        super().__init__(Notification, db)

    async def get_by_user(self, user_id, skip=0, limit=20):
        stmt = select(Notification)\
            .where(Notification.user_id == user_id)\
            .order_by(Notification.created_at.desc())\
            .offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def mark_as_read(self, notification_id):
        stmt = update(Notification)\
            .where(Notification.id == notification_id)\
            .values(is_read=True)
        await self.db.execute(stmt)
        await self.db.commit()
