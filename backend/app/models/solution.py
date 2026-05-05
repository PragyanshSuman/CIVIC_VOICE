
import uuid
from sqlalchemy import String, Text, ForeignKey, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.database import Base

class Solution(Base):
    __tablename__ = "solutions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    problem_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("problems.id"))
    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    
    # AI Scoring Fields (cached for quick access)
    ai_score_feasibility: Mapped[float] = mapped_column(Float, default=0.0)
    ai_score_impact: Mapped[float] = mapped_column(Float, default=0.0)
    ai_score_cost: Mapped[float] = mapped_column(Float, default=0.0)
    overall_score: Mapped[float] = mapped_column(Float, default=0.0)
    
    upvotes_count: Mapped[int] = mapped_column(Integer, default=0)
    downvotes_count: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())

    # Relationships
    problem = relationship("Problem", back_populates="solutions")
    author = relationship("User", back_populates="solutions")
    votes = relationship("Vote", back_populates="solution", cascade="all, delete-orphan")
    media_attachments = relationship("MediaAttachment", back_populates="solution", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="solution")

