# main.py - FastAPI Application Entry Point with Hexagonal Architecture
from fastapi import FastAPI, HTTPException, Depends
from app.application.dependencies import get_time_deposit_service
from app.application.services.time_deposit_service import TimeDepositService
from app.application.schemas.time_deposit import TimeDepositResponse
from typing import List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application instance
app = FastAPI(
    title="Time Deposit API",
    description="RESTful API for managing time deposits with clean architecture",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.get("/", tags=["Health Check"])
async def root():
    """Health check endpoint"""
    return {
        "message": "Time Deposit API is running!",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.put("/time-deposits/balances", tags=["Time Deposits"])
async def update_all_balances(
    service: TimeDepositService = Depends(get_time_deposit_service)
) -> dict:
    """
    Update balances for ALL time deposits in database.
    Uses existing TimeDepositCalculator.updateBalance method.
    No request body needed (updates all records).
    """
    try:
        logger.info("Starting bulk balance update for all time deposits")
        result = service.update_all_balances()
        
        logger.info(f"Successfully updated {result.updated_count} time deposit balances")
        return {
            "message": result.message,
            "updatedCount": result.updated_count,
            "status": "success" if result.success else "error"
        }
    except Exception as e:
        logger.error(f"Error updating balances: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update balances: {str(e)}"
        )

@app.get("/time-deposits", response_model=List[TimeDepositResponse], tags=["Time Deposits"])
async def get_all_deposits(
    service: TimeDepositService = Depends(get_time_deposit_service)
) -> List[TimeDepositResponse]:
    """
    Get all time deposits with their withdrawals.
    Returns array of time deposits with exact required schema.
    """
    try:
        logger.info("Fetching all time deposits with withdrawals")
        deposits = service.get_all_deposits()
        
        logger.info(f"Successfully retrieved {len(deposits)} time deposits")
        return deposits
    except Exception as e:
        logger.error(f"Error fetching deposits: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch deposits: {str(e)}"
        )

# Health check for database connectivity
@app.get("/health", tags=["Health Check"])
async def health_check(
    service: TimeDepositService = Depends(get_time_deposit_service)
) -> dict:
    """Check database connectivity and application health"""
    try:
        # Try to get deposits to verify database connection
        deposits = service.get_all_deposits()
        return {
            "status": "healthy",
            "database": "connected",
            "total_deposits": len(deposits)
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Time Deposit API server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )