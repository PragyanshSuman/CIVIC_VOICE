from pydantic import BaseModel

class UserImpactStats(BaseModel):
    reports_submitted: int = 0
    issues_resolved: int = 0
    verification_score: float = 0.0 # 0.0 to 1.0
    impact_level: str = "Newcomer" # Newcomer, Scout, Guardian, Hero
    volunteered_count: int = 0
