
import uuid
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.models.problem import ProblemStatus

# Shared properties
class ProblemBase(BaseModel):
    title: str
    description: str
    category: str
    latitude: float
    longitude: float
    address: Optional[str] = None
    image_url: Optional[str] = None

from app.schemas.media import MediaAttachmentCreate, MediaAttachmentResponse

class ProblemCreate(ProblemBase):
    media_attachments: Optional[List[MediaAttachmentCreate]] = []
    # For backward compatibility during migration
    media_urls: Optional[List[str]] = []

class ProblemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    status: Optional[ProblemStatus] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    image_url: Optional[str] = None
    media_attachments: Optional[List[MediaAttachmentCreate]] = None
    media_urls: Optional[List[str]] = None
    # Manual Triage Fields
    department_id: Optional[uuid.UUID] = None
    jurisdiction_id: Optional[uuid.UUID] = None

from app.schemas.media import MediaAttachmentResponse
from app.schemas.user import UserResponse

class ProblemResponse(ProblemBase):
    id: uuid.UUID
    status: ProblemStatus
    user_id: uuid.UUID
    author: Optional[UserResponse] = None
    media_attachments: List[MediaAttachmentResponse] = []
    upvotes_count: int = 0
    downvotes_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ProblemStats(BaseModel):
    active_reports: int
    resolved_issues: int
    total_engagement: int
    city_satisfaction: float
