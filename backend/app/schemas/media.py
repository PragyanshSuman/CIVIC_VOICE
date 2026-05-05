import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.media import MediaType

class MediaAttachmentCreate(BaseModel):
    file_url: str
    media_type: MediaType
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_verified_capture: bool = False
    device_info: Optional[str] = None

class MediaAttachmentResponse(BaseModel):
    id: uuid.UUID
    file_url: str
    media_type: MediaType
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_verified_capture: bool = False
    device_info: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
