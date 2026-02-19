from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Pydantic Settings, which automatically overrides your hardcoded values with environment variables when they exist.
    # MongoDB Configuration
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "hrms_lite_db"
    
    # Gemini AI Configuration
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-flash-lite-latest"
    
    # API Configuration
    API_V1_PREFIX: str = "/api"
    PROJECT_NAME: str = "HRMS Lite"
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
