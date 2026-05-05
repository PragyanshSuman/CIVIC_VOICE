import uuid
from sqlalchemy import String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    action: Mapped[str] = mapped_column(String(255), index=True)  # e.g., "CREATE", "UPDATE", "DELETE", "LOGIN"
    resource_type: Mapped[str] = mapped_column(String(255), index=True) # e.g., "PROBLEM", "SOLUTION", "USER"
    resource_id: Mapped[str] = mapped_column(String(255), nullable=True) # ID of the affected resource (can be string representation)
    actor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=True)
    
    ip_address: Mapped[str] = mapped_column(String(255), nullable=True)
    user_agent: Mapped[str] = mapped_column(String(255), nullable=True)
    details: Mapped[dict] = mapped_column(JSON, nullable=True) # Store before/after state or specific changes
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    actor = relationship("User")


