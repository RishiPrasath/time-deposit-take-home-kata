# Phase 3: Integration Flow Diagram

## 🏗️ How Application Layer Connects Everything

```
┌─────────────────────────────────────────────────────────────────────┐
│                         API LAYER (Phase 4)                         │
│                                                                     │
│  FastAPI Endpoints:                                                 │
│  • PUT /time-deposits/balances                                      │
│  • GET /time-deposits                                               │
└─────────────────────────┬───────────────────────────────────────────┘
                          │ Depends on (DI)
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER (Phase 3) 🎯                    │
│                                                                     │
│  TimeDepositService:                                                │
│  • update_all_balances() → UpdateBalancesResponse                  │
│  • get_all_deposits() → List[TimeDepositResponse]                  │
│                                                                     │
│  Schemas (Pydantic):                                                │
│  • TimeDepositResponse (exact API format)                          │
│  • WithdrawalResponse                                               │
│  • UpdateBalancesResponse                                           │
└─────────────────────────┬───────────────────────────────────────────┘
                          │ Uses interface
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     DOMAIN LAYER (Existing) ✅                       │
│                                                                     │
│  Entities:                                                          │
│  • TimeDeposit (EXACT original class)                              │
│  • TimeDepositCalculator (EXACT original logic)                    │
│  • Withdrawal                                                       │
│                                                                     │
│  Interface:                                                         │
│  • TimeDepositRepositoryInterface (abstract)                       │
└─────────────────────────┬───────────────────────────────────────────┘
                          │ Implemented by
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                 INFRASTRUCTURE LAYER (Existing) ✅                   │
│                                                                     │
│  🌉 Adapter (KEY COMPONENT):                                        │
│  • TimeDepositRepositoryAdapter                                     │
│    - Implements: TimeDepositRepositoryInterface                    │
│    - Converts: Model ↔ Domain                                       │
│    - Handles: Decimal ↔ float, relationships                       │
│                                                                     │
│  Repository:                                                        │
│  • TimeDepositRepository (SQLAlchemy operations)                   │
│                                                                     │
│  Models:                                                            │
│  • TimeDepositModel (SQLAlchemy)                                   │
│  • WithdrawalModel (SQLAlchemy)                                    │
└─────────────────────────────────────────────────────────────────────┘
```## 🔄 Data Flow Examples

### 1. Update All Balances Flow

```
API Request: PUT /time-deposits/balances
    │
    ▼
FastAPI Endpoint
    │
    ▼
TimeDepositService.update_all_balances()
    │
    ├─── 1. repository.get_all() 
    │         │
    │         ▼
    │    TimeDepositRepositoryAdapter
    │         │
    │         ├─── sql_repo.get_all() → List[TimeDepositModel]
    │         │
    │         └─── Convert each: Model → Domain (Decimal→float)
    │
    ├─── 2. calculator.update_balance(deposits)
    │         │
    │         └─── EXACT original cumulative logic applied
    │
    └─── 3. repository.save_all(deposits)
              │
              ▼
         TimeDepositRepositoryAdapter
              │
              ├─── Convert each: Domain → Model (float→Decimal)
              │
              └─── sql_repo.save_all_models()
                        │
                        ▼
                   Database UPDATE
```

### 2. Get All Deposits Flow

```
API Request: GET /time-deposits
    │
    ▼
FastAPI Endpoint
    │
    ▼
TimeDepositService.get_all_deposits()
    │
    ├─── 1. repository.get_all_with_withdrawals()
    │         │
    │         ▼
    │    TimeDepositRepositoryAdapter
    │         │
    │         ├─── sql_repo.get_all_with_withdrawals()
    │         │
    │         └─── Convert: Model+Withdrawals → Domain+Withdrawals
    │
    └─── 2. Convert to Response Schema
              │
              ├─── Domain TimeDeposit → TimeDepositResponse
              │
              └─── Domain Withdrawal → WithdrawalResponse
                        │
                        ▼
                   JSON Response
```

## 🔑 Key Integration Points

### 1. Dependency Injection Chain
```python
# In API endpoint
service: TimeDepositService = Depends(get_time_deposit_service)

# In dependencies.py
def get_time_deposit_service(db: Session = Depends(get_db)):
    sql_repo = TimeDepositRepository(db)          # Infrastructure
    adapter = TimeDepositRepositoryAdapter(sql_repo)  # Bridge
    return TimeDepositService(adapter)            # Application
```

### 2. Type Conversions (Handled by Adapter)
```
Database (Decimal) ←→ Adapter ←→ Domain (float) ←→ Service ←→ API (Decimal)
```

### 3. Interface Segregation
- Service depends on `TimeDepositRepositoryInterface` (abstract)
- Adapter implements this interface
- Service doesn't know about SQLAlchemy models

## 📊 Benefits of This Architecture

1. **Clean Separation**: Each layer has a single responsibility
2. **No Breaking Changes**: Original domain logic preserved exactly
3. **Type Safety**: Adapter handles all conversions safely
4. **Testability**: Can mock at interface boundaries
5. **Extensibility**: Easy to add new features without touching domain

## ⚠️ Critical Points

1. **Adapter is KEY**: Already exists and handles all conversions
2. **Service uses Interface**: Not concrete implementation
3. **Domain untouched**: Original calculator logic preserved
4. **Schema exact match**: API returns exact required format