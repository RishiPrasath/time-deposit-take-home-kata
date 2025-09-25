# FastAPI Time Deposit Implementation Plan
## Bottom-Up Approach: Infrastructure → Domain → Application → API

### 🎯 Implementation Strategy Analysis

**Your Proposed Approach**: Start from Infrastructure Layer and work UP to API Layer

```
🏗️ IMPLEMENTATION ORDER (Bottom-Up)
┌─────────────────────────────────────────┐
│ 1️⃣ INFRASTRUCTURE LAYER (Foundation)    │
│  • Database setup, models, repositories │
│  • Test database operations             │
└─────────────────────────────────────────┘
                    ⬇️
┌─────────────────────────────────────────┐
│ 2️⃣ DOMAIN LAYER (Business Logic)        │
│  • Copy existing classes               │
│  • Create interfaces                   │
│  • Test business logic                 │
└─────────────────────────────────────────┘
                    ⬇️
┌─────────────────────────────────────────┐
│ 3️⃣ APPLICATION LAYER (Orchestration)    │
│  • Services and use cases              │
│  • API schemas (Pydantic models)       │
│  • Test service workflows              │
└─────────────────────────────────────────┘
                    ⬇️
┌─────────────────────────────────────────┐
│ 4️⃣ API LAYER (HTTP Interface)           │
│  • FastAPI endpoints                   │
│  • Request/response handling           │
│  • Integration tests                   │
└─────────────────────────────────────────┘
```

---

## ✅ FEASIBILITY ANALYSIS

### **🎯 Is This Approach Feasible? ABSOLUTELY YES!**

**Advantages of Bottom-Up Implementation:**

1. **Solid Foundation First** 🏗️
   - Database layer is the most critical dependency
   - All other layers depend on data persistence
   - Catch database issues early

2. **Incremental Testing** 🧪
   - Test each layer independently as you build
   - Easier to isolate and fix problems
   - Build confidence layer by layer

3. **Natural Dependency Flow** 🔄
   - Each layer builds on the previous one
   - No circular dependencies
   - Clear progression path

4. **Early Problem Detection** 🔍
   - Database connection issues found first
   - Schema problems caught early
   - Performance issues identified upfront

### **🚨 Potential Challenges & Solutions:**

| Challenge | Impact | Solution |
|-----------|---------|----------|
| Can't test API until end | Medium | Use database tests + mock services |
| Hard to visualize progress | Low | Create test scripts for each layer |
| Database schema changes | Medium | Use migrations from start |
| Integration complexity | Medium | Test layer interfaces thoroughly |

---

## 🛠️ DETAILED IMPLEMENTATION PLAN

### **Phase 1: Infrastructure Layer (Foundation) - 90 minutes**

#### **1.1 Environment Setup (20 minutes)**
```bash
# Project structure creation
C:\Users\prasa\Code\ikigai-take-home-assignment\Python\fastapi\
├── app/
│   └── infrastructure/
│       ├── __init__.py
│       ├── database/
│       │   ├── __init__.py
│       │   ├── connection.py
│       │   ├── models.py
│       │   └── repositories/
│       │       ├── __init__.py
│       │       └── time_deposit_repository.py
│       └── config/
│           ├── __init__.py
│           └── settings.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── infrastructure/
│       ├── __init__.py
│       └── test_time_deposit_repository.py
├── migrations/
├── docker-compose.yml
├── requirements.txt
└── .env
```

**Deliverables:**
- Project folder structure
- Dependencies installed (FastAPI, SQLAlchemy, PostgreSQL)
- Docker setup with PostgreSQL container

**Testing Strategy:**
- Test database connection
- Verify Docker containers start correctly

#### **1.2 Database Models (30 minutes)**
```python
# app/infrastructure/database/models.py
class TimeDepositModel(Base):
    __tablename__ = "timeDeposits"
    # Exact schema matching requirements
    
class WithdrawalModel(Base):
    __tablename__ = "withdrawals" 
    # With foreign key relationships
```

