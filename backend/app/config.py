from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    MONGODB_URL: str = ""
    DATABASE_NAME: str = "recruiter_assist"
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production-12345"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Application
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Recruiter Assist"
    VERSION: str = "1.0.0"
    
    # AI/LLM
    MISTRAL_API_KEY: str = ""
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # This ignores extra fields in .env

settings = Settings()