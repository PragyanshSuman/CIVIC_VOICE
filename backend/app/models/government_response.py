
import uuid
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.database import Base

class GovernmentResponse(Base):
    __tablename__ = "government_responses"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    problem_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("problems.id"))
    official_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id")) # link to the official who responded
    
    response_text: Mapped[str] = mapped_column(Text, nullable=False)
    action_plan: Mapped[str] = mapped_column(Text, nullable=True)
    signed_by_name: Mapped[str] = mapped_column(String(255), nullable=True) # Snapshot of occupant name at time of response
    
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())

    problem = relationship("Problem", back_populates="government_responses")
    official = relationship("User") # We don't necessarily need a backref on User for this unless needed