**Deliverables:**
- SQLAlchemy models matching exact schema
- Relationship configurations (1:N)
- Database migration scripts

**Testing Strategy:**
- Test model creation
- Test relationships work correctly
- Test constraints are enforced

#### **1.3 Repository Implementation (40 minutes)**
```python
# app/infrastructure/database/repositories/time_deposit_repository.py
class TimeDepositRepository:
    def get_all(self) -> List[TimeDepositModel]
    def get_all_with_withdrawals(self) -> List[TimeDepositModel]
    def save_all(self, deposits: List[TimeDepositModel])
    def create_sample_data(self)  # For testing
```

**Deliverables:**
- Complete repository implementation
- CRUD operations for time deposits
- Sample data creation methods

**Testing Strategy:**
```python
# tests/infrastructure/test_time_deposit_repository.py
def test_create_time_deposit()
def test_get_all_deposits()
def test_get_with_withdrawals()
def test_update_balances()
def test_foreign_key_constraints()
```

#### **Phase 1 Success Criteria:**
- [ ] Database connection established
- [ ] Models create tables correctly
- [ ] Repository operations work
- [ ] Sample data can be inserted/retrieved
- [ ] All infrastructure tests pass

---

### **Phase 2: Domain Layer (Business Logic) - 30 minutes**

#### **2.1 Copy Existing Classes (15 minutes)**
```python
# app/domain/entities/time_deposit.py
# EXACT COPY - NO MODIFICATIONS
class TimeDeposit:
    def __init__(self, id, planType, balance, days):
        # Original implementation preserved

class TimeDepositCalculator:
    def update_balance(self, xs):
        # Original algorithm preserved exactly
```

**Deliverables:**
- Domain entities (exact copies)
- No breaking changes to existing logic
- Clean separation from infrastructure

**Testing Strategy:**
```python
# tests/domain/test_time_deposit.py
def test_time_deposit_creation()
def test_calculator_basic_plan()
def test_calculator_student_plan()
def test_calculator_premium_plan()
def test_calculator_edge_cases()
```

#### **2.2 Repository Interfaces (15 minutes)**
```python
# app/domain/interfaces/repositories.py
from abc import ABC, abstractmethod

class TimeDepositRepositoryInterface(ABC):
    @abstractmethod
    def get_all(self) -> List[TimeDeposit]: pass
    
    @abstractmethod
    def save_all(self, deposits: List[TimeDeposit]): pass
```

**Deliverables:**
- Abstract interfaces for dependency inversion
- Clear contracts for repository operations
- Foundation for testability

#### **Phase 2 Success Criteria:**
- [ ] Existing business logic preserved
- [ ] Domain tests pass (proving no breaking changes)
- [ ] Interfaces defined for next layer
- [ ] Clean separation of concerns maintained

---

### **Phase 3: Application Layer (Orchestration) - 60 minutes**

#### **3.1 Service Layer Implementation (40 minutes)**
```python
# app/application/services/time_deposit_service.py
class TimeDepositService:
    def __init__(self, repository: TimeDepositRepositoryInterface):
        self.repository = repository
    
    def update_all_balances(self) -> dict:
        """Workflow: Get → Calculate → Save"""
        # 1. Get all deposits from repository
        # 2. Convert to domain entities
        # 3. Apply TimeDepositCalculator logic
        # 4. Convert back and save
        # 5. Return operation result
    
    def get_all_deposits(self) -> List[dict]:
        """Workflow: Get → Format → Return"""
        # 1. Get all deposits with withdrawals
        # 2. Convert to API format
        # 3. Return structured data
```

**Deliverables:**
- Business workflow orchestration
- Integration between domain and infrastructure
- Data transformation logic

**Testing Strategy:**
```python
# tests/application/test_time_deposit_service.py
def test_update_all_balances_success()
def test_update_all_balances_no_deposits()
def test_get_all_deposits_with_withdrawals()
def test_get_all_deposits_empty_database()
def test_service_error_handling()
```

