# Refined FastAPI Implementation Plan
## Integrating Clean Architecture with src/ Main Entry Point

### 🎯 **Refined Approach**

You already have a working FastAPI application in `src/main.py`, but it bypasses your excellent clean architecture in `app/`. The plan now focuses on **refactoring the existing `src/main.py`** to use your well-designed application services while keeping `src/` as the main entry point.

### 🔍 **Current State Analysis**

#### ✅ **What You Have**
- **Working FastAPI app** in `src/main.py` with basic endpoints
- **Excellent clean architecture** in `app/` (infrastructure, domain, application layers)
- **Direct database access** in current main.py (needs to be replaced)

#### 🎯 **What We Need**
- **Refactor `src/main.py`** to use your application services
- **Add proper dependency injection** connecting to `app/` layers
- **Preserve endpoint structure** but use clean architecture
- **Maintain `src/` as entry point** as you prefer

## 📋 **Refined Implementation Plan**

### **Step 1: Create API Support Structure in src/**

Organize `src/` to support clean architecture integration:

```
src/
├── main.py                 # ← REFACTOR: Main FastAPI app (your preference)
├── dependencies.py         # ← NEW: Dependency injection for src/
├── routers/               # ← NEW: API routers
│   ├── __init__.py
│   └── time_deposits.py   # ← NEW: Clean architecture endpoints
├── database/              # ✅ EXISTS
└── domain/                # ✅ EXISTS
```

### **Step 2: Create src/dependencies.py**

Create dependency injection that connects to your `app/` layers:

```python
# src/dependencies.py
"""
Dependency injection for src/main.py FastAPI application.
Connects to the clean architecture layers in app/.
"""
import sys
import os
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

# Add app directory to path to import clean architecture
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from app.infrastructure.database.connection import get_db_session
from app.infrastructure.adapters.time_deposit_repository_adapter import TimeDepositRepositoryAdapter
from app.application.services.time_deposit_service import TimeDepositService
from app.infrastructure.config.settings import Settings

# Database dependency
async def get_database() -> AsyncSession:
    """Get database session from app infrastructure layer."""
    async for session in get_db_session():
        yield session

DatabaseDep = Annotated[AsyncSession, Depends(get_database)]

# Repository dependency
async def get_time_deposit_repository(
    db: DatabaseDep
) -> TimeDepositRepositoryAdapter:
    """Get time deposit repository adapter."""
    return TimeDepositRepositoryAdapter(db)

RepositoryDep = Annotated[TimeDepositRepositoryAdapter, Depends(get_time_deposit_repository)]

# Service dependency
async def get_time_deposit_service(
    repository: RepositoryDep
) -> TimeDepositService:
    """Get time deposit service from app application layer."""
    return TimeDepositService(repository)

ServiceDep = Annotated[TimeDepositService, Depends(get_time_deposit_service)]

# Settings dependency
def get_settings() -> Settings:
    """Get application settings."""
    return Settings()

SettingsDep = Annotated[Settings, Depends(get_settings)]
```

### **Step 3: Create src/routers/time_deposits.py**

Move endpoint logic to a proper router:

```python
# src/routers/time_deposits.py
"""
Time Deposits API Router using Clean Architecture.
Replaces direct database access with application services.
"""
from fastapi import APIRouter, HTTPException, status
from typing import List
import logging
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'app'))

from ..dependencies import ServiceDep
from app.application.schemas.time_deposit import (
    TimeDepositResponse, 
    UpdateBalancesResponse
)
from app.application.exceptions.service_exceptions import ServiceException

logger = logging.getLogger(__name__)

router = APIRouter()

@router.patch(
    "/time-deposits/balances",
    response_model=UpdateBalancesResponse,
    summary="Update all time deposit balances",
    description="Updates balances for ALL time deposits using clean architecture",
)
async def update_all_balances(
    service: ServiceDep
) -> UpdateBalancesResponse:
    """
    Update balances for ALL time deposits - REFACTORED VERSION.
    
    Now uses your excellent application service instead of direct DB access!
    Preserves the original TimeDepositCalculator.update_balance logic exactly.
    """
    try:
        logger.info("API: Updating all time deposit balances via service layer")
        result = service.update_all_balances()
        logger.info(f"API: Successfully updated {result.updated_count} balances")
        return result
    except ServiceException as e:
        logger.error(f"API: Service error updating balances: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"API: Unexpected error updating balances: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating balances"
        )

@router.get(
    "/time-deposits",
    response_model=List[TimeDepositResponse],
    summary="Get all time deposits",
    description="Retrieves all time deposits with withdrawals via clean architecture"
)
async def get_all_time_deposits(
    service: ServiceDep
) -> List[TimeDepositResponse]:
    """
    Get all time deposits - REFACTORED VERSION.
    
    Now uses your application service with proper data conversion
    instead of manual SQL queries and result formatting.
    """
    try:
        logger.info("API: Retrieving all time deposits via service layer")
        deposits = service.get_all_deposits()
        logger.info(f"API: Successfully retrieved {len(deposits)} time deposits")
        return deposits
    except ServiceException as e:
        logger.error(f"API: Service error retrieving deposits: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"API: Unexpected error retrieving deposits: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while retrieving time deposits"
        )
```

### **Step 4: Refactor src/main.py**

Replace your existing `src/main.py` with clean architecture integration:

