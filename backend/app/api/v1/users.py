from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.core.deps import get_current_active_user, get_current_active_admin
from app.services.auth_service import AuthService

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.get("/leaderboard", response_model=List[UserResponse])
async def get_leaderboard(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get top users by karma points.
    """
    stmt = select(User).order_by(User.karma_points.desc()).limit(limit)
    result = await db.execute(stmt)
    users = result.scalars().all()
    users = result.scalars().all()
    return users

from app.schemas.stats import UserImpactStats
from app.repositories.user import UserRepository
import uuid

@router.get("/{user_id}/stats", response_model=UserImpactStats)
async def read_user_stats(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get gamified impact stats for a user (Public Profile).
    """
    repo = UserRepository(db)
    return await repo.get_impact_stats(user_id)

@router.get("/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get public user profile by ID.
    """
    repo = UserRepository(db)
    user = await repo.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/signup", response_model=UserResponse)
async def create_user(
    *,
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create new user.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Signup attempt for email: {user_in.email}")
        auth_service = AuthService(db)
        # The service handles uniqueness check and password hashing
        user = await auth_service.register_user(user_in)
        logger.info(f"User created successfully: {user.email}")
        return user
    except Exception as e:
        logger.error(f"Signup error: {type(e).__name__}: {str(e)}")
        logger.exception("Full traceback:")
        raise


@router.get("/", response_model=List[UserResponse])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_admin),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Retrieve users. Only for admins.
    """
    stmt = select(User).offset(skip).limit(limit)
    result = await db.execute(stmt)
    users = result.scalars().all()
    return users
