# Phase 3: Application Layer Implementation Plan (REFINED)
## Integration with Existing FastAPI Codebase

### 🎯 Current Codebase Analysis

**Existing Structure:**
```
C:\Users\prasa\Code\ikigai-take-home-assignment\Python\fastapi\
├── app/
│   ├── domain/               ✅ Phase 2 Complete
│   │   ├── entities/        (TimeDeposit, Withdrawal classes)
│   │   ├── interfaces/      (TimeDepositRepositoryInterface)
│   │   └── value_objects/
│   ├── infrastructure/       ✅ Phase 1 Complete  
│   │   ├── adapters/        (TimeDepositRepositoryAdapter - bridges domain/infra)
│   │   ├── config/
│   │   └── database/        (models, repositories, connection)
│   └── application/         ❌ MISSING - We need to create this!
├── tests/
├── migrations/
└── requirements.txt
```

**Key Integration Points Discovered:**
1. ✅ Domain layer has the EXACT original `TimeDeposit` and `TimeDepositCalculator` classes
2. ✅ Infrastructure has SQLAlchemy models and repository
3. ✅ An adapter (`TimeDepositRepositoryAdapter`) already bridges domain ↔ infrastructure
4. ❌ Missing: Application layer (services, schemas, mappers)
5. ❌ Missing: API layer (FastAPI endpoints)

---

## 📋 Refined Implementation Plan

### Step 1: Create Application Layer Structure (5 min)

```bash
# Navigate to the FastAPI project
cd C:\Users\prasa\Code\ikigai-take-home-assignment\Python\fastapi

# Create application layer directories
mkdir app\application
mkdir app\application\services
mkdir app\application\schemas  
mkdir app\application\exceptions

# Create __init__.py files
echo. > app\application\__init__.py
echo. > app\application\services\__init__.py
echo. > app\application\schemas\__init__.py
echo. > app\application\exceptions\__init__.py
```### Step 2: Create Pydantic Schemas (15 min)

**IMPORTANT**: The existing codebase has a `Withdrawal` domain entity. Let's check if it matches our schema needs.

#### 2.1 Create Response Schemas
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
    """Response model matching EXACT required schema"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    planType: str  # ⚠️ MUST be planType, not plan_type!
    balance: Decimal
    days: int
    withdrawals: List[WithdrawalResponse] = Field(default_factory=list)

class UpdateBalancesResponse(BaseModel):
    """Response for update operation"""
    success: bool
    message: str
    updated_count: int
    timestamp: date = Field(default_factory=lambda: datetime.utcnow().date())
```### Step 3: Create Service Layer (30 min)

**KEY INSIGHT**: We already have `TimeDepositRepositoryAdapter` that handles domain↔infrastructure conversion!

#### 3.1 Service Implementation
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
    Application service that orchestrates business operations.
    
    KEY: Uses domain repository interface, not concrete implementation!
    This allows us to inject the adapter that handles conversions.
    """
    
    def __init__(self, repository: TimeDepositRepositoryInterface):
        """
        Args:
            repository: Domain repository interface (will be adapter in practice)
        """
        self.repository = repository
        self.calculator = TimeDepositCalculator()
    
    def update_all_balances(self) -> UpdateBalancesResponse:
        """
        Update all time deposit balances using original calculator logic.
        
        Flow:
        1. Get deposits via repository (adapter handles model→domain conversion)
        2. Apply EXACT original calculation logic
        3. Save back via repository (adapter handles domain→model conversion)
        """
        try:
            # Get all deposits as domain entities
            deposits = self.repository.get_all()
            
            if not deposits:
                return UpdateBalancesResponse(
                    success=True,
                    message="No time deposits found to update",
                    updated_count=0
                )
            
            # Store original balances
            original_balances = {d.id: d.balance for d in deposits}
            
            # Apply EXACT original interest calculation
            # ⚠️ CRITICAL: This uses the unusual cumulative logic that MUST be preserved
            self.calculator.update_balance(deposits)
            
            # Save updated deposits back
            self.repository.save_all(deposits)
            
            # Count actual updates
            updated_count = sum(
                1 for d in deposits 
                if d.balance != original_balances[d.id]
            )
            
            return UpdateBalancesResponse(
                success=True,
                message=f"Successfully updated {updated_count} time deposit balances",
                updated_count=updated_count
            )
            
        except Exception as e:
            logger.error(f"Error updating balances: {str(e)}")
            raise ServiceException(f"Failed to update balances: {str(e)}")
    
    def get_all_deposits(self) -> List[TimeDepositResponse]:
        """
        Get all deposits with withdrawals formatted for API response.
        """
        try:
            # Get deposits with withdrawals as domain entities
            deposits = self.repository.get_all_with_withdrawals()
            
            # Convert to response format
            responses = []
            for deposit in deposits:
                # Convert withdrawals
                withdrawal_responses = [
                    WithdrawalResponse(
                        id=w.id,
                        amount=Decimal(str(w.amount)),
                        date=datetime.fromisoformat(w.date).date()
                    )
                    for w in deposit.withdrawals
                ]
                
                # Create deposit response
                response = TimeDepositResponse(
                    id=deposit.id,
                    planType=deposit.planType,
                    balance=Decimal(str(deposit.balance)),
                    days=deposit.days,
                    withdrawals=withdrawal_responses
                )
                responses.append(response)
            
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

