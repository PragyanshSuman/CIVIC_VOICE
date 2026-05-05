from typing import List
from pydantic.v1 import BaseSettings, AnyHttpUrl, validator

class Settings(BaseSettings):
    """
    Application Settings
    
    All configuration is loaded from environment variables or .env file.
    """
    PROJECT_NAME: str = "Civic Collaboration Platform"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
    # Security
    SECRET_KEY: str = "YOUR_SUPER_SECRET_KEY_CHANGE_IN_PRODUCTION"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    MYSQL_SERVER: str = "localhost"
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "password"
    MYSQL_DB: str = "civic_platform"
    MYSQL_PORT: str = "3306"
    
    # Async Database URL
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_SERVER}:{self.MYSQL_PORT}/{self.MYSQL_DB}"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000", 
        "http://localhost:8000", 
        "http://127.0.0.1:3000", 
        "http://127.0.0.1:8000",
        "http://192.168.0.9:3000",
        "http://192.168.0.10:3000"
    ]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # AI Configuration
    USE_OPENAI: bool = False
    OPENAI_API_KEY: str | None = None
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 5242880  # 5MB in bytes
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/jpg"]

    class Config:
        case_sensitive = True
        env_file = ".env"
        # env_file_encoding = 'utf-8'

settings = Settings()
