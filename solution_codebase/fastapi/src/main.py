# main.py - FastAPI application entry point with clean architecture
"""
Refactored FastAPI Application - Now uses clean architecture!

BEFORE: Direct database access, manual SQL queries
AFTER: Application services, dependency injection, clean separation of concerns
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.routers import time_deposits
from src.dependencies import get_settings
from src.application.exceptions.service_exceptions import ServiceException


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    print("Starting Ikigai Time Deposit API with Clean Architecture")
    print("Available at: http://127.0.0.1:8000")
    print("Documentation: http://127.0.0.1:8000/docs")
    print("Health Check: http://127.0.0.1:8000/health")
    yield
    # Shutdown (if needed)
    print("Shutting down Ikigai Time Deposit API")


# Create FastAPI application instance with enhanced configuration
app = FastAPI(
    title="Ikigai Time Deposit API",
    description="RESTful API for Time Deposit Management System using Clean Architecture",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
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
            "update_balances": "PUT /time-deposits/updateBalances",
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

# Exception handler for service exceptions
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

# Run the app when this file is executed directly
if __name__ == "__main__":
    import uvicorn

    print("Starting FastAPI with Clean Architecture Integration")
    print("Using application services instead of direct database access")
    print("Preserving original business logic via domain layer")
    print("Maintaining clean separation of concerns")

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,  # Enable for development
        log_level="info"
    )