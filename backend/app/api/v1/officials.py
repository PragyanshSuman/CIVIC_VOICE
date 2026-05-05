from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.official import Official, OfficialRole
from app.models.user import User
from app.core.deps import get_current_user, get_current_active_admin, get_current_active_official
from app.services.ai_service import AIAnalyticsService
from pydantic import BaseModel, ConfigDict
import uuid

router = APIRouter()

# Schemas
class OfficialCreate(BaseModel):
    user_id: uuid.UUID
    department_id: uuid.UUID
    jurisdiction_id: uuid.UUID
    role: OfficialRole
    badge_number: str
    designation: str
    current_occupant_name: Optional[str] = None

class OfficialRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    department_id: uuid.UUID
    jurisdiction_id: uuid.UUID
    role: OfficialRole
    badge_number: str
    designation: str
    current_occupant_name: Optional[str] = None
    is_verified: bool
    
    # Nested info (optional, or separate fields)
    # We might want to return User name too
    
    class Config:
        from_attributes = True

# Endpoints

@router.post("/", response_model=OfficialRead)
async def create_official(
    official_in: OfficialCreate,
    current_user: User = Depends(get_current_active_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new official profile for an existing user.
    """
    # Check if user exists
    user = await db.get(User, official_in.user_id)
    if not user:
         raise HTTPException(status_code=404, detail="User not found")
         
    # Check if already official
    existing = await db.execute(select(Official).where(Official.user_id == official_in.user_id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User is already an official")

    db_official = Official(**official_in.dict())
    db.add(db_official)
    
    # Auto-promote user role to GOVERNMENT if not already
    current_role = str(user.role).upper()
    if current_role not in [UserRole.GOVERNMENT.value, UserRole.ADMIN.value]:
        user.role = UserRole.GOVERNMENT
        db.add(user) # Update user role
        
    await db.commit()
    await db.refresh(db_official)
    return db_official

@router.get("/", response_model=List[OfficialRead])
async def list_officials(
    department_id: Optional[uuid.UUID] = None,
    jurisdiction_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin)
):
    query = select(Official)
    if department_id:
        query = query.where(Official.department_id == department_id)
    if jurisdiction_id:
        query = query.where(Official.jurisdiction_id == jurisdiction_id)
        
    result = await db.execute(query)
    return result.scalars().all()

    await db.delete(official)
    await db.commit()
    return {"message": "Official removed"}

from app.schemas.problem import ProblemResponse
from app.models.problem import Problem, ProblemStatus

@router.get("/queue", response_model=List[ProblemResponse])
async def get_official_queue(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_official)
) -> Any:
    """
    Get problems assigned to the current official's department or jurisdiction.
    """
    # Get official profile
    stmt = select(Official).where(Official.user_id == current_user.id)
    result = await db.execute(stmt)
    official = result.scalar_one_or_none()
    
    if not official:
        # Fallback if user is GOV but has no official profile yet
        return []
    
    # Filter problems: 
    # 1. Assigned directly to them
    # 2. In their department AND jurisdiction
    query = select(Problem).options(
        selectinload(Problem.media_attachments),
        selectinload(Problem.author)
    ).where(
        (Problem.assigned_official_id == official.id) |
        (
            (Problem.department_id == official.department_id) & 
            (Problem.jurisdiction_id == official.jurisdiction_id) &
            (Problem.status != ProblemStatus.RESOLVED)
        )
    )
    
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/insights")
async def get_dashboard_insights(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_official)
):
    """
    Get AI-driven city insights based on priority scoring formula.
    """
    ai_service = AIAnalyticsService(db)
    return await ai_service.get_city_insights()

class OfficialTransfer(BaseModel):
    new_occupant_name: str
    new_password: str

@router.patch("/{official_id}/transfer", response_model=OfficialRead)
async def transfer_official_seat(
    official_id: uuid.UUID,
    data: OfficialTransfer,
    current_user: User = Depends(get_current_active_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Officially transfer an administrative seat to a new person.
    1. Updates the occupant name.
    2. Resets the login password (forced rotation).
    """
    official = await db.get(Official, official_id)
    if not official:
        raise HTTPException(status_code=404, detail="Official seat not found")
        
    # Update Occupant
    official.current_occupant_name = data.new_occupant_name
    
    # Secure Password Rotation for the seat's login
    user = await db.get(User, official.user_id)
    if user:
        from app.core.security import get_password_hash
        user.hashed_password = get_password_hash(data.new_password)
        db.add(user)
        
    db.add(official)
    await db.commit()
    await db.refresh(official)
    return official
