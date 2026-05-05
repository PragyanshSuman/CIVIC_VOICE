import uuid
from sqlalchemy import String, Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.database import Base

class UserRole(str, enum.Enum):
    CITIZEN = "CITIZEN"
    GOVERNMENT = "GOVERNMENT"
    ADMIN = "ADMIN"

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.CITIZEN)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Gamification
    karma_points: Mapped[int] = mapped_column(default=0)
    level: Mapped[int] = mapped_column(default=1)
    
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())

    # Relationships
    problems = relationship("Problem", back_populates="author", cascade="all, delete-orphan")
    solutions = relationship("Solution", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author")
    votes = relationship("Vote", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    verifications = relationship("Verification", back_populates="user", cascade="all, delete-orphan")
    
    # GovOS Relationship
    official_profile = relationship("Official", back_populates="user", uselist=False, cascade="all, delete-orphan")

