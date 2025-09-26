# Phase 3: Quick Reference Guide

## 🎯 Application Layer Implementation Checklist

### 1️⃣ Project Structure (5 min)
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

### 2️⃣ Implementation Order
1. **Schemas** (20 min) - Pydantic models for API responses
2. **Mappers** (15 min) - Data transformation between layers
3. **Service** (40 min) - Business workflow orchestration
4. **Tests** (15 min) - Unit and integration tests

### 3️⃣ Key Files to Create

#### `schemas/time_deposit.py`
```python
class WithdrawalResponse(BaseModel):
    id: int
    amount: Decimal
    date: date

class TimeDepositResponse(BaseModel):
    id: int
    planType: str  # EXACT field name!
    balance: Decimal
    days: int
    withdrawals: List[WithdrawalResponse]

class UpdateBalancesResponse(BaseModel):
    success: bool
    message: str
    updated_count: int
    timestamp: date
```

#### `services/time_deposit_service.py`
```python
class TimeDepositService:
    def __init__(self, repository: TimeDepositRepositoryInterface):
        self.repository = repository
        self.calculator = TimeDepositCalculator()
    
    def update_all_balances(self) -> UpdateBalancesResponse:
        # Get → Convert → Calculate → Save → Return
        
    def get_all_deposits(self) -> List[TimeDepositResponse]:
        # Get with withdrawals → Convert → Return
```

### 4️⃣ Critical Requirements
- ✅ NO modifications to `TimeDepositCalculator.update_balance`
- ✅ Field names MUST match exactly (planType, not plan_type)
- ✅ Use Decimal for money, not float
- ✅ Service only orchestrates, doesn't calculate

### 5️⃣ Testing Commands
```bash
# Test only application layer
pytest tests/application/ -v

# Test service with mocked repository
pytest tests/application/test_time_deposit_service.py -v

# Integration test with real database
pytest tests/application/test_service_integration.py -v
```

### 6️⃣ Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Import errors | Ensure `__init__.py` files exist |
| Type mismatch | Use Decimal for money, int for IDs |
| Field name errors | Match exact names (planType) |
| Calculation changes | Don't modify domain logic |

### 7️⃣ Success Criteria
- [ ] Both service methods implemented
- [ ] Schemas match exact requirements
- [ ] Mappers handle all conversions
- [ ] All tests pass
- [ ] No breaking changes to domain