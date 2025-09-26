# Phase 3: Ready-to-Use Implementation Code

## 🚀 Copy-Paste Code for Existing FastAPI Project

### 1. Complete Service Implementation

```python
# app/application/services/time_deposit_service.py
from typing import List
from datetime import datetime
from decimal import Decimal
import logging

from app.domain.entities.time_deposit import TimeDepositCalculator
from app.domain.interfaces.repositories import TimeDepositRepositoryInterface
from app.application.schemas.time_deposit import TimeDepositResponse, WithdrawalResponse, UpdateBalancesResponse
from app.application.exceptions.service_exceptions import ServiceException

logger = logging.getLogger(__name__)

class TimeDepositService:
    """
    Application service that orchestrates time deposit operations.
    Uses the existing repository adapter for all data operations.
    """
    
    def __init__(self, repository: TimeDepositRepositoryInterface):
        """
        Initialize service with repository interface.
        In practice, this will be the TimeDepositRepositoryAdapter.
        
        Args:
            repository: Repository interface (injected adapter)
        """
        self.repository = repository
        self.calculator = TimeDepositCalculator()
    
    def update_all_balances(self) -> UpdateBalancesResponse:
        """
        Update all time deposit balances using the EXACT original calculator logic.
        
        Returns:
            UpdateBalancesResponse with operation results
        """
        try:
            # Get all deposits as domain entities (adapter handles conversion)
            logger.info("Retrieving all time deposits for balance update")
            deposits = self.repository.get_all()
            
            if not deposits:
                logger.warning("No time deposits found to update")
                return UpdateBalancesResponse(
                    success=True,
                    message="No time deposits found to update",
                    updated_count=0,
                    timestamp=datetime.utcnow().date()
                )
            
            # Store original balances for comparison
            original_balances = {d.id: d.balance for d in deposits}
            logger.info(f"Processing {len(deposits)} deposits for interest calculation")
            
            # Apply EXACT original interest calculation
            # This preserves the unusual cumulative interest logic
            self.calculator.update_balance(deposits)
            
            # Save updated deposits (adapter handles conversion back)
            logger.info("Saving updated balances to database")
            self.repository.save_all(deposits)
            
            # Count actual updates
            updated_count = sum(
                1 for d in deposits 
                if d.balance != original_balances[d.id]
            )
            
            logger.info(f"Successfully updated {updated_count} deposits")
            
            return UpdateBalancesResponse(
                success=True,
                message=f"Successfully updated {updated_count} time deposit balances",
                updated_count=updated_count,
                timestamp=datetime.utcnow().date()
            )
            
        except Exception as e:
            logger.error(f"Error updating balances: {str(e)}")
            raise ServiceException(f"Failed to update balances: {str(e)}")
    
    def get_all_deposits(self) -> List[TimeDepositResponse]:
        """
        Retrieve all time deposits with their withdrawals.
        
        Returns:
            List of TimeDepositResponse objects
        """
        try:
            logger.info("Retrieving all time deposits with withdrawals")
            
            # Get deposits with withdrawals (adapter handles joins)
            deposits = self.repository.get_all_with_withdrawals()
            
            # Convert to response format
            responses = []
            for deposit in deposits:
                # Convert withdrawals to response format
                withdrawal_responses = []
                for withdrawal in deposit.withdrawals:
                    withdrawal_response = WithdrawalResponse(
                        id=withdrawal.id,
                        amount=Decimal(str(withdrawal.amount)),
                        date=datetime.fromisoformat(withdrawal.date).date()
                    )
                    withdrawal_responses.append(withdrawal_response)
                
                # Create deposit response with exact field names
                response = TimeDepositResponse(
                    id=deposit.id,
                    planType=deposit.planType,  # Must be planType, not plan_type!
                    balance=Decimal(str(deposit.balance)),
                    days=deposit.days,
                    withdrawals=withdrawal_responses
                )
                responses.append(response)
            
            logger.info(f"Successfully retrieved {len(responses)} time deposits")
            return responses
            
        except Exception as e:
            logger.error(f"Error retrieving deposits: {str(e)}")
            raise ServiceException(f"Failed to retrieve deposits: {str(e)}")
```### 2. Pydantic Schemas

```python
# app/application/schemas/time_deposit.py
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from datetime import date
from typing import List

class WithdrawalResponse(BaseModel):
    """Response model for withdrawal data."""
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            Decimal: lambda v: float(v),
            date: lambda v: v.isoformat()
        }
    )
    
    id: int = Field(..., description="Unique withdrawal identifier")
    amount: Decimal = Field(..., description="Withdrawal amount", decimal_places=2)
    date: date = Field(..., description="Withdrawal date in YYYY-MM-DD format")

class TimeDepositResponse(BaseModel):
    """
    Response model for time deposit with exact required schema.
    
    CRITICAL: Field names must match exactly:
    - planType (not plan_type)
    - All fields required
    """
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            Decimal: lambda v: float(v),
            date: lambda v: v.isoformat()
        }
    )
    
    id: int = Field(..., description="Unique deposit identifier")
    planType: str = Field(..., description="Plan type: basic, student, or premium")
    balance: Decimal = Field(..., description="Current balance with interest", decimal_places=2)
    days: int = Field(..., description="Number of days since deposit creation")
    withdrawals: List[WithdrawalResponse] = Field(
        default_factory=list,
        description="List of withdrawals for this deposit"
    )

class UpdateBalancesResponse(BaseModel):
    """Response model for balance update operation."""
    success: bool = Field(..., description="Whether the operation succeeded")
    message: str = Field(..., description="Human-readable result message")
    updated_count: int = Field(..., description="Number of deposits updated")
    timestamp: date = Field(..., description="When the update occurred")
```

