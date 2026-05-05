import uuid
from sqlalchemy import String, Enum, ForeignKey, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum

class OfficialRole(str, enum.Enum):
    FIELD_AGENT = "FIELD_AGENT"       # Can only update status
    SUPERVISOR = "SUPERVISOR"         # Can assign/approve estimates
    APPROVER = "APPROVER"             # Can release budget
    ANALYST = "ANALYST"               # Read-only analytics
    PRIME_ADMIN = "PRIME_ADMIN"       # God mode

class Official(Base):
    __tablename__ = "officials"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    
    # Link to the core User model (for Auth)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    
    # Governance Matrix (Where do they fit?)
    department_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("departments.id"), nullable=False)
    jurisdiction_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jurisdictions.id"), nullable=False)
    
    role: Mapped[OfficialRole] = mapped_column(Enum(OfficialRole), default=OfficialRole.FIELD_AGENT)
    designation: Mapped[str] = mapped_column(String(255), nullable=True) # e.g. "Junior Engineer"
    current_occupant_name: Mapped[str] = mapped_column(String(255), nullable=True) # The human currently "in the seat"
    badge_number: Mapped[str] = mapped_column(String(255), unique=True, nullable=True)
    
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="official_profile")
    department = relationship("Department", back_populates="officials")
    jurisdiction = relationship("Jurisdiction", back_populates="officials")
    
    # Work
    assigned_problems = relationship("Problem", back_populates="assigned_official", foreign_keys="Problem.assigned_official_id")

