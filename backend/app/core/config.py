"""
Application configuration and settings.

Uses environment variables for configuration.
"""

from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    
    # Database
    database_url: str = "postgresql://fraudguard:fraudguard_dev_pass@localhost:5432/fraudguard_db"
    
    # JWT
    jwt_secret_key: str = "change-this-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # Server
    debug: bool = False
    environment: str = "development"
    api_title: str = "FraudGuard AI API"
    api_version: str = "0.1.0"
    
    # CORS
    cors_origins: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]
    
    # ML Model paths (relative to backend directory)
    model_path: str = "../ml/artifacts/fraud_model.joblib"
    preprocessor_path: str = "../ml/artifacts/preprocessor.joblib"
    model_metadata_path: str = "../ml/artifacts/model_metadata.json"
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Instantiate settings
settings = Settings()
