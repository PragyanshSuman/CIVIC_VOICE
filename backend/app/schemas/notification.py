from pydantic import BaseModel, UUID4, ConfigDict
from datetime import datetime
from typing import Optional

class NotificationBase(BaseModel):
    title: str
    message: str
    resource_id: Optional[UUID4] = None
    resource_type: Optional[str] = None # "problem", "solution"

class NotificationCreate(NotificationBase):
    user_id: UUID4

class NotificationResponse(NotificationBase):
    id: UUID4
    user_id: UUID4
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
