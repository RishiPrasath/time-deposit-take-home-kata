from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from datetime import date
from typing import List

class WithdrawalResponse(BaseModel):
    """Response model for withdrawal data."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    amount: Decimal
    date: date

class TimeDepositResponse(BaseModel):
    """
    Response model for time deposit with exact required schema.

    CRITICAL: Field names must match exactly:
    - planType (not plan_type)
    - All fields required
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    planType: str
    balance: Decimal
    days: int
    withdrawals: List[WithdrawalResponse] = []

class UpdateBalancesResponse(BaseModel):
    """Response model for balance update operation."""
    success: bool
    message: str
    updated_count: int
    timestamp: date