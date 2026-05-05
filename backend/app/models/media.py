import uuid
from sqlalchemy import String, ForeignKey, Enum, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.database import Base

class MediaType(str, enum.Enum):
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"

class MediaAttachment(Base):
    __tablename__ = "media_attachments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    file_url: Mapped[str] = mapped_column(String(255), nullable=False)
    media_type: Mapped[MediaType] = mapped_column(Enum(MediaType), default=MediaType.IMAGE)
    
    # Legitimacy Metadata
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    is_verified_capture: Mapped[bool] = mapped_column(Boolean, default=False)
    device_info: Mapped[str] = mapped_column(String(255), nullable=True)
    
    # Foreign Keys
    problem_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("problems.id"), nullable=True)
    solution_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("solutions.id"), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    
    # Relationships
    problem = relationship("Problem", back_populates="media_attachments")
    solution = relationship("Solution", back_populates="media_attachments")

