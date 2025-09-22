import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # MongoDB Configuration
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "mental_health_chatbot"
    
    # Gemini API Configuration
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-1.5-flash"
    
    # Application Settings
    DEBUG: bool = False
    SECRET_KEY: str = "your-secret-key-here"
    
    # Agent Configuration
    MAX_CONVERSATION_HISTORY: int = 50
    DEFAULT_LANGUAGE: str = "English"
    
    # Crisis Helpline Configuration
    CRISIS_HELPLINE_INDIA: str = "+91-9152987821"
    CRISIS_HELPLINE_US: str = "988"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
