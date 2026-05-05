from app.repositories.base import BaseRepository
from app.models.audit_log import AuditLog
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

class AuditRepository(BaseRepository[AuditLog]):
    def __init__(self, db: AsyncSession):
        super().__init__(AuditLog, db)

    async def log_action(
        self,
        action: str,
        resource_type: str,
        resource_id: str,
        actor_id: str,
        ip_address: str = None,
        user_agent: str = None,
        details: dict = None
    ) -> AuditLog:
        """
        Create a new audit log entry.
        """
        log_entry = AuditLog(
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id),
            actor_id=str(actor_id) if actor_id else None,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details
        )
        self.db.add(log_entry)
        await self.db.commit()
        await self.db.refresh(log_entry)
        return log_entry
