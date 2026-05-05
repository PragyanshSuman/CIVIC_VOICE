
import uuid
import enum
from sqlalchemy import ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.database import Base

class VoteType(str, enum.Enum):
    UPVOTE = "UPVOTE"
    DOWNVOTE = "DOWNVOTE"

class Vote(Base):
    __tablename__ = "votes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    solution_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("solutions.id"), nullable=True)
    problem_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("problems.id"), nullable=True)
    
    vote_type: Mapped[VoteType] = mapped_column(Enum(VoteType))
    created_at: Mapped[datetime] = mapped_column(default=func.now())

    user = relationship("User", back_populates="votes")
    solution = relationship("Solution", back_populates="votes")
    problem = relationship("Problem", back_populates="votes")

