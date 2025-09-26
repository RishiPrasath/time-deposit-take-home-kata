# Phase 2 Implementation Canvas
## Domain Layer Integration with Existing FastAPI Codebase

### 🎯 **OBJECTIVE**
Add Domain Layer (Phase 2) to existing FastAPI infrastructure without breaking changes, preserving exact business logic from original codebase.

---

## 📋 **CURRENT STATE ANALYSIS**

### **✅ What's Already Implemented (Phase 1):**
```
C:\Users\prasa\Code\ikigai-take-home-assignment\Python\fastapi\
├── app\
│   └── infrastructure\
│       ├── config\
│       └── database\
│           ├── connection.py
│           ├── models.py            ✅ TimeDepositModel, WithdrawalModel
│           └── repositories\
│               └── time_deposit_repository.py  ✅ SqlAlchemy repository
├── migrations\                      ✅ Database migrations
├── tests\                          ✅ Test infrastructure
├── docker-compose.yml              ✅ PostgreSQL setup
└── requirements.txt                ✅ Dependencies
```

### **🔍 Infrastructure Analysis:**
- ✅ **Database Models**: `TimeDepositModel`, `WithdrawalModel` exist
- ✅ **Repository**: `TimeDepositRepository` with CRUD operations
- ✅ **Database Setup**: PostgreSQL + SQLAlchemy configured
- ❌ **Missing**: Domain layer, business logic, integration bridge

---

## 🛠️ **IMPLEMENTATION PLAN**

### **📁 NEW FOLDER STRUCTURE TO CREATE**

```
app\
├── infrastructure\          ✅ EXISTS
│   └── adapters\            🆕 CREATE - Integration bridge
│       ├── __init__.py
│       └── time_deposit_repository_adapter.py
├── domain\                  🆕 CREATE - Business logic layer
│   ├── __init__.py
│   ├── entities\
│   │   ├── __init__.py
│   │   ├── time_deposit.py  🆕 EXACT copy from original
│   │   └── withdrawal.py
│   ├── interfaces\
│   │   ├── __init__.py
│   │   └── repositories.py  🆕 Abstract interfaces
│   └── value_objects\
│       ├── __init__.py
│       └── plan_types.py
└── application\             🔜 PHASE 3 - Services layer
    └── services\
```

---

## 🚀 **STEP-BY-STEP IMPLEMENTATION**

### **STEP 1: Create Domain Entities (15 minutes)**

#### **1.1 Copy Original TimeDeposit Logic**
```bash
# Create domain structure
mkdir app\domain
mkdir app\domain\entities
mkdir app\domain\interfaces
mkdir app\domain\value_objects
```

#### **1.2 Create: `app\domain\entities\time_deposit.py`**
```python
"""
CRITICAL: EXACT COPY from original codebase - NO MODIFICATIONS
Source: C:\Users\prasa\OneDrive\Documents\GitHub\time-deposit-take-home-kata\exisiting codebase\python\time_deposit.py
"""

class TimeDeposit:
    """
    Original TimeDeposit entity - PRESERVED EXACTLY
    
    ⚠️ ZERO CHANGES ALLOWED - This must match original behavior exactly
    """
    def __init__(self, id, planType, balance, days):
        self.id = id
        self.planType = planType
        self.balance = balance
        self.days = days
        # Note: Original doesn't have withdrawals property!
        # We'll add it for API requirements but keep constructor unchanged
        self.withdrawals = []

class TimeDepositCalculator:
    """
    Original business logic - PRESERVED EXACTLY
    
    ⚠️ CRITICAL: This has unusual cumulative interest behavior that MUST be preserved
    - Interest accumulates across ALL deposits
    - Same cumulative interest applied to EACH deposit  
    - Monthly rates (annual rate / 12)
    - Specific day thresholds and conditions
    """
    
    def update_balance(self,xs):
        """
        EXACT COPY - NO MODIFICATIONS WHATSOEVER
        
        Unusual behavior (but must be preserved):
        1. Calculates cumulative interest across ALL deposits
        2. Applies same cumulative interest to EACH individual deposit
        3. Uses monthly rates (annual / 12)
        4. Specific conditions for each plan type
        """
        interest = 0
        for td in xs:
            if td.days > 30:
                if td.planType == 'student':
                    if td.days < 366:
                        interest += (td.balance * 0.03)/12
                elif td.planType == 'premium':
                    if td.days > 45:
                        interest += (td.balance * 0.05)/12
                elif td.planType == 'basic':
                    interest += (td.balance * 0.01) / 12
            td.balance = round(td.balance + ((interest * 100) / 100), 2)
```

