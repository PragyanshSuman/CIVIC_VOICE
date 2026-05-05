from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.jurisdiction import Jurisdiction, JurisdictionType
from app.models.user import User
from app.core.deps import get_current_user
from pydantic import BaseModel
import uuid

router = APIRouter()

# Schemas
class JurisdictionCreate(BaseModel):
    name: str
    type: JurisdictionType
    parent_id: Optional[uuid.UUID] = None
    boundary_polygon: Optional[dict] = None

class JurisdictionRead(BaseModel):
    id: uuid.UUID
    name: str
    type: JurisdictionType
    parent_id: Optional[uuid.UUID]
    boundary_polygon: Optional[dict]

    class Config:
        from_attributes = True

# Endpoints
@router.post("/", response_model=JurisdictionRead)
async def create_jurisdiction(
    juris_in: JurisdictionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
        
    db_juris = Jurisdiction(**juris_in.dict())
    db.add(db_juris)
    await db.commit()
    await db.refresh(db_juris)
    return db_juris

@router.get("/", response_model=List[JurisdictionRead])
async def list_jurisdictions(
    type: Optional[JurisdictionType] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Jurisdiction)
    if type:
        query = query.where(Jurisdiction.type == type)
    result = await db.execute(query)
    return result.scalars().all()

@router.put("/{juris_id}", response_model=JurisdictionRead)
async def update_jurisdiction(
    juris_id: uuid.UUID,
    juris_in: JurisdictionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
        
    db_juris = await db.get(Jurisdiction, juris_id)
    if not db_juris:
        raise HTTPException(status_code=404, detail="Jurisdiction not found")
        
    for var, value in juris_in.dict(exclude_unset=True).items():
        setattr(db_juris, var, value)
        
    await db.commit()
    await db.refresh(db_juris)
    return db_juris

@router.delete("/{juris_id}")
async def delete_jurisdiction(
    juris_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
        
    db_juris = await db.get(Jurisdiction, juris_id)
    if not db_juris:
        raise HTTPException(status_code=404, detail="Jurisdiction not found")
        
    await db.delete(db_juris)
    await db.commit()
    return {"status": "success"}
