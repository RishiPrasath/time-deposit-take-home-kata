"""
Time Deposits API Router using Clean Architecture.
Replaces direct database access with application services.
"""
from fastapi import APIRouter, HTTPException, status
from typing import List
import logging

from src.dependencies import ServiceDep
from src.application.schemas.time_deposit import (
    TimeDepositResponse,
    UpdateBalancesResponse
)
from src.application.exceptions.service_exceptions import ServiceException

logger = logging.getLogger(__name__)

router = APIRouter()

@router.put(
    "/time-deposits/updateBalances",
    summary="Update all time deposit balances",
    description="Updates balances for ALL time deposits using clean architecture",
)
async def update_all_balances(
    service: ServiceDep
):
    """
    Update balances for ALL time deposits - REFACTORED VERSION.

    Now uses your excellent application service instead of direct DB access!
    Preserves the original TimeDepositCalculator.update_balance logic exactly.
    """
    try:
        logger.info("API: Updating all time deposit balances via service layer")
        result = service.update_all_balances()
        logger.info(f"API: Successfully updated {result.updated_count} balances")

        # Convert to match the original API response format
        return {
            "message": result.message,
            "updatedCount": result.updated_count,
            "status": "success" if result.success else "failed"
        }
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