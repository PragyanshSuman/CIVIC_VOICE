import shutil
from pathlib import Path
from typing import Any
from fastapi import APIRouter, UploadFile, File, HTTPException
import uuid
from app.config import settings

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/", response_model=dict)
async def upload_file(
    file: UploadFile = File(...)
) -> dict[str, str]:
    """
    Upload a file to local storage.
    Returns the URL to access the file.
    """
    try:
        # Validate file type
        if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
             raise HTTPException(status_code=400, detail="Invalid file type")

        # Generate unique filename
        file_ext = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_ext}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Save file asynchronously
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
            
        # Return local URL (in prod this would be S3 URL)
        # We assume the app serves /static/ points to uploads/
        return {"url": f"/static/{unique_filename}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not upload file: {str(e)}")
