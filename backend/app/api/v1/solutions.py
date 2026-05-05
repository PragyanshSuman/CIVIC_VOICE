from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import uuid

from app.database import get_db
from app.schemas.solution import SolutionCreate, SolutionResponse
from app.services.solution_service import SolutionService
from app.core import deps
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=SolutionResponse)
async def create_solution(
    *,
    solution_in: SolutionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
    background_tasks: BackgroundTasks
) -> Any:
    """
    Propose a new solution.
    AI Analysis runs in the background.
    """
    service = SolutionService(db)
    solution = await service.create_solution(solution_in, current_user.id)
    
    # Schedule AI scoring in background
    background_tasks.add_task(service.process_ai_scoring, solution.id)
    
    return solution

@router.get("/problem/{problem_id}", response_model=List[SolutionResponse])
async def read_solutions(
    problem_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get solutions for a specific problem.
    """
    service = SolutionService(db)
    return await service.get_solutions_for_problem(problem_id)

@router.post("/{solution_id}/vote", response_model=SolutionResponse)
async def vote_solution(
    solution_id: uuid.UUID,
    vote_type: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Vote for a solution (upvote/downvote).
    """
    from app.models.vote import VoteType
    try:
        v_type = VoteType(vote_type.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid vote type. Use 'upvote' or 'downvote'.")
        
    service = SolutionService(db)
    try:
        solution = await service.vote(current_user.id, solution_id, v_type)
        
        # Gamification: Award XP
        try:
            from app.services.gamification_service import GamificationService
            game_service = GamificationService(db)
            await game_service.award_xp(current_user.id, "VOTE")
        except Exception as e:
            print(f"Gamification Error: {e}")
            
        return solution
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/top", response_model=List[SolutionResponse])
async def read_top_solutions(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_official),
) -> Any:
    """
    Retrieve top-ranked solutions by AI impact score. Official access only.
    """
    service = SolutionService(db)
    from sqlalchemy import select
    from app.models.solution import Solution
    
    query = select(Solution).options(selectinload(Solution.media_attachments)).order_by(Solution.overall_score.desc()).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()
