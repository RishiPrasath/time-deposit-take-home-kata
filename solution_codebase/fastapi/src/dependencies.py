"""
Dependency injection for src/main.py FastAPI application.
Connects to the clean architecture layers in src/.
"""
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session

from src.infrastructure.database.connection import get_db
from src.infrastructure.database.repositories.time_deposit_repository import TimeDepositRepository
from src.infrastructure.adapters.time_deposit_repository_adapter import TimeDepositRepositoryAdapter
from src.application.services.time_deposit_service import TimeDepositService
from src.infrastructure.config.settings import Settings

# Database dependency
def get_database():
    """Get database session from src infrastructure layer."""
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()

DatabaseDep = Annotated[Session, Depends(get_database)]

# Repository dependency
def get_time_deposit_repository(
    db: DatabaseDep
) -> TimeDepositRepositoryAdapter:
    """Get time deposit repository adapter."""
    sql_repository = TimeDepositRepository(db)
    return TimeDepositRepositoryAdapter(sql_repository)

RepositoryDep = Annotated[TimeDepositRepositoryAdapter, Depends(get_time_deposit_repository)]

# Service dependency
def get_time_deposit_service(
    repository: RepositoryDep
) -> TimeDepositService:
    """Get time deposit service from src application layer."""
    return TimeDepositService(repository)

ServiceDep = Annotated[TimeDepositService, Depends(get_time_deposit_service)]

# Settings dependency
def get_settings() -> Settings:
    """Get application settings."""
    return Settings()

SettingsDep = Annotated[Settings, Depends(get_settings)]