#### **1.3 Create: `app\domain\entities\withdrawal.py`**
```python
"""
Withdrawal entity for API requirements
"""

class Withdrawal:
    """
    Withdrawal entity for managing withdrawal data
    
    Used for API response formatting but not part of original business logic
    """
    def __init__(self, id: int, amount: float, date: str):
        self.id = id
        self.amount = amount
        self.date = date
    
    def __repr__(self):
        return f"Withdrawal(id={self.id}, amount={self.amount}, date='{self.date}')"
```

#### **1.4 Create: `app\domain\value_objects\plan_types.py`**
```python
"""
Plan type enumeration for type safety
"""
from enum import Enum

class PlanType(Enum):
    """Valid time deposit plan types"""
    BASIC = "basic"
    STUDENT = "student"  
    PREMIUM = "premium"
    
    @classmethod
    def is_valid(cls, plan_type: str) -> bool:
        """Check if plan type is valid"""
        return plan_type in [pt.value for pt in cls]
```

### **STEP 2: Create Domain Interfaces (10 minutes)**

#### **2.1 Create: `app\domain\interfaces\repositories.py`**
```python
"""
Abstract repository interface for dependency inversion
"""
from abc import ABC, abstractmethod
from typing import List
from app.domain.entities.time_deposit import TimeDeposit

class TimeDepositRepositoryInterface(ABC):
    """
    Abstract interface for time deposit repository operations
    
    This interface decouples the domain layer from infrastructure,
    allowing different implementations (database, memory, etc.)
    """
    
    @abstractmethod
    def get_all(self) -> List[TimeDeposit]:
        """
        Get all time deposits as domain entities
        
        Returns:
            List of TimeDeposit domain objects
        """
        pass
    
    @abstractmethod
    def get_all_with_withdrawals(self) -> List[TimeDeposit]:
        """
        Get all time deposits with their withdrawals loaded
        
        Returns:
            List of TimeDeposit domain objects with withdrawals populated
        """
        pass
    
    @abstractmethod
    def save_all(self, deposits: List[TimeDeposit]) -> None:
        """
        Save all time deposits back to persistence layer
        
        Args:
            deposits: List of TimeDeposit domain objects to save
        """
        pass
    
    @abstractmethod
    def create_sample_data(self) -> None:
        """
        Create sample data for testing and development
        """
        pass
```

### **STEP 3: Create Integration Adapter (20 minutes)**

#### **3.1 Create: `app\infrastructure\adapters\__init__.py`**
```python
"""
Infrastructure adapters for integrating with domain layer
"""
```

