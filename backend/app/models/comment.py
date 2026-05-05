
import uuid
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.database import Base

class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    
    # Polymorphic-like association (nullable FKs)
    # A comment can belong to a problem OR a solution
    problem_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("problems.id"), nullable=True)
    solution_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("solutions.id"), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())

    author = relationship("User", back_populates="comments")
    problem = relationship("Problem", back_populates="comments")
    solution = relationship("Solution", back_populates="comments")

