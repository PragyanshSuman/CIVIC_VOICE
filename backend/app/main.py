"""
Civic Collaboration Platform - Main Application Entry Point

This module initializes the FastAPI application with all necessary middleware,
exception handlers, and route configurations.
"""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.config import settings
from app.core.middleware import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
    request_logging_middleware
)
from app.utils.logger import logger

# Initialize FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-powered civic engagement platform transforming citizen problems into actionable solutions",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Exception Handlers
# Exception Handlers
# Import handler first (need to modify imports or pass it)
# For now, let's rely on valid imports.
from app.core.middleware import authentication_exception_handler
from app.core.exceptions import AuthenticationError

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(AuthenticationError, authentication_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Middleware - Order matters! CORS should be first
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

from fastapi.staticfiles import StaticFiles
from app.api.v1 import uploads

# Request logging middleware
app.middleware("http")(request_logging_middleware)

# Rate Limiting (100 reqs/min)
from app.core.rate_limiter import RateLimitMiddleware
app.add_middleware(RateLimitMiddleware, limit=100, window=60)

# Mount static files for local uploads
app.mount("/static", StaticFiles(directory="uploads"), name="static")

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(uploads.router, prefix=f"{settings.API_V1_STR}/uploads", tags=["uploads"])

@app.on_event("startup")
async def startup_event():
    """Execute on application startup"""
    logger.info(f"🚀 Starting {settings.PROJECT_NAME}")
    logger.info(f"📚 API Documentation available at /docs")
    logger.info(f"🔧 Environment: {'Development' if settings.DEBUG else 'Production'}")
    print("\n" + "="*50)
    print(f"✅ SERVER IS LISTENING ON 0.0.0.0:8000")
    print(f"👉 TRY CONNECTING FROM PHONE TO: http://192.168.0.10:8000/docs")
    print("="*50 + "\n")

@app.on_event("shutdown")
async def shutdown_event():
    """Execute on application shutdown"""
    logger.info(f"👋 Shutting down {settings.PROJECT_NAME}")

@app.get("/", tags=["Health"])
async def root():
    """
    Root endpoint - Health check
    
    Returns basic API information and status.
    """
    return {
        "status": "online",
        "message": "Welcome to the Civic Collaboration Platform API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring
    
    Returns the health status of the application.
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME
    }
