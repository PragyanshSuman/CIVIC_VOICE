import json
from typing import List, Optional, Tuple
from app.models.problem import Problem
from app.models.department import Department
from app.models.jurisdiction import Jurisdiction, JurisdictionType
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from shapely.geometry import shape, Point
import logging

logger = logging.getLogger(__name__)

class SmartRouter:
    """
    AI Service to route problems to the correct Department and Jurisdiction.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def predict_department(self, title: str, description: str) -> Optional[Department]:
        """
        Uses simple keyword matching (Phase 1 AI) to predict department.
        TODO: Upgrade to BERT/OpenAI embeddings in Phase 2.5
        """
        text = (title + " " + description).lower()
        
        # Fetch all departments
        result = await self.db.execute(select(Department))
        departments = result.scalars().all()
        
        best_match = None
        max_score = 0
        
        for dept in departments:
            # Simple keyword overlap score
            keywords = dept.name.lower().split()
            score = sum(1 for word in keywords if word in text)
            
            # Hardcoded heuristics for demo
            if "pothole" in text or "road" in text:
                if "road" in dept.name.lower() or "public works" in dept.name.lower():
                    score += 5
            if "garbage" in text or "waste" in text or "dump" in text:
                if "sanitation" in dept.name.lower() or "health" in dept.name.lower():
                    score += 5
            if "water" in text or "leak" in text or "pipe" in text:
                if "water" in dept.name.lower():
                    score += 5
            
            if score > max_score:
                max_score = score
                best_match = dept
                
        return best_match

    async def resolve_jurisdiction(self, lat: float, lng: float) -> Optional[Jurisdiction]:
        """
        Finds the smallest jurisdiction (WARD) that contains the point.
        Uses Ray Casting (Point in Polygon) algorithm.
        """
        # Fetch all Wards first (optimisation)
        result = await self.db.execute(
            select(Jurisdiction).where(Jurisdiction.type == JurisdictionType.WARD)
        )
        wards = result.scalars().all()
        
        point = Point(lng, lat)
        
        for ward in wards:
            if not ward.boundary_polygon:
                continue
                
            try:
                # Assuming boundary_polygon is GeoJSON dict
                polygon = shape(ward.boundary_polygon)
                if polygon.contains(point):
                    return ward
            except Exception as e:
                logger.error(f"Error parsing polygon for ward {ward.name}: {e}")
                continue
                
        # If no Ward found, try City/Zone (Fallback)
        # ... logic for fallback ...
        
        return None

    async def route_problem(self, problem: Problem) -> Tuple[Optional[Department], Optional[Jurisdiction]]:
        """
        Main entry point. Analyzes problem and returns routing info.
        """
        dept = await self.predict_department(problem.title, problem.description)
        jurisdiction = await self.resolve_jurisdiction(problem.latitude, problem.longitude)
        
        return dept, jurisdiction
