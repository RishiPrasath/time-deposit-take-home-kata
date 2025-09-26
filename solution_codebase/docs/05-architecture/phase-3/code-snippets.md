# Phase 3: Code Snippets for Quick Implementation

## 1. Complete Service Implementation

```python
# app/application/services/time_deposit_service.py
from typing import List
from datetime import datetime
from decimal import Decimal
import logging

from app.domain.entities.time_deposit import TimeDepositCalculator
from app.domain.interfaces.repositories import TimeDepositRepositoryInterface
from app.application.schemas.time_deposit import TimeDepositResponse, UpdateBalancesResponse
from app.application.mappers.time_deposit_mapper import TimeDepositMapper
from app.application.exceptions.service_exceptions import ServiceException

logger = logging.getLogger(__name__)

class TimeDepositService:
    """
    Application service for time deposit operations.
    Orchestrates between domain logic and infrastructure.
    """
    
    def __init__(self, repository: TimeDepositRepositoryInterface):
        self.repository = repository
        self.calculator = TimeDepositCalculator()
        self.mapper = TimeDepositMapper()
    
    def update_all_balances(self) -> UpdateBalancesResponse:
        """
        Update balances for all time deposits using domain calculation logic.
        """
        try:
            # Get all deposits
            logger.info("Retrieving all time deposits for balance update")
            deposit_models = self.repository.get_all()
            
            if not deposit_models:
                logger.warning("No time deposits found to update")
                return UpdateBalancesResponse(
                    success=True,
                    message="No time deposits found to update",
                    updated_count=0,
                    timestamp=datetime.utcnow().date()
                )
            
            # Convert to domain entities
            logger.info(f"Converting {len(deposit_models)} deposits to domain entities")
            domain_deposits = [
                self.mapper.model_to_domain(model) 
                for model in deposit_models
            ]
            
            # Store original balances for comparison
            original_balances = {d.id: d.balance for d in domain_deposits}
            
            # Apply interest calculations using existing logic
            self.calculator.update_balance(domain_deposits)
            
            # Convert back and save
            logger.info("Saving updated balances to database")
            for i, domain_deposit in enumerate(domain_deposits):
                deposit_model = deposit_models[i]
                self.mapper.domain_to_model(domain_deposit, deposit_model)
            
            self.repository.save_all(deposit_models)
            
            # Calculate how many were actually updated
            updated_count = sum(
                1 for d in domain_deposits 
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
        """
        try:
            logger.info("Retrieving all time deposits with withdrawals")
            
            # Get deposits with eager-loaded withdrawals
            deposit_models = self.repository.get_all_with_withdrawals()
            
            # Convert to response format
            logger.info(f"Converting {len(deposit_models)} deposits to response format")
            responses = self.mapper.models_to_responses(deposit_models)
            
            logger.info(f"Successfully retrieved {len(responses)} time deposits")
            return responses
            
        except Exception as e:
            logger.error(f"Error retrieving deposits: {str(e)}")
            raise ServiceException(f"Failed to retrieve deposits: {str(e)}")
```## 2. Complete Mapper Implementation

```python
# app/application/mappers/time_deposit_mapper.py
from typing import List
from decimal import Decimal
from app.domain.entities.time_deposit import TimeDeposit
from app.infrastructure.database.models import TimeDepositModel, WithdrawalModel
from app.application.schemas.time_deposit import TimeDepositResponse, WithdrawalResponse

class TimeDepositMapper:
    """Handles data transformation between layers"""
    
    @staticmethod
    def model_to_domain(model: TimeDepositModel) -> TimeDeposit:
        """Convert database model to domain entity"""
        return TimeDeposit(
            id=model.id,
            planType=model.planType,
            balance=float(model.balance),  # Domain uses float
            days=model.days
        )
    
    @staticmethod
    def domain_to_model(domain: TimeDeposit, model: TimeDepositModel) -> TimeDepositModel:
        """Update database model from domain entity"""
        model.balance = Decimal(str(domain.balance))  # Preserve precision
        # Note: We only update balance, other fields are immutable
        return model

    @staticmethod
    def model_to_response(model: TimeDepositModel) -> TimeDepositResponse:
        """Convert database model to API response"""
        withdrawals = [
            WithdrawalResponse(
                id=w.id,
                amount=w.amount,
                date=w.date
            )
            for w in model.withdrawals
        ]
        
        return TimeDepositResponse(
            id=model.id,
            planType=model.planType,
            balance=model.balance,
            days=model.days,
            withdrawals=withdrawals
        )
    
    @staticmethod
    def models_to_responses(models: List[TimeDepositModel]) -> List[TimeDepositResponse]:
        """Convert list of models to list of responses"""
        return [TimeDepositMapper.model_to_response(model) for model in models]
```## 3. Complete Schema Definitions