```python
# src/main.py - FastAPI application entry point with clean architecture
"""
Refactored FastAPI Application - Now uses clean architecture!

BEFORE: Direct database access, manual SQL queries
AFTER: Application services, dependency injection, clean separation of concerns
"""
import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add app directory to path for clean architecture imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from .routers import time_deposits
from .dependencies import get_settings

# Create FastAPI application instance with enhanced configuration
app = FastAPI(
    title="Ikigai Time Deposit API",
    description="RESTful API for Time Deposit Management System using Clean Architecture",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with clean architecture endpoints
app.include_router(
    time_deposits.router,
    prefix="",  # Keep your existing URL structure
    tags=["time-deposits"]
)

# Enhanced health check
@app.get("/")
async def root():
    """Root endpoint - now indicates clean architecture usage."""
    return {
        "message": "Ikigai Time Deposit API is running!",
        "architecture": "Clean Architecture with FastAPI",
        "status": "healthy",
        "endpoints": {
            "update_balances": "PATCH /time-deposits/balances",
            "get_all_deposits": "GET /time-deposits",
            "docs": "/docs",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Dedicated health check endpoint."""
    return {
        "status": "healthy", 
        "api": "Time Deposit Management System",
        "architecture": "Clean Architecture"
    }

# Application startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    print("🚀 Starting Ikigai Time Deposit API with Clean Architecture")
    print("📊 Available at: http://127.0.0.1:8000")
    print("📚 Documentation: http://127.0.0.1:8000/docs")
    print("🏥 Health Check: http://127.0.0.1:8000/health")

# Run the app when this file is executed directly
if __name__ == "__main__":
    import uvicorn
    
    print("🎯 Starting FastAPI with Clean Architecture Integration")
    print("✅ Using application services instead of direct database access")
    print("✅ Preserving original business logic via domain layer")
    print("✅ Maintaining clean separation of concerns")
    
    uvicorn.run(
        "main:app", 
        host="127.0.0.1", 
        port=8000, 
        reload=True,  # Enable for development
        log_level="info"
    )
```

### **Step 5: Create src/routers/__init__.py**

```python
# src/routers/__init__.py
from .time_deposits import router as time_deposits_router

__all__ = ["time_deposits_router"]
```

### **Step 6: Update Endpoint URLs (Optional)**

If you want to keep your exact existing URLs, modify the router:

```python
# In src/routers/time_deposits.py

# Change from:
@router.patch("/time-deposits/balances", ...)

# To match your existing URL:
@router.put("/time-deposits/updateBalances", ...)

# Keep the GET endpoint the same:
@router.get("/time-deposits", ...)
```

### **Step 7: Enhanced Error Handling**

Add proper error handling that integrates with your application layer:

```python
# Add to src/main.py
from fastapi import Request
from fastapi.responses import JSONResponse
from app.application.exceptions.service_exceptions import ServiceException

@app.exception_handler(ServiceException)
async def service_exception_handler(request: Request, exc: ServiceException):
    """Handle application service exceptions."""
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            "type": "ServiceException",
            "path": str(request.url)
        }
    )
```

## 🚀 **Migration Steps**

### **Phase 1: Structure Setup (30 minutes)**
1. Create `src/dependencies.py`
2. Create `src/routers/` directory and `__init__.py`
3. Create `src/routers/time_deposits.py`

### **Phase 2: Endpoint Migration (45 minutes)**  
4. Copy your existing endpoints to the router
5. Replace direct database calls with service calls
6. Test individual endpoints

### **Phase 3: Main App Integration (30 minutes)**
7. Refactor `src/main.py` to use the router
8. Add middleware and error handling
9. Test complete integration

### **Phase 4: Validation (15 minutes)**
10. Test both endpoints work identically
11. Verify clean architecture integration
12. Confirm original business logic preserved

## ⚠️ **Key Benefits of This Approach**

### **🎯 Maintains Your Preferences**
- ✅ Keeps `src/main.py` as entry point
- ✅ Preserves your existing URL structure
- ✅ Uses your excellent clean architecture

### **🏗️ Architecture Improvements**
- ✅ **Before**: Direct SQL in endpoints
- ✅ **After**: Application services with proper separation
- ✅ **Before**: Manual data conversion
- ✅ **After**: Pydantic schemas with validation
- ✅ **Before**: Basic error handling  
- ✅ **After**: Structured exception handling

### **🔒 Business Logic Preservation**
- ✅ Uses your existing `TimeDepositCalculator.update_balance` exactly
- ✅ Maintains unusual cumulative interest behavior
- ✅ Preserves all domain rules and calculations

## 🧪 **Testing Strategy**

### **Before/After Comparison Tests**
```python
# tests/api/test_migration_compatibility.py
def test_endpoints_return_identical_results():
    """Verify refactored endpoints return identical results to original."""
    # Test that clean architecture version produces same results
    # as the original direct database version
```

### **Clean Architecture Integration Tests**
```python  
# tests/integration/test_src_app_integration.py
def test_src_uses_app_services():
    """Verify src/main.py properly uses app/ services."""
    # Test that dependency injection works
    # Test that services are called correctly
```

## ⏱️ **Time Estimate**

- **Structure Setup**: 30 minutes
- **Endpoint Migration**: 45 minutes
- **Main App Integration**: 30 minutes  
- **Testing & Validation**: 15 minutes
- **Total**: **2 hours** (very quick since you already have working endpoints!)

## 🎉 **Final Result**

You'll have:

1. **✅ Same Entry Point**: `src/main.py` remains your main application
2. **✅ Same URLs**: Your existing endpoints work identically  
3. **✅ Clean Architecture**: Now uses your excellent app/ layers
4. **✅ Better Code**: Replaces direct SQL with proper services
5. **✅ Same Behavior**: Original business logic preserved exactly
6. **✅ Better Testing**: Can mock services instead of database
7. **✅ Better Maintenance**: Changes in business logic don't affect API layer

This approach **respects your preference** for `src/` while **dramatically improving** the code quality by using your excellent clean architecture! 🚀
