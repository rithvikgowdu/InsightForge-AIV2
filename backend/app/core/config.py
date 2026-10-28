from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "InsightForge AI"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Security & Auth
    SECRET_KEY: str = "dev-insecure-secret-key-replace-in-production-min32chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Database
    # Default to local sqlite for development/testing if no Postgres specified
    DATABASE_URL: str = "sqlite:///./insightforge.db"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    # External APIs
    GITHUB_TOKEN: Optional[str] = None
    GITHUB_API_BASE_URL: str = "https://api.github.com"

    # AI Pipeline Configuration
    LLM_PROVIDER: str = "deterministic_fallback"  # "deterministic_fallback" | "ollama" | "hosted"
    LLM_MODEL: str = "llama3.2"
    LLM_API_KEY: Optional[str] = None
    LLM_API_BASE_URL: Optional[str] = "http://localhost:11434/v1"

    # Embeddings
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    USE_LIGHTWEIGHT_EMBEDDINGS: bool = False

    # Analysis Defaults
    DEFAULT_ISSUE_LIMIT: int = 50
    MAX_ISSUE_LIMIT: int = 150

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()

