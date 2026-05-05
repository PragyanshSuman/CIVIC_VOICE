from datetime import timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

from app.core import security
from app.config import settings
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserLogin
from app.models.user import User
from app.core.exceptions import AuthenticationError, DuplicateResourceError

class AuthService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)

    async def authenticate_user(self, login_data: OAuth2PasswordRequestForm) -> User:
        """
        Authenticate a user by email and password.
        Uses the UserRepository for data access.
        """
        user = await self.user_repo.get_by_email(login_data.username)
        if not user:
            raise AuthenticationError("Incorrect email or password")
        
        if not security.verify_password(login_data.password, user.hashed_password):
            raise AuthenticationError("Incorrect email or password")
            
        return user

    async def register_user(self, user_in: UserCreate) -> User:
        """
        Register a new user. 
        Checks for uniqueness and hashes password.
        """
        existing_user = await self.user_repo.get_by_email(user_in.email)
        if existing_user:
            raise DuplicateResourceError(resource="User", field="email")
            
        hashed_password = security.get_password_hash(user_in.password)
        
        # Create user dict but replace password with hash
        user_data = user_in.model_dump()
        user_data["hashed_password"] = hashed_password
        del user_data["password"]
        
        return await self.user_repo.create(user_data)
        
    def create_token(self, user: User) -> dict:
        """Create access token for user"""
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security.create_access_token(
            subject=str(user.id), expires_delta=access_token_expires
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": str(user.id),
            "role": user.role.value
        }
