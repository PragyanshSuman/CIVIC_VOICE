from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.department import Department
from app.models.user import User
from app.core.deps import get_current_user
from pydantic import BaseModel
import uuid

router = APIRouter()

# Schemas
class DepartmentCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None
    sla_config: Optional[dict] = {}
    workflow_config: Optional[dict] = {}
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    wikidata_id: Optional[str] = None

class DepartmentRead(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    parent_id: Optional[uuid.UUID]
    sla_config: dict
    workflow_config: dict
    logo_url: Optional[str]
    website_url: Optional[str]
    wikidata_id: Optional[str]
    
    class Config:
        from_attributes = True

# Endpoints
@router.post("/", response_model=DepartmentRead)
async def create_department(
    dept_in: DepartmentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Only Admin can create departments (TODO: Proper RBAC)
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
        
    # Check uniqueness
    existing_code = await db.scalar(select(Department).where(Department.code == dept_in.code))
    if existing_code:
        raise HTTPException(status_code=400, detail="Department code already exists")
        
    db_dept = Department(**dept_in.dict())
    db.add(db_dept)
    await db.commit()
    await db.refresh(db_dept)
    return db_dept

@router.get("/", response_model=List[DepartmentRead])
async def list_departments(
    skip: int = 0, 
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Department).offset(skip).limit(limit))
    return result.scalars().all()