#### **3.2 Create: `app\infrastructure\adapters\time_deposit_repository_adapter.py`**
```python
"""
🌉 CRITICAL INTEGRATION BRIDGE

This adapter converts between:
- Infrastructure layer (SQLAlchemy models) 
- Domain layer (Pure Python objects)

This is THE KEY to preserving existing business logic while adding database persistence.
"""
from typing import List
from decimal import Decimal
from datetime import date

from app.domain.interfaces.repositories import TimeDepositRepositoryInterface
from app.domain.entities.time_deposit import TimeDeposit
from app.domain.entities.withdrawal import Withdrawal
from app.infrastructure.database.repositories.time_deposit_repository import TimeDepositRepository
from app.infrastructure.database.models import TimeDepositModel, WithdrawalModel

class TimeDepositRepositoryAdapter(TimeDepositRepositoryInterface):
    """
    🌉 INTEGRATION ADAPTER: Connects Infrastructure ↔ Domain
    
    This adapter:
    1. Implements domain repository interface
    2. Uses infrastructure repository internally
    3. Converts between SQLAlchemy models and domain entities
    4. Preserves exact business logic behavior
    
    ⚠️ CRITICAL: All conversions must preserve data integrity and types
    """
    
    def __init__(self, sql_repository: TimeDepositRepository):
        """
        Initialize with infrastructure repository
        
        Args:
            sql_repository: The SQLAlchemy-based repository from Phase 1
        """
        self._sql_repo = sql_repository
    
    def get_all(self) -> List[TimeDeposit]:
        """
        Get all time deposits as domain entities
        
        Flow: Database → SQLAlchemy Models → Domain Entities
        """
        try:
            models = self._sql_repo.get_all()
            return [self._model_to_domain(model) for model in models]
        except Exception as e:
            raise Exception(f"Failed to get all time deposits: {str(e)}")
    
    def get_all_with_withdrawals(self) -> List[TimeDeposit]:
        """
        Get all time deposits with withdrawals as domain entities
        
        Flow: Database → SQLAlchemy Models (with joins) → Domain Entities (with withdrawals)
        """
        try:
            models = self._sql_repo.get_all_with_withdrawals()
            return [self._model_to_domain_with_withdrawals(model) for model in models]
        except Exception as e:
            raise Exception(f"Failed to get time deposits with withdrawals: {str(e)}")
    
    def save_all(self, deposits: List[TimeDeposit]) -> None:
        """
        Save domain entities back to database
        
        Flow: Domain Entities → SQLAlchemy Models → Database
        
        ⚠️ CRITICAL: Must handle balance updates from TimeDepositCalculator
        """
        try:
            models = [self._domain_to_model(deposit) for deposit in deposits]
            self._sql_repo.save_all_models(models)
        except Exception as e:
            raise Exception(f"Failed to save time deposits: {str(e)}")
    
    def create_sample_data(self) -> None:
        """
        Create sample data using infrastructure repository
        """
        try:
            self._sql_repo.create_sample_data()
        except Exception as e:
            raise Exception(f"Failed to create sample data: {str(e)}")
    
    # 🔄 CONVERSION METHODS - THE CRITICAL INTEGRATION LOGIC
    
    def _model_to_domain(self, model: TimeDepositModel) -> TimeDeposit:
        """
        Convert SQLAlchemy model to domain entity
        
        ⚠️ CRITICAL CONVERSIONS:
        - Decimal → float (for business logic compatibility)
        - Database ID → domain ID
        - Preserve all original field types and names
        """
        return TimeDeposit(
            id=model.id,
            planType=model.planType,  # Already string
            balance=float(model.balance),  # Convert Decimal to float for original logic
            days=model.days  # Already int
        )
    
    def _model_to_domain_with_withdrawals(self, model: TimeDepositModel) -> TimeDeposit:
        """
        Convert SQLAlchemy model to domain entity WITH withdrawals
        
        ⚠️ CRITICAL: Properly handles relationship data
        """
        # Start with base conversion
        domain = self._model_to_domain(model)
        
        # Add withdrawals if they exist
        if model.withdrawals:
            for withdrawal_model in model.withdrawals:
                withdrawal = Withdrawal(
                    id=withdrawal_model.id,
                    amount=float(withdrawal_model.amount),  # Convert Decimal to float
                    date=withdrawal_model.date.isoformat()  # Convert Date to ISO string
                )
                domain.withdrawals.append(withdrawal)
        
        return domain
    
    def _domain_to_model(self, domain: TimeDeposit) -> TimeDepositModel:
        """
        Convert domain entity to SQLAlchemy model
        
        ⚠️ CRITICAL: Must handle updated balances from TimeDepositCalculator
        This is where calculated interest gets persisted back to database
        """
        # Get existing model if it exists (for updates)
        existing_model = None
        if domain.id:
            try:
                existing_model = self._sql_repo.db.query(TimeDepositModel).filter(
                    TimeDepositModel.id == domain.id
                ).first()
            except:
                pass
        
        if existing_model:
            # Update existing model with potentially changed balance
            existing_model.balance = Decimal(str(domain.balance))  # Convert float back to Decimal
            existing_model.planType = domain.planType
            existing_model.days = domain.days
            return existing_model
        else:
            # Create new model
            return TimeDepositModel(
                id=domain.id,
                planType=domain.planType,
                days=domain.days,
                balance=Decimal(str(domain.balance))  # Convert float to Decimal for database
            )
```

