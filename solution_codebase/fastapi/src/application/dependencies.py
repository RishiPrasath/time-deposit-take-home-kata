from typing import Generator
from sqlalchemy.orm import Session
from fastapi import Depends

from src.infrastructure.database.connection import get_db
from src.infrastructure.database.repositories.time_deposit_repository import TimeDepositRepository
from src.infrastructure.adapters.time_deposit_repository_adapter import TimeDepositRepositoryAdapter
from src.application.services.time_deposit_service import TimeDepositService

def get_time_deposit_service(db: Session = Depends(get_db)) -> TimeDepositService:
    """
    Dependency injection factory for time deposit service.

    This creates the complete dependency chain:
    1. Database session
    2. SQL repository (infrastructure)
    3. Repository adapter (bridge)
    4. Application service

    Returns:
        Configured TimeDepositService instance
    """
    # Create infrastructure repository
    sql_repository = TimeDepositRepository(db)

    # Wrap in adapter (handles all conversions)
    adapter = TimeDepositRepositoryAdapter(sql_repository)

    # Create service with adapter
    return TimeDepositService(adapter)