
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.core import deps
from app.database import get_db
from app.models.problem import Problem, ProblemStatus
from app.models.solution import Solution
from app.models.user import User, UserRole
from app.models.vote import Vote
from app.models.media import MediaAttachment, MediaType
from app.schemas.problem import ProblemCreate, ProblemUpdate, ProblemResponse, ProblemStats
from sqlalchemy import func

from sqlalchemy.orm import selectinload

router = APIRouter()

@router.get("/", response_model=List[ProblemResponse])
async def read_problems(
    skip: int = 0,
    limit: int = 100,
    status: ProblemStatus = None,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Retrieve problems. Filter by status optionally.
    """
    query = select(Problem).options(
        selectinload(Problem.media_attachments),
        selectinload(Problem.author)
    )
    if status:
        query = query.where(Problem.status == status)
        
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    problems = result.scalars().all()
    return problems


@router.get("/stats", response_model=ProblemStats)
async def read_problem_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_official),
) -> Any:
    """
    Retrieve city-wide civic statistics. Official access only.
    """
    # Active Reports
    active_count = await db.scalar(select(func.count(Problem.id)).where(Problem.status != ProblemStatus.RESOLVED))
    
    # Resolved Issues
    resolved_count = await db.scalar(select(func.count(Problem.id)).where(Problem.status == ProblemStatus.RESOLVED))
    
    # Total Engagement (Sum of upvotes across all solutions)
    total_upvotes = await db.scalar(select(func.sum(Solution.upvotes_count))) or 0
    
    # Average AI Impact Score
    avg_impact = await db.scalar(select(func.avg(Solution.overall_score))) or 0.0
    
    return {
        "active_reports": active_count,
        "resolved_issues": resolved_count,
        "total_engagement": total_upvotes,
        "city_satisfaction": round(avg_impact * 10, 1) # Scale to 10
    }

@router.post("/", response_model=ProblemResponse)
async def create_problem(
    problem_in: ProblemCreate,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create new problem.
    """
    problem_data = problem_in.model_dump(exclude={"media_urls", "media_attachments"})
    db_problem = Problem(
        **problem_data,
        user_id=current_user.id
    )
    
    # Phase 2: AI Smart Routing
    try:
        from app.ai.smart_router import SmartRouter
        router = SmartRouter(db)
        dept, jurisdiction = await router.route_problem(db_problem)
        
        if dept:
            db_problem.department_id = dept.id
            
        if jurisdiction:
            db_problem.jurisdiction_id = jurisdiction.id
            
    except Exception as e:
        print(f"AI Routing Error: {e}")

    db.add(db_problem)
    await db.flush() # Generate ID
    
    # Handle enriched media attachments (Verification Logic)
    if problem_in.media_attachments:
        for m_in in problem_in.media_attachments:
            media = MediaAttachment(
                **m_in.model_dump(),
                problem_id=db_problem.id
            )
            db.add(media)
    
    # Fallback for legacy media_urls
    elif problem_in.media_urls:
        for url in problem_in.media_urls:
            # Simple extension check (expand as needed)
            m_type = MediaType.VIDEO if url.lower().endswith(('.mp4', '.mov', '.avi')) else MediaType.IMAGE
            media = MediaAttachment(
                file_url=url,
                media_type=m_type,
                problem_id=db_problem.id
            )
            db.add(media)
            
    await db.commit()
    
    # Reload with eager relationships
    stmt = select(Problem).options(
        selectinload(Problem.media_attachments),
        selectinload(Problem.author)
    ).where(Problem.id == db_problem.id)
    result = await db.execute(stmt)
    db_problem = result.scalar_one()
    
    # Gamification: Award XP
    try:
        from app.services.gamification_service import GamificationService
        game_service = GamificationService(db)
        await game_service.award_xp(current_user.id, "REPORT")
    except Exception as e:
        print(f"Gamification Error: {e}")

    return db_problem

    return db_problem

from app.repositories.problem import ProblemRepository

@router.get("/user/{user_id}", response_model=List[ProblemResponse])
async def read_user_problems(
    user_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get problems submitted by a specific user.
    """
    repo = ProblemRepository(db)
    return await repo.get_by_user(user_id, skip=skip, limit=limit)

@router.get("/{problem_id}", response_model=ProblemResponse)
async def read_problem(
    problem_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get problem by ID.
    """
    stmt = select(Problem).options(
        selectinload(Problem.media_attachments),
        selectinload(Problem.author)
    ).where(Problem.id == problem_id)
    result = await db.execute(stmt)
    problem = result.scalar_one_or_none()
    
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem

@router.put("/{problem_id}", response_model=ProblemResponse)
async def update_problem(
    problem_id: uuid.UUID,
    problem_in: ProblemUpdate,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Update a problem. Only author or admin can update.
    """
    from app.services.problem_service import ProblemService
    service = ProblemService(db)
    problem = await service.get_problem(problem_id)
    
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
        
    # Permission Check
    # DEBUG LOGGING for 403 issues
    user_role_val = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    user_role_val = user_role_val.upper()
    
    is_admin = user_role_val in [UserRole.ADMIN.value, UserRole.GOVERNMENT.value, "ADMIN", "GOVERNMENT"]
    is_author = str(problem.user_id) == str(current_user.id)
    
    print(f"--- PERMISSION CHECK ---")
    print(f"User ID: {current_user.id}")
    print(f"User Role: {user_role_val}")
    print(f"Is Admin/Gov: {is_admin}")
    print(f"Is Author: {is_author}")
    
    if not (is_author or is_admin):
        raise HTTPException(status_code=403, detail=f"Not enough permissions. Your role: {user_role_val}")

    # Manual Triage & Auto-Assignment Logic
    update_data = problem_in.model_dump(exclude_unset=True)
    
    if is_admin:
        if problem_in.department_id:
            problem.department_id = problem_in.department_id
        if problem_in.jurisdiction_id:
            problem.jurisdiction_id = problem_in.jurisdiction_id
            
        # AUTO-CONNECTION: If an official starts working, assign them automatically
        if update_data.get("status") == ProblemStatus.IN_PROGRESS:
            # Try to find official profile for this user
            from app.models.official import Official
            stmt = select(Official).where(Official.user_id == current_user.id)
            res = await db.execute(stmt)
            official = res.scalar_one_or_none()
            if official:
                problem.assigned_official_id = official.id
                # Ensure the field is in the update data so repo tracks it if needed
                update_data["assigned_official_id"] = official.id

    return await service.update_problem(problem_id, update_data)

@router.post("/{problem_id}/vote", response_model=ProblemResponse)
async def vote_problem(
    problem_id: uuid.UUID,
    vote_type: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Vote for a problem report (upvote/downvote).
    """
    from app.models.vote import VoteType
    try:
        v_type = VoteType(vote_type.upper())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid vote type. Use 'UPVOTE' or 'DOWNVOTE'.")
        
    try:
        from app.services.problem_service import ProblemService
        service = ProblemService(db)
        return await service.vote(current_user.id, problem_id, v_type)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

from app.schemas.government_response import GovernmentResponseCreate, GovernmentResponseResponse

@router.post("/{problem_id}/respond", response_model=GovernmentResponseResponse)
async def respond_to_problem(
    problem_id: uuid.UUID,
    response_in: GovernmentResponseCreate,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Official government response to a problem.
    """
    if current_user.role not in [UserRole.GOVERNMENT, UserRole.ADMIN]:
        raise HTTPException(
            status_code=403, 
            detail="Only government officials or admins can respond officially"
        )
    
    from app.services.problem_service import ProblemService
    service = ProblemService(db)
    try:
        return await service.respond_to_problem(problem_id, current_user.id, response_in)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{problem_id}/responses", response_model=List[GovernmentResponseResponse])
async def read_government_responses(
    problem_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get all official responses for a problem.
    """
    from app.services.problem_service import ProblemService
    service = ProblemService(db)
    service = ProblemService(db)
    return await service.get_government_responses(problem_id)



# Citizen Resolution Verification API

from app.models.verification import Verification
from app.services.gamification_service import GamificationService

@router.post("/{problem_id}/verify-resolution", response_model=dict)
async def verify_problem_resolution(
    problem_id: uuid.UUID,
    is_resolved: bool,
    comment: str = None,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Citizen verifies if an issue is actually fixed by the government.
    Closes the issue if verified.
    """
    problem = await db.get(Problem, problem_id)
    if not problem:
         raise HTTPException(status_code=404, detail="Problem not found")
    
    if problem.user_id != current_user.id:
         raise HTTPException(status_code=403, detail="Only the original reporter can verify resolution")
         
    if problem.status != ProblemStatus.RESOLVED:
         raise HTTPException(status_code=400, detail="Problem is not in RESOLVED state yet")

    # Check if already verified
    stmt = select(Verification).where(
        Verification.problem_id == problem_id,
        Verification.user_id == current_user.id
    )
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing:
        existing.is_resolved = is_resolved
        existing.comment = comment
    else:
        new_verification = Verification(
            problem_id=problem_id, 
            user_id=current_user.id,
            is_resolved=is_resolved,
            comment=comment
        )
        db.add(new_verification)
        
    if is_resolved:
        problem.status = ProblemStatus.CLOSED
        problem.workflow_state = "CLOSED"
    else:
        problem.status = ProblemStatus.IN_PROGRESS
        problem.workflow_state = "IN_PROGRESS"
        
    # Award XP
    gamification = GamificationService(db)
    await gamification.award_xp(current_user.id, "VERIFY")
    
    await db.commit()
    
    state_msg = "Issue Closed." if is_resolved else "Issue returned to In Progress."
    return {"message": f"Verification submitted! {state_msg}", "points_awarded": 20}
