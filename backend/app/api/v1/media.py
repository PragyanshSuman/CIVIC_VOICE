from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List
import shutil
import os
import uuid
from app.core import deps
from app.models.user import User
from app.config import settings

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=List[str])
async def upload_files(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Upload multiple files (images/videos) and return their URLs.
    """
    uploaded_urls = []
    
    for file in files:
        # Generate unique filename
        file_extension = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Save file locally
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Could not save file: {str(e)}")
            
        # Construct URL (assumes server is mounted at /static or similar, or just returns relative path)
        # We'll return the full URL based on the API_STR or a new STATIC_URL setting.
        # For now, simplistic approach: /static/filename
        file_url = f"/static/{unique_filename}"
        uploaded_urls.append(file_url)
        
    return uploaded_urls