```python
# app/application/schemas/time_deposit.py
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from datetime import date
from typing import List

class WithdrawalResponse(BaseModel):
    """Response model for withdrawal data"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="Unique withdrawal identifier")
    amount: Decimal = Field(..., description="Withdrawal amount", decimal_places=2)
    date: date = Field(..., description="Withdrawal date in YYYY-MM-DD format")

class TimeDepositResponse(BaseModel):
    """Response model for time deposit with withdrawals"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="Unique deposit identifier")
    planType: str = Field(..., description="Plan type: basic, student, or premium")
    balance: Decimal = Field(..., description="Current balance with interest", decimal_places=2)
    days: int = Field(..., description="Number of days since deposit creation")
    withdrawals: List[WithdrawalResponse] = Field(
        default_factory=list, 
        description="List of withdrawals for this deposit"
    )

class UpdateBalancesResponse(BaseModel):
    """Response model for balance update operation"""
    success: bool = Field(..., description="Whether the operation succeeded")
    message: str = Field(..., description="Human-readable result message")
    updated_count: int = Field(..., description="Number of deposits updated")
    timestamp: date = Field(..., description="When the update occurred")
```

## 4. Exception Classes

```python
# app/application/exceptions/service_exceptions.py
class ServiceException(Exception):
    """Base exception for service layer errors"""
    pass

class RepositoryException(ServiceException):
    """Exception for repository operation failures"""
    pass

class ValidationException(ServiceException):
    """Exception for data validation failures"""
    pass

class BusinessRuleException(ServiceException):
    """Exception for business rule violations"""
    pass
```
## 5. Service Factory

```python
# app/application/services/__init__.py
from app.infrastructure.database.repositories.time_deposit_repository import TimeDepositRepository
from app.application.services.time_deposit_service import TimeDepositService
from app.infrastructure.database.connection import get_db

def get_time_deposit_service() -> TimeDepositService:
    """
    Factory function to create service with dependencies.
    Used for dependency injection in FastAPI.
    """
    db = next(get_db())
    repository = TimeDepositRepository(db)
    return TimeDepositService(repository)
```

## 6. __init__.py Files

```python
# app/application/__init__.py
"""Application layer - orchestrates business workflows"""

# app/application/services/__init__.py
from .time_deposit_service import TimeDepositService

__all__ = ["TimeDepositService"]

# app/application/schemas/__init__.py
from .time_deposit import TimeDepositResponse, WithdrawalResponse, UpdateBalancesResponse
__all__ = ["TimeDepositResponse", "WithdrawalResponse", "UpdateBalancesResponse"]

# app/application/mappers/__init__.py
from .time_deposit_mapper import TimeDepositMapper

__all__ = ["TimeDepositMapper"]

# app/application/exceptions/__init__.py
from .service_exceptions import ServiceException, RepositoryException, ValidationException

__all__ = ["ServiceException", "RepositoryException", "ValidationException"]
```

## 7. Quick Test Runner Script

```python
# scripts/test_application_layer.py
import subprocess
import sys

def run_tests():
    """Run application layer tests"""
    print("🧪 Running Application Layer Tests...")
    print("=" * 50)
    
    # Run unit tests
    print("\n📋 Running unit tests...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/application/test_time_deposit_service.py", 
        "-v"
    ])
    
    if result.returncode != 0:
        print("❌ Unit tests failed!")
        return False
    
    # Run mapper tests
    print("\n🔄 Running mapper tests...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/application/test_mappers.py", 
        "-v"
    ])
    
    if result.returncode != 0:
        print("❌ Mapper tests failed!")
        return False
    
    # Run schema tests
    print("\n📝 Running schema tests...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/application/test_schemas.py", 
        "-v"
    ])
    
    if result.returncode != 0:
        print("❌ Schema tests failed!")
        return False
    
    print("\n✅ All application layer tests passed!")
    return True
if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
```

## 8. Sample Test Data Creator

```python
# scripts/create_test_deposits.py
from decimal import Decimal
from datetime import date, timedelta
from app.infrastructure.database.models import TimeDepositModel, WithdrawalModel
from app.infrastructure.database.connection import get_db, engine
from app.infrastructure.database.models import Base

def create_test_data():
    """Create sample test data for development"""
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = next(get_db())
    
    # Create deposits
    deposits = [
        TimeDepositModel(
            planType="basic",
            balance=Decimal("1000.00"),
            days=45
        ),
        TimeDepositModel(
            planType="student",
            balance=Decimal("5000.00"),            days=90
        ),
        TimeDepositModel(
            planType="premium",
            balance=Decimal("10000.00"),
            days=50
        ),
        TimeDepositModel(
            planType="basic",
            balance=Decimal("2500.00"),
            days=25  # No interest yet
        )
    ]
    
    db.add_all(deposits)
    db.commit()
    
    # Add withdrawals to second deposit
    withdrawals = [
        WithdrawalModel(
            timeDepositId=2,
            amount=Decimal("500.00"),
            date=date.today() - timedelta(days=30)
        ),
        WithdrawalModel(
            timeDepositId=2,
            amount=Decimal("250.00"),
            date=date.today() - timedelta(days=15)
        )
    ]    
    db.add_all(withdrawals)
    db.commit()
    
    print("✅ Test data created successfully!")
    print(f"📊 Created {len(deposits)} deposits and {len(withdrawals)} withdrawals")

if __name__ == "__main__":
    create_test_data()
```

## 9. Logging Configuration

```python
# app/application/config/logging_config.py
import logging
import sys

def setup_logging():
    """Configure logging for the application"""
    
    # Create logger
    logger = logging.getLogger('app')
    logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler
    logger.addHandler(console_handler)
    
    return logger
```

These snippets provide everything needed for quick copy-paste implementation of Phase 3!