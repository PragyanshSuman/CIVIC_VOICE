import uuid
from sqlalchemy import String, Enum, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum

class JurisdictionType(str, enum.Enum):
    COUNTRY = "COUNTRY"
    STATE = "STATE"
    DISTRICT = "DISTRICT"
    CITY = "CITY"
    ZONE = "ZONE"
    WARD = "WARD"

class Jurisdiction(Base):
    __tablename__ = "jurisdictions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False) # e.g. "Ward 12"
    type: Mapped[JurisdictionType] = mapped_column(Enum(JurisdictionType), nullable=False)
    
    # Hierarchy
    parent_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jurisdictions.id"), nullable=True)
    
    # Geo-Spatial Data
    # Storing as JSON for now (e.g., GeoJSON Polygon). 
    # In a real PostGIS setup, this would be Geometry type.
    boundary_polygon: Mapped[dict] = mapped_column(JSON, nullable=True) 

    # Relationships
    parent = relationship("Jurisdiction", remote_side=[id], backref="sub_jurisdictions")
    officials = relationship("Official", back_populates="jurisdiction")
    problems = relationship("Problem", back_populates="jurisdiction")

