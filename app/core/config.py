from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    API_VERSION: str = "v1"
    PROJECT_NAME: str = "AI Personal Guide"
    DEBUG: bool = True
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "https://yourfrontend.com"]
    
    # Gemini AI settings
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    
    # Tavily API settings
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
    
    # # Database settings if needed
    # DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()