#### **3.2 API Schemas (20 minutes)**
```python
# app/application/schemas/time_deposit.py
from pydantic import BaseModel
from typing import List
from decimal import Decimal
from datetime import date

class WithdrawalResponse(BaseModel):
    id: int
    amount: Decimal
    date: date

class TimeDepositResponse(BaseModel):
    id: int
    planType: str
    balance: Decimal
    days: int
    withdrawals: List[WithdrawalResponse]

class UpdateBalancesResponse(BaseModel):
    success: bool
    message: str
    updated_count: int
```

**Deliverables:**
- Pydantic models for API responses
- Exact schema matching requirements
- Data validation and serialization

#### **Phase 3 Success Criteria:**
- [ ] Service workflows work correctly
- [ ] Data flows between layers properly
- [ ] Business logic integration successful
- [ ] Response schemas match requirements
- [ ] All application tests pass

---

### **Phase 4: API Layer (HTTP Interface) - 45 minutes**

#### **4.1 FastAPI Application Setup (15 minutes)**
```python
# app/main.py
from fastapi import FastAPI
from app.api.v1.api import api_router

app = FastAPI(
    title="Time Deposit Management System",
    description="Ikigai Digital Take-Home Assignment",
    version="1.0.0"
)

app.include_router(api_router, prefix="/api/v1")
```

**Deliverables:**
- FastAPI application instance
- Router configuration
- API documentation setup

#### **4.2 Endpoint Implementation (30 minutes)**
```python
# app/api/v1/endpoints/time_deposits.py
from fastapi import APIRouter, Depends, HTTPException
from app.application.services.time_deposit_service import TimeDepositService

router = APIRouter()

@router.put("/time-deposits/balances")
async def update_all_time_deposit_balances(
    service: TimeDepositService = Depends(get_time_deposit_service)
):
    """Update balances for ALL time deposits in database"""
    try:
        result = service.update_all_balances()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/time-deposits")
async def get_all_time_deposits(
    service: TimeDepositService = Depends(get_time_deposit_service)
):
    """Returns array of time deposits with exact schema"""
    try:
        deposits = service.get_all_deposits()
        return deposits
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Deliverables:**
- 2 required API endpoints (no more, no less)
- Proper HTTP methods (PUT, GET)
- Error handling and status codes
- Dependency injection setup

**Testing Strategy:**
```python
# tests/api/test_endpoints.py
def test_update_balances_endpoint()
def test_get_all_deposits_endpoint()
def test_endpoint_error_handling()
def test_response_formats()
def test_integration_end_to_end()
```

#### **Phase 4 Success Criteria:**
- [ ] Both endpoints working correctly
- [ ] Exact API response format
- [ ] Error handling implemented
- [ ] Integration tests pass
- [ ] End-to-end workflow successful

---

## 🧪 TESTING STRATEGY PER LAYER

### **Layer-by-Layer Testing Approach:**

#### **Infrastructure Layer Tests:**
```python
# Can run immediately after implementing repositories
pytest tests/infrastructure/ -v

# Tests database operations without needing upper layers
def test_database_connection()
def test_create_time_deposits()
def test_query_with_joins()
def test_transaction_handling()
```

#### **Domain Layer Tests:**
```python
# Tests business logic in isolation
pytest tests/domain/ -v

# Verifies no breaking changes to existing logic
def test_existing_calculator_behavior()
def test_interest_calculation_rules()
def test_edge_cases_preserved()
```

#### **Application Layer Tests:**
```python
# Uses mock repositories to test service logic
pytest tests/application/ -v

# Tests orchestration without database dependency
def test_service_workflows()
def test_data_transformations()
def test_error_handling()
```

#### **API Layer Tests:**
```python
# Full integration tests
pytest tests/api/ -v

