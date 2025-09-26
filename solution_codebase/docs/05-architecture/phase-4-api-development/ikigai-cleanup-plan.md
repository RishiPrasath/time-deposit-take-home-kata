# Ikigai Time Deposit System - Architectural Refactoring Plan

## 🎯 Executive Summary

**Current Status:** Your project has been partially migrated from mixed `app/` + `src/` structure to a consolidated `src/` structure, but there are still cleanup tasks and optimization opportunities remaining.

**Goal:** Complete the architectural consolidation, eliminate redundancy, and ensure a clean, maintainable codebase that follows Clean Architecture principles.

**Timeline:** 2-3 hours (well within your deadline of Sept 26, 11:30 PM HK time)

---

## 📊 Current Architecture Analysis

### ✅ **What's Working Well:**
- **Clean Architecture implemented** in `src/` with proper layer separation
- **Domain logic preserved** - no breaking changes to TimeDeposit class
- **Both API endpoints working** (PUT updateBalances, GET time-deposits)
- **Database schema correct** with proper foreign keys
- **Interest calculation rules implemented** correctly
- **Dependency injection** properly configured
- **Tests updated** to use `src.` imports instead of `app.` imports

### 🚨 **Issues Identified:**

1. **Legacy Directory Structure**
   ```
   app/                    # Mostly empty, only __init__.py remains
   src/database_old/       # Duplicate/old database files
   src/domain_old/         # Old domain files (if exists)
   ```

2. **Import Path Inconsistencies**
   - Some files may still use complex import paths
   - Tests might have lingering `sys.path.insert()` workarounds

3. **File Organization**
   - Old database files in multiple locations
   - Possible duplicate configuration files

4. **Documentation**
   - README may not reflect current structure
   - API documentation needs updating

---

## 🗂️ Current Directory Structure

```
C:\Users\prasa\Code\ikigai-take-home-assignment\Python\fastapi\
├── src/                           # ✅ PRIMARY ARCHITECTURE (GOOD)
│   ├── main.py                    # ✅ FastAPI entry point
│   ├── dependencies.py            # ✅ DI configuration
│   ├── routers/                   # ✅ API endpoints
│   │   └── time_deposits.py       # ✅ Both required endpoints
│   ├── domain/                    # ✅ Business logic layer
│   │   ├── entities/              # ✅ TimeDeposit, Withdrawal
│   │   ├── interfaces/            # ✅ Repository contracts
│   │   └── value_objects/         # ✅ Plan types
│   ├── application/               # ✅ Use cases layer
│   │   ├── services/              # ✅ TimeDepositService
│   │   ├── schemas/               # ✅ Pydantic models
│   │   └── exceptions/            # ✅ Service exceptions
│   ├── infrastructure/            # ✅ External concerns layer
│   │   ├── database/              # ✅ SQLAlchemy models & repos
│   │   ├── adapters/              # ✅ Repository adapters
│   │   └── config/                # ✅ Settings
│   ├── database_old/              # 🚨 CLEANUP NEEDED
│   └── domain_old/                # 🚨 CLEANUP NEEDED (if exists)
├── app/                           # 🚨 CLEANUP NEEDED (nearly empty)
├── tests/                         # ✅ GOOD (updated to src imports)
├── migrations/                    # ✅ Database setup
├── requirements.txt               # ✅ Dependencies
├── docker-compose.yml             # ✅ Containerization
└── README.md                      # 🔄 UPDATE NEEDED
```

---

## 🔧 Detailed Refactoring Plan

### **Phase 1: Directory Cleanup (30 minutes)**

#### Step 1.1: Remove Legacy `app/` Directory
```bash
# Verify app/ is empty except __init__.py
# Remove if no longer needed
rmdir app\
```

#### Step 1.2: Clean Up Old Database Files
```bash
# Remove old database files from src/
rm -rf src\database_old\
rm -rf src\domain_old\  # if exists
```

