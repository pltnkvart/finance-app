from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "FinTrack API"
    VERSION: str = "0.1.0"
    
    # Database
    DATABASE_URL: str
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str
    
    # Application
    SECRET_KEY: str
    ENVIRONMENT: str = "development"
    
    # Categorization
    MIN_TRAINING_SAMPLES: int = 3
    SIMILARITY_THRESHOLD: float = 0.7
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
