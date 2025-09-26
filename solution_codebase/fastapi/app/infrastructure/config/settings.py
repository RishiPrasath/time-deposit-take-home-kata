from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    # Database
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/timedeposit_db"
    )
    DATABASE_URL_TEST: str = Field(
        default="sqlite:///./test.db"
    )

    # PostgreSQL specific
    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: str = Field(default="postgres")
    POSTGRES_DB: str = Field(default="timedeposit_db")
    POSTGRES_HOST: str = Field(default="localhost")
    POSTGRES_PORT: int = Field(default=5432)

    # Application
    APP_NAME: str = Field(default="Time Deposit Management System")
    APP_VERSION: str = Field(default="1.0.0")
    DEBUG: bool = Field(default=True)

    # API
    API_V1_STR: str = Field(default="/api/v1")


settings = Settings()