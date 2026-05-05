
from fastapi import APIRouter
from app.api.v1 import auth, users, problems, solutions, comments

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(problems.router, prefix="/problems", tags=["problems"])
api_router.include_router(solutions.router, prefix="/solutions", tags=["solutions"])
api_router.include_router(comments.router, prefix="/comments", tags=["comments"])
from app.api.v1 import notifications, media
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(media.router, prefix="/media", tags=["media"])


from app.api.v1 import departments, jurisdictions
api_router.include_router(departments.router, prefix="/departments", tags=["departments"])
api_router.include_router(jurisdictions.router, prefix="/jurisdictions", tags=["jurisdictions"])


from app.api.v1 import officials
api_router.include_router(officials.router, prefix="/officials", tags=["officials"])
