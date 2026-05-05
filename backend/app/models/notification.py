
import uuid
from sqlalchemy import String, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.database import Base

class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(String(255), nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Navigation Support
    resource_id: Mapped[str] = mapped_column(String(255), nullable=True) # ID of Problem/Solution
    resource_type: Mapped[str] = mapped_column(String(255), nullable=True) # "problem", "solution"

    created_at: Mapped[datetime] = mapped_column(default=func.now())

    user = relationship("User", back_populates="notifications")

