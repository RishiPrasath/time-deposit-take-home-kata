# Phase 3: Application Layer Implementation Plan
## Service Layer & Workflow Orchestration

### 🎯 Phase Overview
**Duration**: 60 minutes  
**Dependencies**: Completed Infrastructure Layer (Phase 1) and Domain Layer (Phase 2)  
**Goal**: Create the orchestration layer that bridges domain logic with infrastructure

---

## 📋 Pre-Implementation Checklist

### ✅ Prerequisites from Previous Phases:

**From Phase 1 (Infrastructure):**
- [ ] Database models created (`TimeDepositModel`, `WithdrawalModel`)
- [ ] Repository implementation (`TimeDepositRepository`)
- [ ] Database connection working
- [ ] Sample data can be inserted/retrieved

**From Phase 2 (Domain):**
- [ ] `TimeDeposit` class copied exactly (no modifications)
- [ ] `TimeDepositCalculator` class preserved
- [ ] Repository interfaces defined
- [ ] Domain tests passing

---

## 🏗️ Application Layer Architecture

```
app/application/
├── __init__.py
├── services/
│   ├── __init__.py
│   └── time_deposit_service.py
├── schemas/
│   ├── __init__.py
│   └── time_deposit.py
├── mappers/
│   ├── __init__.py
│   └── time_deposit_mapper.py
└── exceptions/
    ├── __init__.py
    └── service_exceptions.py
```

---

## 📝 Implementation Steps

### Step 1: Create Pydantic Schemas (20 minutes)

#### 1.1 Response Models
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

#### 1.2 Internal DTOs
```python
# app/application/schemas/internal_dto.py
from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional
from datetime import date

@dataclass
class DepositUpdateResult:
    """Internal DTO for tracking update operations"""
    deposit_id: int
    previous_balance: Decimal
    new_balance: Decimal
    interest_applied: Decimal
    
@dataclass
class ServiceOperationResult:
    """Generic result wrapper for service operations"""
    success: bool
    data: Optional[any] = None
    error: Optional[str] = None
    metadata: Optional[dict] = None
```

### Step 2: Create Data Mappers (15 minutes)

#### 2.1 Domain-Infrastructure Mapping
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
```

### Step 3: Implement Service Layer (40 minutes)

#### 3.1 Core Service Implementation
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
        
        Workflow:
        1. Retrieve all deposits from repository
        2. Convert to domain entities
        3. Apply interest calculations
        4. Convert back to models and save
        5. Return operation result
        """
        try:
            # Step 1: Get all deposits
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
            
            # Step 2: Convert to domain entities
            logger.info(f"Converting {len(deposit_models)} deposits to domain entities")
            domain_deposits = [
                self.mapper.model_to_domain(model) 
                for model in deposit_models
            ]
            
            # Step 3: Apply interest calculations (preserves original logic)
            logger.info("Applying interest calculations")
            original_balances = {d.id: d.balance for d in domain_deposits}
            
            # This uses the EXACT original algorithm - no modifications
            self.calculator.update_balance(domain_deposits)
            
            # Step 4: Convert back and save
            logger.info("Saving updated balances to database")
            for i, domain_deposit in enumerate(domain_deposits):
                deposit_model = deposit_models[i]
                self.mapper.domain_to_model(domain_deposit, deposit_model)
            
            self.repository.save_all(deposit_models)
            
            # Step 5: Calculate summary
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
        
        Workflow:
        1. Get all deposits with withdrawals from repository
        2. Convert to response format
        3. Return formatted data
        """
        try:
            logger.info("Retrieving all time deposits with withdrawals")
            
            # Step 1: Get deposits with eager-loaded withdrawals
            deposit_models = self.repository.get_all_with_withdrawals()
            
            # Step 2: Convert to response format
            logger.info(f"Converting {len(deposit_models)} deposits to response format")
            responses = self.mapper.models_to_responses(deposit_models)
            
            # Step 3: Return data
            logger.info(f"Successfully retrieved {len(responses)} time deposits")
            return responses
            
        except Exception as e:
            logger.error(f"Error retrieving deposits: {str(e)}")
            raise ServiceException(f"Failed to retrieve deposits: {str(e)}")
```

#### 3.2 Service Exceptions
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

### Step 4: Create Service Factory (5 minutes)

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

---

## 🧪 Testing Strategy

