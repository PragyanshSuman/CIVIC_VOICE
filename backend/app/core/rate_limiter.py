from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
import time
from fastapi.responses import JSONResponse
from app.core.exceptions import CivicPlatformException

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, limit: int = 100, window: int = 60):
        super().__init__(app)
        self.limit = limit
        self.window = window
        self.requests = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Filter out requests older than the window
        self.requests[client_ip] = [t for t in self.requests[client_ip] if current_time - t < self.window]
        
        if len(self.requests[client_ip]) >= self.limit:
             return JSONResponse(
                status_code=429,
                content={
                    "status": "error",
                    "message": "Too many requests. Please try again later."
                }
            )
            
        self.requests[client_ip].append(current_time)
        response = await call_next(request)
        return response