### 3. Exception Classes

```python
# app/application/exceptions/service_exceptions.py
"""
Service layer exceptions
"""

class ServiceException(Exception):
    """Base exception for service layer errors."""
    pass

class RepositoryException(ServiceException):
    """Exception for repository operation failures."""
    pass

class ValidationException(ServiceException):
    """Exception for data validation failures."""
    pass

class BusinessRuleException(ServiceException):
    """Exception for business rule violations."""
    pass
```

### 4. Dependency Injection

```python
# app/application/dependencies.py
from typing import Generator
from sqlalchemy.orm import Session
from fastapi import Depends

from app.infrastructure.database.connection import get_db
from app.infrastructure.database.repositories.time_deposit_repository import TimeDepositRepository
from app.infrastructure.adapters.time_deposit_repository_adapter import TimeDepositRepositoryAdapter
from app.application.services.time_deposit_service import TimeDepositService

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
```### 5. Init Files

```python
# app/application/__init__.py
"""
Application layer - orchestrates business workflows.

This layer contains:
- Services: Business operation orchestration
- Schemas: API request/response models
- Dependencies: Dependency injection setup
"""

# app/application/services/__init__.py
from .time_deposit_service import TimeDepositService

__all__ = ["TimeDepositService"]

# app/application/schemas/__init__.py
from .time_deposit import (
    TimeDepositResponse,
    WithdrawalResponse,
    UpdateBalancesResponse
)

__all__ = [
    "TimeDepositResponse",
    "WithdrawalResponse",
    "UpdateBalancesResponse"
]

# app/application/exceptions/__init__.py
from .service_exceptions import (
    ServiceException,
    RepositoryException,
    ValidationException,
    BusinessRuleException
)

__all__ = [
    "ServiceException",
    "RepositoryException", 
    "ValidationException",
    "BusinessRuleException"
]
```

### 6. Test for Service Integration

```python
# tests/application/test_time_deposit_service.py
import pytest
from unittest.mock import Mock, MagicMock
from decimal import Decimal
from datetime import date

from app.domain.entities.time_deposit import TimeDeposit
from app.domain.entities.withdrawal import Withdrawal
from app.application.services.time_deposit_service import TimeDepositService
from app.application.schemas.time_deposit import UpdateBalancesResponse

class TestTimeDepositService:
    
    @pytest.fixture
    def mock_repository(self):
        """Create a mock repository that implements the interface."""
        return Mock()
    
    @pytest.fixture
    def service(self, mock_repository):
        """Create service with mocked repository."""
        return TimeDepositService(mock_repository)
    
    def test_update_all_balances_with_existing_deposits(self, service, mock_repository):
        # Arrange
        deposits = [
            TimeDeposit(1, "basic", 1000.0, 45),
            TimeDeposit(2, "student", 2000.0, 90)
        ]
        mock_repository.get_all.return_value = deposits
        
        # Act
        result = service.update_all_balances()
        
        # Assert
        assert isinstance(result, UpdateBalancesResponse)
        assert result.success is True
        assert result.updated_count > 0
        mock_repository.save_all.assert_called_once_with(deposits)
    
    def test_get_all_deposits_with_withdrawals(self, service, mock_repository):
        # Arrange
        deposit = TimeDeposit(1, "basic", 1000.0, 45)
        withdrawal = Withdrawal(1, 100.0, "2024-01-15")
        deposit.withdrawals = [withdrawal]
        
        mock_repository.get_all_with_withdrawals.return_value = [deposit]
        
        # Act
        result = service.get_all_deposits()
        
        # Assert
        assert len(result) == 1
        assert result[0].id == 1
        assert result[0].planType == "basic"  # Exact field name
        assert len(result[0].withdrawals) == 1
```

### 7. Quick Setup Script

```python
# scripts/setup_application_layer.py
import os
import sys

def create_application_structure():
    """Create application layer directory structure."""
    
    base_path = "app/application"
    subdirs = ["services", "schemas", "exceptions"]
    
    # Create base directory
    os.makedirs(base_path, exist_ok=True)
    
    # Create __init__.py
    with open(f"{base_path}/__init__.py", "w") as f:
        f.write('"""Application layer - orchestrates business workflows."""\n')
    
    # Create subdirectories
    for subdir in subdirs:
        path = f"{base_path}/{subdir}"
        os.makedirs(path, exist_ok=True)
        with open(f"{path}/__init__.py", "w") as f:
            f.write(f'"""{subdir.capitalize()} module."""\n')
    
    print("✅ Application layer structure created!")
    print(f"📁 Created directories: {', '.join(subdirs)}")

if __name__ == "__main__":
    create_application_structure()
```

## 🔧 Integration Commands

```bash
# 1. Navigate to your FastAPI project
cd C:\Users\prasa\Code\ikigai-take-home-assignment\Python\fastapi

# 2. Run setup script
python scripts/setup_application_layer.py

# 3. Copy the code files from above into their respective locations

# 4. Run tests
python -m pytest tests/application/ -v

# 5. Check integration
python -c "from app.application.services import TimeDepositService; print('✅ Import successful!')"
```

All code is tailored to work with your existing FastAPI structure!