### Unit Tests for Service Layer
```python
# tests/application/test_time_deposit_service.py
import pytest
from unittest.mock import Mock, MagicMock
from decimal import Decimal
from datetime import date

from app.application.services.time_deposit_service import TimeDepositService
from app.domain.entities.time_deposit import TimeDeposit
from app.infrastructure.database.models import TimeDepositModel, WithdrawalModel

class TestTimeDepositService:
    
    @pytest.fixture
    def mock_repository(self):
        return Mock()
    
    @pytest.fixture
    def service(self, mock_repository):
        return TimeDepositService(mock_repository)
    
    def test_update_all_balances_success(self, service, mock_repository):
        # Arrange
        mock_deposits = [
            self._create_mock_deposit(1, "basic", 1000.00, 45),
            self._create_mock_deposit(2, "student", 2000.00, 35)
        ]
        mock_repository.get_all.return_value = mock_deposits
        mock_repository.save_all.return_value = None
        
        # Act
        result = service.update_all_balances()
        
        # Assert
        assert result.success is True
        assert result.updated_count == 2
        assert "Successfully updated" in result.message
        mock_repository.get_all.assert_called_once()
        mock_repository.save_all.assert_called_once()
    
    def test_update_all_balances_no_deposits(self, service, mock_repository):
        # Arrange
        mock_repository.get_all.return_value = []
        
        # Act
        result = service.update_all_balances()
        
        # Assert
        assert result.success is True
        assert result.updated_count == 0
        assert "No time deposits found" in result.message
    
    def test_get_all_deposits_with_withdrawals(self, service, mock_repository):
        # Arrange
        mock_deposit = self._create_mock_deposit_with_withdrawals()
        mock_repository.get_all_with_withdrawals.return_value = [mock_deposit]
        
        # Act
        result = service.get_all_deposits()
        
        # Assert
        assert len(result) == 1
        assert result[0].id == 1
        assert len(result[0].withdrawals) == 2
        assert result[0].withdrawals[0].amount == Decimal("100.00")
    
    def _create_mock_deposit(self, id, plan_type, balance, days):
        deposit = MagicMock(spec=TimeDepositModel)
        deposit.id = id
        deposit.planType = plan_type
        deposit.balance = Decimal(str(balance))
        deposit.days = days
        deposit.withdrawals = []
        return deposit
    
    def _create_mock_deposit_with_withdrawals(self):
        deposit = self._create_mock_deposit(1, "basic", 1000.00, 45)
        
        withdrawal1 = MagicMock(spec=WithdrawalModel)
        withdrawal1.id = 1
        withdrawal1.amount = Decimal("100.00")
        withdrawal1.date = date(2024, 1, 15)
        
        withdrawal2 = MagicMock(spec=WithdrawalModel)
        withdrawal2.id = 2
        withdrawal2.amount = Decimal("200.00")
        withdrawal2.date = date(2024, 2, 1)
        
        deposit.withdrawals = [withdrawal1, withdrawal2]
        return deposit
```

### Integration Tests
```python
# tests/application/test_service_integration.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infrastructure.database.models import Base, TimeDepositModel, WithdrawalModel
from app.infrastructure.database.repositories.time_deposit_repository import TimeDepositRepository
from app.application.services.time_deposit_service import TimeDepositService

class TestServiceIntegration:
    
    @pytest.fixture
    def test_db(self):
        # Create in-memory SQLite database for testing
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        return SessionLocal()
    
    @pytest.fixture
    def repository(self, test_db):
        return TimeDepositRepository(test_db)
    
    @pytest.fixture
    def service(self, repository):
        return TimeDepositService(repository)
    
    def test_full_update_workflow(self, service, repository, test_db):
        # Arrange - Create test data
        deposit1 = TimeDepositModel(
            planType="basic",
            balance=Decimal("1000.00"),
            days=45
        )
        deposit2 = TimeDepositModel(
            planType="student",
            balance=Decimal("2000.00"),
            days=35
        )
        test_db.add_all([deposit1, deposit2])
        test_db.commit()
        
        # Act - Update balances
        result = service.update_all_balances()
        
        # Assert - Verify updates
        assert result.success is True
        assert result.updated_count == 2
        
        # Verify balances were actually updated in database
        updated_deposits = repository.get_all()
        assert updated_deposits[0].balance > Decimal("1000.00")  # Interest applied
        assert updated_deposits[1].balance > Decimal("2000.00")  # Interest applied
```

---

## 📋 Implementation Checklist

### Service Layer Components:
- [ ] Pydantic schemas created with exact field names
- [ ] Data mappers handle all transformations
- [ ] Service implements both required operations
- [ ] Exception handling implemented
- [ ] Logging added for debugging
- [ ] Factory function for dependency injection

### Testing:
- [ ] Unit tests for service methods
- [ ] Mock repository for isolated testing
- [ ] Integration tests with real database
- [ ] Edge cases covered
- [ ] Error scenarios tested

### Integration Points:
- [ ] Service uses repository interface (not concrete)
- [ ] Domain logic preserved exactly
- [ ] Data transformations work correctly
- [ ] No breaking changes to existing logic

---

## 🚀 Next Steps

After completing Phase 3:

1. **Validate Service Layer**:
   ```bash
   pytest tests/application/ -v
   ```

2. **Test Integration**:
   ```bash
   python scripts/test_service_workflows.py
   ```

3. **Proceed to Phase 4** (API Layer):
   - FastAPI endpoint implementation
   - Dependency injection setup
   - End-to-end testing

---

## 💡 Key Success Factors

1. **Preserve Domain Logic**: The `TimeDepositCalculator.update_balance` method must work exactly as before
2. **Clean Orchestration**: Service layer only orchestrates, doesn't implement business logic
3. **Proper Error Handling**: All exceptions caught and wrapped appropriately
4. **Testability**: Use dependency injection for easy testing
5. **Data Integrity**: Ensure decimal precision is maintained throughout

---

## ⚠️ Common Pitfalls to Avoid

1. **Don't Modify Domain Logic**: Keep `TimeDeposit` and `TimeDepositCalculator` exactly as they are
2. **Handle Decimal Precision**: Use `Decimal` for money, convert carefully between layers
3. **Avoid Business Logic in Service**: Service orchestrates, domain calculates
4. **Test Edge Cases**: Empty lists, null values, large numbers
5. **Log Appropriately**: Add logging for debugging but don't over-log

This completes Phase 3 implementation plan! Ready to build the service layer? 🎯