### **STEP 4: Update Existing Infrastructure (5 minutes)**

#### **4.1 Add method to existing repository: `app\infrastructure\database\repositories\time_deposit_repository.py`**

Add this method to the existing `TimeDepositRepository` class:

```python
def save_all_models(self, models: List[TimeDepositModel]) -> None:
    """
    Save all models back to database
    
    Used by adapter to persist domain entity changes
    """
    try:
        for model in models:
            # Merge handles both updates and inserts
            self.db.merge(model)
        self.db.commit()
    except SQLAlchemyError as e:
        self.db.rollback()
        raise Exception(f"Failed to save time deposit models: {str(e)}")
```

---

## 🧪 **TESTING PHASE 2 IMPLEMENTATION**

### **TEST 1: Domain Logic Preservation**
```bash
# Create test file: tests\domain\test_time_deposit_business_logic.py
```

```python
"""
CRITICAL TESTS: Verify no breaking changes to original business logic
"""
import pytest
from app.domain.entities.time_deposit import TimeDeposit, TimeDepositCalculator

def test_exact_original_behavior_basic():
    """Test basic plan matches original logic exactly"""
    deposits = [TimeDeposit(1, "basic", 1000.0, 45)]
    calculator = TimeDepositCalculator()
    
    calculator.update_balance(deposits)
    
    # Expected: interest = (1000.0 * 0.01) / 12 = 0.8333...
    # balance = round(1000.0 + ((0.8333... * 100) / 100), 2)
    expected_interest = (1000.0 * 0.01) / 12
    expected_balance = round(1000.0 + ((expected_interest * 100) / 100), 2)
    
    assert deposits[0].balance == expected_balance
    print(f"✅ Basic plan: {1000.0} → {deposits[0].balance}")

def test_cumulative_interest_behavior():
    """Test the unusual cumulative interest behavior is preserved"""
    deposits = [
        TimeDeposit(1, "basic", 1000.0, 45),      # Contributes: (1000 * 0.01)/12 = 0.833
        TimeDeposit(2, "student", 2000.0, 180),   # Contributes: (2000 * 0.03)/12 = 5.0  
        TimeDeposit(3, "premium", 3000.0, 60)     # Contributes: (3000 * 0.05)/12 = 12.5
    ]
    calculator = TimeDepositCalculator()
    
    calculator.update_balance(deposits)
    
    # Total interest = 0.833 + 5.0 + 12.5 = 18.333
    # Each deposit gets this SAME amount added!
    cumulative_interest = (1000.0 * 0.01)/12 + (2000.0 * 0.03)/12 + (3000.0 * 0.05)/12
    interest_addition = (cumulative_interest * 100) / 100
    
    # All balances should increase by same amount (the unusual behavior)
    assert deposits[0].balance == round(1000.0 + interest_addition, 2)
    assert deposits[1].balance == round(2000.0 + interest_addition, 2) 
    assert deposits[2].balance == round(3000.0 + interest_addition, 2)
    
    print(f"✅ Cumulative interest preserved: {cumulative_interest}")
```

### **TEST 2: Integration Bridge**
```bash
# Create test file: tests\integration\test_domain_infrastructure_bridge.py
```

```python
"""
Integration tests for Phase 1 ↔ Phase 2 bridge
"""
import pytest
from decimal import Decimal
from app.infrastructure.database.models import TimeDepositModel
from app.infrastructure.adapters.time_deposit_repository_adapter import TimeDepositRepositoryAdapter
from app.domain.entities.time_deposit import TimeDeposit, TimeDepositCalculator

def test_model_to_domain_conversion():
    """Test SQLAlchemy model converts correctly to domain entity"""
    # Create SQLAlchemy model (Phase 1)
    model = TimeDepositModel(
        id=1,
        planType="basic",
        balance=Decimal("1000.00"),
        days=45
    )
    
    # Convert via adapter
    adapter = TimeDepositRepositoryAdapter(mock_sql_repo)
    domain = adapter._model_to_domain(model)
    
    # Verify domain entity
    assert isinstance(domain, TimeDeposit)
    assert domain.id == 1
    assert domain.planType == "basic"
    assert domain.balance == 1000.0  # Decimal → float
    assert domain.days == 45

def test_business_logic_with_database_data():
    """Test that original business logic works with database-sourced data"""
    # This is the CRITICAL integration test
    pass  # Implementation depends on your test database setup
```

