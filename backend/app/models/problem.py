
import uuid
from sqlalchemy import String, Text, Float, ForeignKey, Enum, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.database import Base

class ProblemStatus(str, enum.Enum):
    REPORTED = "REPORTED"
    TRIAGED = "TRIAGED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class Problem(Base):
    __tablename__ = "problems"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    status: Mapped[ProblemStatus] = mapped_column(Enum(ProblemStatus), default=ProblemStatus.REPORTED)
    
    # Geolocation
    latitude: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    address: Mapped[str] = mapped_column(String(255), nullable=True)
    
    image_url: Mapped[str] = mapped_column(String(255), nullable=True)
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())

    # Relationships
    # GovOS Fields
    department_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("departments.id"), nullable=True)
    jurisdiction_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jurisdictions.id"), nullable=True)
    assigned_official_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("officials.id"), nullable=True)
    
    workflow_state: Mapped[str] = mapped_column(String(255), default="REPORTED", nullable=True)
    escalation_level: Mapped[int] = mapped_column(Integer, default=0)
    sla_due_at: Mapped[datetime] = mapped_column(nullable=True)

    # Relationships
    author = relationship("User", back_populates="problems", lazy="selectin")
    solutions = relationship("Solution", back_populates="problem", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="problem", lazy="selectin")
    government_responses = relationship("GovernmentResponse", back_populates="problem")
    media_attachments = relationship("MediaAttachment", back_populates="problem", cascade="all, delete-orphan", lazy="selectin")
    verifications = relationship("Verification", back_populates="problem", cascade="all, delete-orphan")
    votes = relationship("Vote", back_populates="problem", cascade="all, delete-orphan", lazy="selectin")
    
    # GovOS Relationships
    department = relationship("Department", back_populates="problems")
    jurisdiction = relationship("Jurisdiction", back_populates="problems")
    assigned_official = relationship("Official", back_populates="assigned_problems")
    
    @property
    def upvotes_count(self) -> int:
        from app.models.vote import VoteType
        return sum(1 for v in self.votes if v.vote_type == VoteType.UPVOTE)
        
    @property
    def downvotes_count(self) -> int:
        from app.models.vote import VoteType
        return sum(1 for v in self.votes if v.vote_type == VoteType.DOWNVOTE)

