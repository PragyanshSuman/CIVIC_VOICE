import uuid
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.problem import ProblemStatus

class GovernmentResponseBase(BaseModel):
    response_text: str
    action_plan: Optional[str] = None

class GovernmentResponseCreate(GovernmentResponseBase):
    problem_id: uuid.UUID
    signed_by_name: Optional[str] = None
    new_status: Optional[ProblemStatus] = None

class GovernmentResponseUpdate(BaseModel):
    response_text: Optional[str] = None
    action_plan: Optional[str] = None

class GovernmentResponseResponse(GovernmentResponseBase):
    id: uuid.UUID
    problem_id: uuid.UUID
    official_id: uuid.UUID
    signed_by_name: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
