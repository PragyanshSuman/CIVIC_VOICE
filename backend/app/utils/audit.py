from fastapi import BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.services.audit_service import AuditService
from app.models.user import User

async def log_audit_background(
    action: str, 
    resource_type: str, 
    resource_id: str, 
    actor_id: str, 
    ip: str, 
    ua: str
):
    """
    Background task to write audit log without blocking the response.
    """
    async with AsyncSessionLocal() as db:
        service = AuditService(db)
        await service.log_event(
            action=action,
            resource=resource_type,
            resource_id=resource_id,
            actor_id=actor_id,
            request_info={"ip": ip, "user_agent": ua}
        )

def audit_log(
    background_tasks: BackgroundTasks,
    request: Request,
    user: User,
    action: str,
    resource_type: str,
    resource_id: str
):
    """
    Helper to schedule an audit log.
    """
    background_tasks.add_task(
        log_audit_background,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id),
        actor_id=str(user.id),
        ip=request.client.host,
        ua=request.headers.get("user-agent")
    )
