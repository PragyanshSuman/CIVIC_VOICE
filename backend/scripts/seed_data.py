"""
Seed script to populate the database with sample civic problems and solutions
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.models.problem import Problem, ProblemStatus
from app.models.solution import Solution
from app.core.security import get_password_hash
import uuid
from datetime import datetime

async def seed_database():
    """Populate database with sample data"""
    async with AsyncSessionLocal() as session:
        print("Starting database seeding...")
        
        # Clear existing data for a clean seed
        from sqlalchemy import delete
        from app.models.government_response import GovernmentResponse
        from app.models.vote import Vote
        from app.models.comment import Comment
        
        # Delete in order of dependencies
        await session.execute(delete(GovernmentResponse))
        await session.execute(delete(Vote))
        await session.execute(delete(Comment))
        await session.execute(delete(Solution))
        await session.execute(delete(Problem))
        await session.commit()
        print("Cleared existing problems and solutions.")
        
        # Get the first user (the one who just signed up)
        result = await session.execute(select(User).limit(1))
        user = result.scalar_one_or_none()
        
        if not user:
            print("No users found. Please sign up first.")
            return
        
        print(f"Found user: {user.email}")
        
        # Sample problems with realistic civic issues
        sample_problems = [
            {
                "title": "Pothole on Main Street",
                "description": "Large pothole causing traffic issues and potential vehicle damage near the intersection of Main St and 5th Ave.",
                "category": "Infrastructure",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "address": "Main St & 5th Ave, New York, NY",
                "status": ProblemStatus.OPEN
            },
            {
                "title": "Broken Street Light",
                "description": "Street light has been out for 2 weeks, making the area unsafe at night.",
                "category": "Public Safety",
                "latitude": 40.7580,
                "longitude": -73.9855,
                "address": "Times Square, New York, NY",
                "status": ProblemStatus.UNDER_REVIEW
            },
            {
                "title": "Illegal Dumping in Park",
                "description": "Construction waste dumped in Central Park near the north entrance.",
                "category": "Environment",
                "latitude": 40.7829,
                "longitude": -73.9654,
                "address": "Central Park North, New York, NY",
                "status": ProblemStatus.OPEN
            },
            {
                "title": "Graffiti on Public Building",
                "description": "Vandalism on the exterior walls of the community center.",
                "category": "Vandalism",
                "latitude": 40.7489,
                "longitude": -73.9680,
                "address": "Community Center, Queens, NY",
                "status": ProblemStatus.OPEN
            },
            {
                "title": "Noise Pollution from Construction",
                "description": "Construction site operating beyond permitted hours, disturbing residents.",
                "category": "Noise",
                "latitude": 40.7614,
                "longitude": -73.9776,
                "address": "Midtown Manhattan, NY",
                "status": ProblemStatus.SOLVED
            }
        ]
        
        print(f"Creating {len(sample_problems)} sample problems...")
        
        created_problems = []
        for problem_data in sample_problems:
            problem = Problem(
                id=uuid.uuid4(),
                title=problem_data["title"],
                description=problem_data["description"],
                category=problem_data["category"],
                latitude=problem_data["latitude"],
                longitude=problem_data["longitude"],
                address=problem_data.get("address"),
                status=problem_data["status"],
                user_id=user.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(problem)
            created_problems.append(problem)
        
        await session.commit()
        print(f"Created {len(created_problems)} problems")
        
        # Create sample solutions for some problems
        print("Creating sample solutions...")
        
        sample_solutions = [
            {
                "problem": created_problems[0],  # Pothole
                "title": "Quick Asphalt Patch",
                "description": "Use cold-mix asphalt for immediate repair, followed by permanent hot-mix repair within 2 weeks."
            },
            {
                "problem": created_problems[1],  # Street Light
                "title": "LED Replacement",
                "description": "Replace with energy-efficient LED bulb and inspect electrical connection."
            },
            {
                "problem": created_problems[2],  # Illegal Dumping
                "title": "Community Cleanup Event",
                "description": "Organize volunteer cleanup event and install surveillance cameras to prevent future dumping."
            }
        ]
        
        for solution_data in sample_solutions:
            solution = Solution(
                id=uuid.uuid4(),
                title=solution_data["title"],
                description=solution_data["description"],
                problem_id=solution_data["problem"].id,
                author_id=user.id,
                created_at=datetime.utcnow()
            )
            session.add(solution)
        
        await session.commit()

        
        # Create official responses for some problems
        from app.models.government_response import GovernmentResponse
        from app.models.vote import Vote, VoteType
        from app.models.user import UserRole
        
        # Get the official user
        official = (await session.execute(select(User).filter(User.role == UserRole.GOVERNMENT))).scalars().first()
        citizen = (await session.execute(select(User).filter(User.role == UserRole.CITIZEN))).scalars().first()
        
        if official and created_problems:
            resp = GovernmentResponse(
                problem_id=created_problems[0].id,
                official_id=official.id,
                response_text="Verified: Engineering teams have been dispatched to evaluate the structural integrity and prioritize repairs within the next 48 hours.",
                action_plan="1. Site analysis (Completed)\n2. Material procurement (In Progress)\n3. Evening deployment scheduled"
            )
            session.add(resp)
            created_problems[0].status = ProblemStatus.UNDER_REVIEW

        await session.commit()
        print("Database transformed with official responses and community stats!")

if __name__ == "__main__":
    asyncio.run(seed_database())