class ValidationException(ServiceException):
    """Exception for validation failures"""
    pass
```### Step 4: Create Dependency Injection Setup (10 min)

```python
# app/application/dependencies.py
from sqlalchemy.orm import Session
from app.infrastructure.database.connection import get_db
from app.infrastructure.database.repositories.time_deposit_repository import TimeDepositRepository
from app.infrastructure.adapters.time_deposit_repository_adapter import TimeDepositRepositoryAdapter
from app.application.services.time_deposit_service import TimeDepositService

def get_time_deposit_service(db: Session = Depends(get_db)) -> TimeDepositService:
    """
    Dependency injection factory for time deposit service.
    
    Flow:
    1. Get database session
    2. Create infrastructure repository
    3. Wrap in adapter (handles conversions)
    4. Create service with adapter
    """
    sql_repository = TimeDepositRepository(db)
    adapter = TimeDepositRepositoryAdapter(sql_repository)
    return TimeDepositService(adapter)
```

### Step 5: Integration Testing (10 min)

```python
# tests/application/test_service_integration.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decimal import Decimal

from app.infrastructure.database.models import Base, TimeDepositModel
from app.infrastructure.database.repositories.time_deposit_repository import TimeDepositRepository
from app.infrastructure.adapters.time_deposit_repository_adapter import TimeDepositRepositoryAdapter
from app.application.services.time_deposit_service import TimeDepositService

class TestServiceIntegration:
    
    @pytest.fixture
    def test_db(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        return SessionLocal()
    
    @pytest.fixture
    def service(self, test_db):
        sql_repo = TimeDepositRepository(test_db)
        adapter = TimeDepositRepositoryAdapter(sql_repo)
        return TimeDepositService(adapter)
    
    def test_full_update_workflow(self, service, test_db):
        # Create test data
        deposits = [
            TimeDepositModel(planType="basic", balance=Decimal("1000.00"), days=45),
            TimeDepositModel(planType="student", balance=Decimal("2000.00"), days=90)
        ]
        test_db.add_all(deposits)
        test_db.commit()
        
        # Update balances
        result = service.update_all_balances()
        
        # Verify
        assert result.success is True
        assert result.updated_count > 0
```

---

## 🔧 Key Integration Considerations

### 1. **Leverage Existing Adapter**
The codebase already has `TimeDepositRepositoryAdapter` that handles:
- Model → Domain conversion (Decimal → float)
- Domain → Model conversion (float → Decimal)
- Withdrawal relationship handling

### 2. **Preserve Domain Logic**
- The `TimeDepositCalculator` has UNUSUAL cumulative interest logic
- Interest accumulates across ALL deposits
- Same cumulative interest applied to EACH deposit
- This MUST be preserved exactly

### 3. **Type Conversions**
- Database uses `Decimal` for money
- Domain uses `float` (from original code)
- Adapter handles conversions automatically

### 4. **Schema Requirements**
- API must return `planType` (not `plan_type`)
- Exact field names must match requirements
- Withdrawals array must be included

---

## 📋 Implementation Checklist

### Directory Structure:
- [ ] Create `app/application/` directory
- [ ] Create subdirectories (services, schemas, exceptions)
- [ ] Add all `__init__.py` files

### Code Implementation:
- [ ] Create Pydantic schemas with EXACT field names
- [ ] Implement service using existing repository interface
- [ ] Add exception classes
- [ ] Create dependency injection setup

### Integration:
- [ ] Service uses `TimeDepositRepositoryInterface` (not concrete)
- [ ] Inject `TimeDepositRepositoryAdapter` (handles conversions)
- [ ] Test with existing database models

### Testing:
- [ ] Unit tests with mocked repository
- [ ] Integration tests with in-memory database
- [ ] Verify cumulative interest calculation preserved

---

## 🚀 Commands to Execute

```bash
# 1. Navigate to project
cd C:\Users\prasa\Code\ikigai-take-home-assignment\Python\fastapi

# 2. Create application structure
mkdir app\application app\application\services app\application\schemas app\application\exceptions

# 3. Create files
# (Copy implementations from this plan)

# 4. Run tests
python -m pytest tests/application/ -v

# 5. Test integration
python -m pytest tests/application/test_service_integration.py -v
```

---

## ⚠️ Critical Success Factors

1. **NO CHANGES** to `TimeDepositCalculator.update_balance` method
2. **USE EXISTING** `TimeDepositRepositoryAdapter` for conversions
3. **EXACT SCHEMA** - field names must match (planType, not plan_type)
4. **PRESERVE** the unusual cumulative interest calculation logic
5. **LEVERAGE** existing infrastructure and domain layers

This refined plan integrates seamlessly with your existing codebase structure! 🎯