# Tests complete request/response cycle
def test_actual_http_endpoints()
def test_real_database_integration()
def test_end_to_end_workflows()
```

---

## ⚡ IMPLEMENTATION TIMELINE

| Phase | Duration | Cumulative | Key Milestone |
|-------|----------|------------|---------------|
| Infrastructure | 90 min | 1.5h | ✅ Database working |
| Domain | 30 min | 2h | ✅ Business logic preserved |
| Application | 60 min | 3h | ✅ Services orchestrating |
| API | 45 min | 3.75h | ✅ Endpoints responding |
| **Integration Testing** | 45 min | 4.5h | ✅ End-to-end working |
| **Documentation** | 30 min | 5h | ✅ Production ready |

**Total: 5 hours** (faster than original 6.75h estimate due to focused approach)

---

## 🎯 VALIDATION AT EACH PHASE

### **Phase 1 Validation (Infrastructure):**
```bash
# Start PostgreSQL container
docker-compose up postgres -d

# Run database tests
python -m pytest tests/infrastructure/ -v

# Validate sample data creation
python scripts/create_sample_data.py

# Expected Results:
# ✅ Tables created successfully
# ✅ Sample data inserted
# ✅ Repository operations work
# ✅ Relationships function correctly
```

### **Phase 2 Validation (Domain):**
```bash
# Test existing business logic preservation
python -m pytest tests/domain/ -v

# Run specific calculator tests
python -c "
from app.domain.entities.time_deposit import TimeDeposit, TimeDepositCalculator
deposits = [TimeDeposit(1, 'basic', 1000.0, 45)]
calc = TimeDepositCalculator()
calc.update_balance(deposits)
print(f'Balance after interest: {deposits[0].balance}')
"

# Expected Results:
# ✅ All domain tests pass
# ✅ Interest calculations work
# ✅ No breaking changes detected
```

### **Phase 3 Validation (Application):**
```bash
# Test service layer workflows
python -m pytest tests/application/ -v

# Test service integration with mocked repository
python scripts/test_service_workflows.py

# Expected Results:
# ✅ Services orchestrate correctly
# ✅ Data transformations work
# ✅ Business workflows complete
```

### **Phase 4 Validation (API):**
```bash
# Start full application
uvicorn app.main:app --reload --port 8000

# Test endpoints manually
curl -X PUT "http://localhost:8000/api/v1/time-deposits/balances"
curl "http://localhost:8000/api/v1/time-deposits"

# Run integration tests
python -m pytest tests/api/ -v

# Expected Results:
# ✅ Both endpoints respond correctly
# ✅ Response format matches requirements
# ✅ Integration works end-to-end
```

---

## 🚀 ADVANTAGES OF THIS APPROACH

### **1. Risk Mitigation:**
- Database issues caught early (most common failure point)
- Each layer tested before building on top
- Incremental validation prevents late-stage surprises

### **2. Clear Progress Tracking:**
- Tangible milestones at each phase
- Can demonstrate working components incrementally
- Easy to identify where problems occur

### **3. Maintainable Development:**
- Clean separation of concerns from start
- No circular dependencies
- Easy to modify individual layers

### **4. Testing Excellence:**
- Each layer has focused test suite
- Mock dependencies only when needed
- Integration tests validate complete system

---

## ✅ RECOMMENDATION: PROCEED WITH BOTTOM-UP APPROACH

**Your proposed plan is not only feasible but OPTIMAL for this project because:**

1. **Matches Natural Dependencies**: API depends on Application depends on Domain depends on Infrastructure
2. **Early Risk Detection**: Database and schema issues found immediately
3. **Incremental Validation**: Can test and verify each layer works before proceeding
4. **Clean Architecture**: Forces proper separation of concerns from the start
5. **Faster Debugging**: Problems isolated to specific layers

**Next Steps:**
1. **Start with Phase 1** (Infrastructure Layer)
2. **Create project structure** in your working directory
3. **Set up PostgreSQL with Docker**
4. **Implement and test database layer**

**Ready to begin Phase 1: Infrastructure Layer implementation?** 🎯

I can help you create the complete project structure and start implementing the database layer right now!