#### Step 1.3: Consolidate Database Files
```bash
# Ensure only one set of database files exists in:
# src\infrastructure\database\
```

### **Phase 2: Import Path Optimization (45 minutes)**

#### Step 2.1: Verify Current Import Structure
**Check these files for any remaining issues:**

1. **src/main.py** ✅ 
   ```python
   from src.routers import time_deposits
   from src.dependencies import get_settings
   from src.application.exceptions.service_exceptions import ServiceException
   ```

2. **src/dependencies.py** ✅
   ```python
   from src.infrastructure.database.connection import get_db
   from src.infrastructure.database.repositories.time_deposit_repository import TimeDepositRepository
   # ... other src imports
   ```

3. **src/routers/time_deposits.py** ✅
   ```python
   from src.dependencies import ServiceDep
   from src.application.schemas.time_deposit import TimeDepositResponse
   # ... other src imports
   ```

#### Step 2.2: Remove sys.path Workarounds
**Search and eliminate any remaining:**
```python
# Remove these patterns if found:
sys.path.insert(0, ...)
sys.path.append(...)
```

#### Step 2.3: Update Test Imports
**Ensure all test files use:**
```python
from src.domain.entities.time_deposit import TimeDeposit
from src.application.services.time_deposit_service import TimeDepositService
# etc.
```

### **Phase 3: Configuration Standardization (30 minutes)**

#### Step 3.1: Database Configuration
**Consolidate to single database config:**
```
src/infrastructure/config/settings.py  # Primary config
src/infrastructure/database/connection.py  # DB connection
```

#### Step 3.2: Environment Variables
**Ensure .env file has:**
```env
DATABASE_URL=sqlite:///./time_deposits.db
ENVIRONMENT=development
API_HOST=127.0.0.1
API_PORT=8000
```

#### Step 3.3: Docker Configuration
**Update docker-compose.yml if needed:**
```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./time_deposits.db
    working_dir: /app
    command: ["python", "-m", "src.main"]
```

### **Phase 4: Testing & Validation (45 minutes)**

#### Step 4.1: Run All Tests
```bash
pytest tests/ -v --tb=short
```

#### Step 4.2: API Endpoint Validation
```bash
# Start API
python -m src.main

# Test endpoints
curl -X PUT http://localhost:8000/time-deposits/updateBalances
curl -X GET http://localhost:8000/time-deposits
```

#### Step 4.3: Database Schema Verification
```sql
-- Verify exact schema matches requirements:
CREATE TABLE timeDeposits (
    id INTEGER PRIMARY KEY,
    planType VARCHAR(50) NOT NULL,
    days INTEGER NOT NULL,
    balance DECIMAL(15,2) NOT NULL
);

CREATE TABLE withdrawals (
    id INTEGER PRIMARY KEY,
    timeDepositId INTEGER NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    date DATE NOT NULL,
    FOREIGN KEY (timeDepositId) REFERENCES timeDeposits(id)
);
```

### **Phase 5: Documentation Update (30 minutes)**

