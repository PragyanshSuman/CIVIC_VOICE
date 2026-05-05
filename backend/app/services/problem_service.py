from app.repositories.problem import ProblemRepository
from app.repositories.government_response import GovernmentResponseRepository
from app.schemas.problem import ProblemCreate, ProblemUpdate
from app.schemas.government_response import GovernmentResponseCreate
from app.models.problem import Problem, ProblemStatus
from app.models.government_response import GovernmentResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Any
from uuid import UUID

class ProblemService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ProblemRepository(db)
        self.response_repo = GovernmentResponseRepository(db)

    async def create_problem(self, problem_in: ProblemCreate, user_id: UUID) -> Problem:
        """
        Create a new problem report.
        """
        problem_data = problem_in.model_dump()
        problem_data["author_id"] = user_id
        # In a real app, we might validate coordinates via GeolocationService here
        return await self.repo.create(problem_data)

    async def get_problem(self, problem_id: UUID) -> Optional[Problem]:
        return await self.repo.get(problem_id)

    async def get_all_problems(self, skip: int = 0, limit: int = 100) -> List[Problem]:
        return await self.repo.get_all(skip=skip, limit=limit)
        
    async def update_problem(self, problem_id: UUID, problem_in: ProblemUpdate) -> Optional[Problem]:
        problem = await self.repo.get(problem_id)
        if not problem:
            return None
        return await self.repo.update(problem, problem_in)

    async def respond_to_problem(self, problem_id: UUID, user_id: UUID, response_in: GovernmentResponseCreate) -> GovernmentResponse:
        """
        Add an official government response to a problem.
        Uses the Admin Seat (Official) logic for footprinting.
        """
        from app.models.official import Official
        from sqlalchemy import select

        # 1. Verify problem exists
        problem = await self.repo.get(problem_id)
        if not problem:
            raise Exception("Problem not found")
        
        # 2. Get the Official Seat for this User
        stmt = select(Official).where(Official.user_id == user_id)
        res = await self.db.execute(stmt)
        official = res.scalar_one_or_none()
        
        # 3. Create response with signature snapshot
        response_data = response_in.model_dump()
        response_data["official_id"] = user_id 
        
        if official:
            response_data["signed_by_name"] = official.current_occupant_name or official.designation or "Acting Officer"
        else:
            response_data["signed_by_name"] = "Acting Officer"
        
        new_status = response_data.pop("new_status", None)
        response = await self.response_repo.create(response_data)
        
        # 4. Update problem status
        if new_status:
            await self.repo.update(problem, {"status": new_status})
        elif problem.status == ProblemStatus.REPORTED:
            # Auto-triage if it was just reported
            await self.repo.update(problem, {"status": ProblemStatus.TRIAGED})
            
        return response

    async def get_government_responses(self, problem_id: UUID) -> List[GovernmentResponse]:
        return await self.response_repo.get_by_problem_id(problem_id)

    async def vote(self, user_id: UUID, problem_id: UUID, vote_type: Any) -> Problem:
        from app.models.vote import Vote, VoteType
        from sqlalchemy import select, delete
        
        # 1. Check if problem exists
        problem = await self.repo.get(problem_id)
        if not problem:
            raise Exception("Problem not found")
            
        # 2. Check if user already voted
        stmt = select(Vote).where(Vote.user_id == user_id, Vote.problem_id == problem_id)
        res = await self.db.execute(stmt)
        existing_vote = res.scalar_one_or_none()
        
        if existing_vote:
            if existing_vote.vote_type == vote_type:
                # Remove vote if clicking same button (toggle)
                await self.db.delete(existing_vote)
            else:
                # Change vote type
                existing_vote.vote_type = vote_type
        else:
            # Create new vote
            new_vote = Vote(
                user_id=user_id,
                problem_id=problem_id,
                vote_type=vote_type
            )
            self.db.add(new_vote)
            
            # Award XP for engaging
            try:
                from app.services.gamification_service import GamificationService
                game_service = GamificationService(self.db)
                await game_service.award_xp(user_id, "VOTE")
            except:
                pass # Gamification optional
                
        await self.db.commit()
        await self.db.refresh(problem)
        return problem

