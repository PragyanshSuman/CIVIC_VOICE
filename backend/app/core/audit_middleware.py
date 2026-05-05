from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.database import AsyncSessionLocal
from app.services.audit_service import AuditService
# from app.core.security import get_current_user_from_token # Broken import, not used in this file
# Note: Full auth info extraction in middleware is complex due to stream consumption.
# For government grade, we often use a dedicated Audit Decorator on specific routes instead of 
# a global middleware that might fail to parse bodies.
# However, for simplicity here, we will log "Request Received" events for critical paths.

class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Only audit state-changing methods
        if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            # We fire and forget the audit log to not slow down response? 
            # ideally, use background tasks.
            # implementing a true robust audit middleware requires reading the auth token manually
            pass 
            
        return response

# REVISION:
# Instead of a global middleware which is hard to get User ID from (since Auth happens effectively inside the route),
# We will create a dependency "Auditor" that routes can use.
