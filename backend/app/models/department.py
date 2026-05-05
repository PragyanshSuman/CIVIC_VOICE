import uuid
from sqlalchemy import String, Boolean, Enum, JSON, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum

class Department(Base):
    __tablename__ = "departments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    code: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False) # e.g. "PWD-MH"
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    logo_url: Mapped[str] = mapped_column(String(255), nullable=True) # Official department logo
    website_url: Mapped[str] = mapped_column(String(255), nullable=True) # Official government link
    wikidata_id: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=True) # Cross-reference ID
    
    # Hierarchy
    parent_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("departments.id"), nullable=True)
    
    # Configuration (The "Brain" of the Department)
    sla_config: Mapped[dict] = mapped_column(JSON, default={}) 
    # e.g., {"pothole": {"hours": 48, "priority": "HIGH"}}
    
    workflow_config: Mapped[dict] = mapped_column(JSON, default={})
    # e.g., {"default": ["OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"]}

    # Budgeting (Civic ERP)
    budget_allocated: Mapped[float] = mapped_column(default=0.0)
    budget_utilized: Mapped[float] = mapped_column(default=0.0)

    # Relationships
    parent = relationship("Department", remote_side=[id], backref="sub_departments")
    officials = relationship("Official", back_populates="department")
    problems = relationship("Problem", back_populates="department")

