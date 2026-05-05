import uuid
from sqlalchemy import String, ForeignKey, DateTime, Enum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime
import enum

class ChatCategory(str, enum.Enum):
    ESTIMATE = "ESTIMATE"
    SITE_ACCESS = "SITE_ACCESS"
    MATERIAL_DELAY = "MATERIAL_DELAY"
    GENERAL = "GENERAL"
    URGENT = "URGENT"

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    work_order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("work_orders.id"), nullable=False)
    sender_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    message: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[ChatCategory] = mapped_column(Enum(ChatCategory), default=ChatCategory.GENERAL)
    
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    
    created_at: Mapped[datetime] = mapped_column(default=func.now())

    # Relationships
    work_order = relationship("WorkOrder")
    sender = relationship("User")

