
import uuid
from sqlalchemy import ForeignKey, Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.database import Base

class Verification(Base):
    __tablename__ = "verifications"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    problem_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("problems.id"), index=True)
    
    # Did the citizen verify the problem is resolved?
    # True = Issue is fixed, close it.
    # False = Dispute, issue is not fixed.
    is_resolved: Mapped[bool] = mapped_column(Boolean, nullable=False)
    comment: Mapped[str] = mapped_column(String(255), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="verifications")
    problem = relationship("Problem", back_populates="verifications")

