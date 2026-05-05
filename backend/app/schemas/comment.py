from pydantic import BaseModel, UUID4, ConfigDict
from datetime import datetime
from typing import Optional
from app.schemas.user import UserResponse

class CommentBase(BaseModel):
    content: str
    problem_id: Optional[UUID4] = None
    solution_id: Optional[UUID4] = None

class CommentCreate(CommentBase):
    pass

class CommentResponse(CommentBase):
    id: UUID4
    user_id: UUID4
    created_at: datetime
    author: Optional[UserResponse] = None

    model_config = ConfigDict(from_attributes=True)
