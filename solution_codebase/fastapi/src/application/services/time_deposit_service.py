from typing import List
from datetime import datetime, timezone
from decimal import Decimal
import logging

from src.domain.entities.time_deposit import TimeDepositCalculator
from src.domain.interfaces.repositories import TimeDepositRepositoryInterface
from src.application.schemas.time_deposit import TimeDepositResponse, WithdrawalResponse, UpdateBalancesResponse
from src.application.exceptions.service_exceptions import ServiceException

logger = logging.getLogger(__name__)

class TimeDepositService:
    """
    Application service that orchestrates time deposit operations.
    Uses the existing repository adapter for all data operations.
    """

    def __init__(self, repository: TimeDepositRepositoryInterface):
        """
        Initialize service with repository interface.
        In practice, this will be the TimeDepositRepositoryAdapter.

        Args:
            repository: Repository interface (injected adapter)
        """
        self.repository = repository
        self.calculator = TimeDepositCalculator()

    def update_all_balances(self) -> UpdateBalancesResponse:
        """
        Update all time deposit balances using the EXACT original calculator logic.

        Returns:
            UpdateBalancesResponse with operation results
        """
        try:
            # Get all deposits as domain entities (adapter handles conversion)
            logger.info("Retrieving all time deposits for balance update")
            deposits = self.repository.get_all()

            if not deposits:
                logger.warning("No time deposits found to update")
                return UpdateBalancesResponse(
                    success=True,
                    message="No time deposits found to update",
                    updated_count=0,
                    timestamp=datetime.now(timezone.utc).date()
                )

            # Store original balances for comparison
            original_balances = {d.id: d.balance for d in deposits}
            logger.info(f"Processing {len(deposits)} deposits for interest calculation")

            # Apply EXACT original interest calculation
            # This preserves the unusual cumulative interest logic
            self.calculator.update_balance(deposits)

            # Save updated deposits (adapter handles conversion back)
            logger.info("Saving updated balances to database")
            self.repository.save_all(deposits)

            # Count actual updates
            updated_count = sum(
                1 for d in deposits
                if d.balance != original_balances[d.id]
            )

            logger.info(f"Successfully updated {updated_count} deposits")

            return UpdateBalancesResponse(
                success=True,
                message=f"Successfully updated {updated_count} time deposit balances",
                updated_count=updated_count,
                timestamp=datetime.now(timezone.utc).date()
            )

        except Exception as e:
            logger.error(f"Error updating balances: {str(e)}")
            raise ServiceException(f"Failed to update balances: {str(e)}")

    def get_all_deposits(self) -> List[TimeDepositResponse]:
        """
        Retrieve all time deposits with their withdrawals.

        Returns:
            List of TimeDepositResponse objects
        """
        try:
            logger.info("Retrieving all time deposits with withdrawals")

            # Get deposits with withdrawals (adapter handles joins)
            deposits = self.repository.get_all_with_withdrawals()

            # Convert to response format
            responses = []
            for deposit in deposits:
                # Convert withdrawals to response format
                withdrawal_responses = []
                for withdrawal in deposit.withdrawals:
                    withdrawal_response = WithdrawalResponse(
                        id=withdrawal.id,
                        amount=Decimal(str(withdrawal.amount)),
                        date=datetime.fromisoformat(withdrawal.date).date()
                    )
                    withdrawal_responses.append(withdrawal_response)

                # Create deposit response with exact field names
                response = TimeDepositResponse(
                    id=deposit.id,
                    planType=deposit.planType,  # Must be planType, not plan_type!
                    balance=Decimal(str(deposit.balance)),
                    days=deposit.days,
                    withdrawals=withdrawal_responses
                )
                responses.append(response)

            logger.info(f"Successfully retrieved {len(responses)} time deposits")
            return responses

        except Exception as e:
            logger.error(f"Error retrieving deposits: {str(e)}")
            raise ServiceException(f"Failed to retrieve deposits: {str(e)}")