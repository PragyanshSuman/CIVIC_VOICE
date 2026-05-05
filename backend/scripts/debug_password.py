import asyncio
import sys
import os
from sqlalchemy import select

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from app.models.user import User
from app.core.security import verify_password, get_password_hash

async def check_password():
    async with AsyncSessionLocal() as db:
        stmt = select(User).where(User.email == "admin@civic.com")
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user:
            print(f"User: {user.email}")
            print(f"Stored Hash: {user.hashed_password}")
            
            test_pass = "Admin123"
            is_valid = verify_password(test_pass, user.hashed_password)
            print(f"Is 'Admin123' valid? {is_valid}")
            
            if not is_valid:
                print("--- Diagnostics ---")
                new_hash = get_password_hash(test_pass)
                print(f"New Hash of '{test_pass}': {new_hash}")
                print(f"Verify New Hash: {verify_password(test_pass, new_hash)}")
                
        else:
            print("User not found")

if __name__ == "__main__":
    asyncio.run(check_password())
