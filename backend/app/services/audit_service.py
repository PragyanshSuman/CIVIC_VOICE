from app.repositories.audit_repository import AuditRepository
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

class AuditService:
    def __init__(self, db: AsyncSession):
        self.repo = AuditRepository(db)

    async def log_event(self, action: str, resource: str, resource_id: str, actor_id: str, request_info: dict = None):
        """
        Log an event to the audit table.
        """
        ip = request_info.get("ip") if request_info else None
        ua = request_info.get("user_agent") if request_info else None
        
        await self.repo.log_action(
            action=action,
            resource_type=resource,
            resource_id=resource_id,
            actor_id=actor_id,
            ip_address=ip,
            user_agent=ua,
            details=request_info
        )