#### Step 5.1: Update README.md
**Include current structure:**
```markdown
## Project Structure
```
src/
├── main.py                 # FastAPI application entry point
├── dependencies.py         # Dependency injection configuration
├── routers/               # API endpoint controllers
├── domain/                # Business logic layer
├── application/           # Use cases and services layer
└── infrastructure/        # Data access and external services
```

#### Step 5.2: Add Setup Instructions
```markdown
## Quick Start
1. pip install -r requirements.txt
2. python scripts/init_database.py
3. python -m src.main
4. Visit http://localhost:8000/docs
```

#### Step 5.3: Document API Endpoints
```markdown
## API Endpoints
- PUT /time-deposits/updateBalances - Update all balances
- GET /time-deposits - Get all time deposits with withdrawals
```

---

## ✅ Quality Checklist

### **SOLID Principles Compliance**
- [x] **S** - Single Responsibility: Each class has one reason to change
- [x] **O** - Open/Closed: Interest calculation extensible via strategy pattern
- [x] **L** - Liskov Substitution: Repository interfaces properly implemented
- [x] **I** - Interface Segregation: Focused interfaces for different concerns
- [x] **D** - Dependency Inversion: Depends on abstractions, not concretions

### **Clean Architecture Compliance**
- [x] **Domain Layer**: Core business logic isolated
- [x] **Application Layer**: Use cases and services
- [x] **Infrastructure Layer**: Database, external services
- [x] **API Layer**: Controllers and routes

### **Functional Requirements**
- [x] **Two API Endpoints**: updateBalances (PUT), getAllDeposits (GET)
- [x] **Database Schema**: Exact match to requirements
- [x] **Interest Rules**: All three plan types implemented correctly
- [x] **No Breaking Changes**: TimeDeposit class preserved
- [x] **updateBalance Method**: Signature unchanged

---

## 🚀 Implementation Commands

### **Execute Cleanup (Run these commands):**

```powershell
# Navigate to project root
cd C:\Users\prasa\Code\ikigai-take-home-assignment\Python\fastapi

# Remove empty app directory (if completely empty)
if (Test-Path "app" -PathType Container) { 
    if ((Get-ChildItem "app" | Measure-Object).Count -le 1) {
        Remove-Item -Recurse -Force "app"
    }
}

# Remove old database files
Remove-Item -Recurse -Force "src\database_old" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "src\domain_old" -ErrorAction SilentlyContinue

# Clean up cache files
Get-ChildItem -Recurse -Name "__pycache__" | Remove-Item -Recurse -Force
Get-ChildItem -Recurse -Name "*.pyc" | Remove-Item -Force

# Run tests to verify everything works
pytest tests/ -v

# Start the API to test
python -m src.main
```

---

## 📈 Success Metrics

### **Immediate Success Indicators:**
1. ✅ All tests pass without import errors
2. ✅ API starts without import errors  
3. ✅ Both endpoints return correct responses
4. ✅ Database operations work correctly
5. ✅ No `sys.path.insert()` workarounds needed

### **Code Quality Metrics:**
1. ✅ Clean import statements throughout
2. ✅ Single source of truth for each component
3. ✅ No duplicate files or directories
4. ✅ Clear separation of concerns
5. ✅ Easy to navigate file structure

### **Functional Validation:**
1. ✅ Interest calculations match original business logic
2. ✅ updateBalance method works identically to before
3. ✅ API responses match exact schema requirements
4. ✅ Database schema matches requirements exactly

---

## 🎉 Final Deliverable State

After completing this refactoring plan, your project will have:

### **Clean Architecture ✅**
- Pure domain layer with no external dependencies
- Application services orchestrating business logic
- Infrastructure layer handling data access
- API layer providing RESTful endpoints

### **Production-Ready Code ✅**
- No import path hacks or workarounds
- Clean, maintainable file structure
- Comprehensive test coverage
- Proper error handling and logging

### **Ikigai Requirements Met ✅**
- Both required API endpoints working perfectly
- Exact database schema implementation
- All interest calculation rules preserved
- No breaking changes to existing logic
- Extensible design for future requirements

---

## 📞 Support & Troubleshooting

### **If Import Errors Occur:**
1. Check PYTHONPATH includes project root
2. Ensure __init__.py files exist in all packages
3. Use absolute imports from src.* consistently

### **If Tests Fail:**
1. Run `pytest tests/ -v --tb=long` for detailed output
2. Check test database configuration
3. Verify all fixtures are properly configured

### **If API Doesn't Start:**
1. Check requirements.txt dependencies installed
2. Verify database file exists and is accessible
3. Check port 8000 is not already in use

---

**🏆 This plan will deliver a clean, production-ready codebase that exceeds the Ikigai requirements while maintaining all existing functionality.**
