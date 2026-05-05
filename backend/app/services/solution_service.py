from app.repositories.solution import SolutionRepository
from app.repositories.vote import VoteRepository
from app.schemas.solution import SolutionCreate
from app.models.solution import Solution
from app.models.vote import Vote, VoteType
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from app.ai.pipeline import AIPipeline

class SolutionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = SolutionRepository(db)
        self.vote_repo = VoteRepository(db)
        # Initialize AI Pipeline (singleton ideal in prod)
        self.ai = AIPipeline() 

    async def create_solution(self, solution_in: SolutionCreate, user_id: UUID) -> Solution:
        """
        Create a solution without blocking for AI.
        """
        solution_data = solution_in.model_dump()
        solution_data["author_id"] = user_id
        
        # 1. Save initial solution
        solution = await self.repo.create(solution_data)
        return solution
        
    async def process_ai_scoring(self, solution_id: UUID):
        """
        Background task: Trigger AI Analysis and update record.
        """
        from app.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as db:
            repo = SolutionRepository(db)
            solution = await repo.get(solution_id)
            if not solution:
                return

            # Analyze
            scores = self.ai.analyze_single_solution(solution.title, solution.description)
            
            # Update
            update_data = {
                "ai_score_feasibility": scores["feasibility"],
                "ai_score_impact": scores["impact"],
                "ai_score_cost": scores["cost"],
                "overall_score": scores["overall"]
            }
            await repo.update(solution, update_data)

    async def get_solutions_for_problem(self, problem_id: UUID) -> List[Solution]:
        return await self.repo.get_by_problem_id(problem_id)

    async def vote(self, user_id: UUID, solution_id: UUID, vote_type: VoteType) -> Solution:
        """
        Vote for a solution. Toggles existing same-type votes, updates counts.
        """
        solution = await self.repo.get(solution_id)
        if not solution:
            raise Exception("Solution not found")

        existing_vote = await self.vote_repo.get_user_vote(user_id, solution_id)
        
        up_change = 0
        down_change = 0

        if existing_vote:
            if existing_vote.vote_type == vote_type:
                # Remove vote (toggle)
                await self.vote_repo.delete_vote(existing_vote.id)
                if vote_type == VoteType.UPVOTE:
                    up_change = -1
                else:
                    down_change = -1
            else:
                # Change vote type
                existing_vote.vote_type = vote_type
                if vote_type == VoteType.UPVOTE:
                    up_change = 1
                    down_change = -1
                else:
                    up_change = -1
                    down_change = 1
        else:
            # Create new vote
            await self.vote_repo.create({
                "user_id": user_id,
                "solution_id": solution_id,
                "vote_type": vote_type
            })
            if vote_type == VoteType.UPVOTE:
                up_change = 1
            else:
                down_change = 1

        # Update solution counts
        update_data = {
            "upvotes_count": solution.upvotes_count + up_change,
            "downvotes_count": solution.downvotes_count + down_change
        }
        await self.repo.update(solution, update_data)
        return solution

