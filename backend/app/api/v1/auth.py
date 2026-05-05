

from typing import Any
from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.common import Token
from app.services.auth_service import AuthService


router = APIRouter()

@router.post("/login", response_model=Token)
async def login_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    # Rate limiting is handled by RateLimitMiddleware globally
    auth_service = AuthService(db)
    user = await auth_service.authenticate_user(form_data)
    return auth_service.create_token(user)

