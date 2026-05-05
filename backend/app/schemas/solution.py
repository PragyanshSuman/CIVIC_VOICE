
import uuid
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class SolutionBase(BaseModel):
    title: str
    description: str

class SolutionCreate(SolutionBase):
    problem_id: uuid.UUID

class SolutionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class SolutionResponse(SolutionBase):
    id: uuid.UUID
    problem_id: uuid.UUID
    author_id: uuid.UUID
    
    # AI Scores
    ai_score_feasibility: float
    ai_score_impact: float
    ai_score_cost: float
    overall_score: float
    
    upvotes_count: int
    downvotes_count: int
    
    media_attachments: List['MediaAttachmentResponse'] = []
    
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

from app.schemas.media import MediaAttachmentResponse