---

## ✅ **VALIDATION CHECKLIST**

### **Before Proceeding to Phase 3:**

- [ ] **Domain entities created**: `time_deposit.py`, `withdrawal.py`
- [ ] **Interfaces defined**: Abstract repository interface 
- [ ] **Adapter implemented**: Converts between models and entities
- [ ] **No breaking changes**: Original `TimeDepositCalculator` works exactly as before
- [ ] **Integration tests pass**: Data flows correctly between layers
- [ ] **Business logic tests pass**: All interest calculations work correctly
- [ ] **Cumulative interest preserved**: Unusual behavior maintained exactly

### **Validation Commands:**
```bash
# Test domain logic
python -m pytest tests/domain/ -v

# Test integration
python -m pytest tests/integration/ -v

# Quick business logic check
python -c "
from app.domain.entities.time_deposit import TimeDeposit, TimeDepositCalculator
deposits = [TimeDeposit(1, 'basic', 1000.0, 45)]
calc = TimeDepositCalculator()
calc.update_balance(deposits)
print(f'✅ Balance after interest: {deposits[0].balance}')
"
```

---

## 🎯 **SUCCESS CRITERIA**

**Phase 2 is complete when:**

1. **✅ Domain Layer Exists**: Clean domain entities and interfaces
2. **✅ Integration Bridge Works**: Adapter converts data correctly  
3. **✅ Business Logic Preserved**: Original calculator works identically
4. **✅ Database Integration**: Domain changes persist to database
5. **✅ Tests Pass**: All domain and integration tests successful
6. **✅ No Breaking Changes**: Existing behavior 100% preserved

**Next**: Phase 3 will create Application Services that use the Domain Repository Interface (without knowing about database details) to orchestrate business workflows for the API endpoints.

---

## 🚨 **CRITICAL REMINDERS**

1. **ZERO modifications** to `TimeDepositCalculator.update_balance` method
2. **EXACT preservation** of unusual cumulative interest behavior  
3. **Proper data type conversions** (Decimal ↔ float, Date ↔ string)
4. **Test everything** before moving to Phase 3
5. **The adapter is the ONLY place** that knows about both infrastructure and domain

**The goal is to add database persistence WITHOUT changing the original business logic!** 🛡️

## 🚨 Critical Analysis of Existing Logic

**The existing `update_balance` method has UNUSUAL behavior that must be preserved:**

### **🔍 Key Behavior Patterns:**

1. **Cumulative Interest Across All Deposits**: 
   ```python
   interest = 0  # Global variable across ALL deposits
   for td in xs:
       # Interest accumulates for ALL deposits
       if conditions_met:
           interest += (td.balance * rate)/12
   ```

2. **Same Interest Applied to Each Deposit**:
   ```python
   # EVERY deposit gets the SAME cumulative interest amount added!
   td.balance = round(td.balance + ((interest * 100) / 100), 2)
   ```

3. **Monthly Interest Calculation**: All rates divided by 12
   - Basic: `(balance * 0.01) / 12` per month
   - Student: `(balance * 0.03) / 12` per month  
   - Premium: `(balance * 0.05) / 12` per month

4. **Specific Day Thresholds**:
   - Basic: `days > 30`
   - Student: `days > 30 AND days < 366` (exactly 365 days max)
   - Premium: `days > 30 AND days > 45` (must be > 45, not >= 45)

5. **Rounding**: `round(balance + interest, 2)` for 2 decimal places

### **🚨 Unusual Consequence:**
If you have 3 deposits that all qualify for interest, **each deposit gets the SUM of all three interest calculations added to its balance!** This creates a compound effect across deposits.

**Example:**
- Deposit A (basic, $1000): generates $0.83 interest
- Deposit B (student, $2000): generates $5.00 interest  
- Deposit C (premium, $3000): generates $12.50 interest
- **Total interest = $18.33**
- **EACH deposit gets $18.33 added to its balance!**
- Final balances: $1018.33, $2018.33, $3018.33

This might be a bug in the original code, but **WE MUST PRESERVE IT EXACTLY!**
