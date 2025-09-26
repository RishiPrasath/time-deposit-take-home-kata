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