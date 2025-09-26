"""
🌉 CRITICAL INTEGRATION BRIDGE

This adapter converts between:
- Infrastructure layer (SQLAlchemy models)
- Domain layer (Pure Python objects)

This is THE KEY to preserving existing business logic while adding database persistence.
"""
from typing import List
from decimal import Decimal

from src.domain.interfaces.repositories import TimeDepositRepositoryInterface
from src.domain.entities.time_deposit import TimeDeposit
from src.domain.entities.withdrawal import Withdrawal
from src.infrastructure.database.repositories.time_deposit_repository import TimeDepositRepository
from src.infrastructure.database.models import TimeDepositModel, WithdrawalModel


class TimeDepositRepositoryAdapter(TimeDepositRepositoryInterface):
    """
    🌉 INTEGRATION ADAPTER: Connects Infrastructure ↔ Domain

    This adapter:
    1. Implements domain repository interface
    2. Uses infrastructure repository internally
    3. Converts between SQLAlchemy models and domain entities
    4. Preserves exact business logic behavior

    ⚠️ CRITICAL: All conversions must preserve data integrity and types
    """

    def __init__(self, sql_repository: TimeDepositRepository):
        """
        Initialize with infrastructure repository

        Args:
            sql_repository: The SQLAlchemy-based repository from Phase 1
        """
        self._sql_repo = sql_repository

    def get_all(self) -> List[TimeDeposit]:
        """
        Get all time deposits as domain entities

        Flow: Database → SQLAlchemy Models → Domain Entities
        """
        try:
            models = self._sql_repo.get_all()
            return [self._model_to_domain(model) for model in models]
        except Exception as e:
            raise Exception(f"Failed to get all time deposits: {str(e)}")

    def get_all_with_withdrawals(self) -> List[TimeDeposit]:
        """
        Get all time deposits with withdrawals as domain entities

        Flow: Database → SQLAlchemy Models (with joins) → Domain Entities (with withdrawals)
        """
        try:
            models = self._sql_repo.get_all_with_withdrawals()
            return [self._model_to_domain_with_withdrawals(model) for model in models]
        except Exception as e:
            raise Exception(f"Failed to get time deposits with withdrawals: {str(e)}")

    def save_all(self, deposits: List[TimeDeposit]) -> None:
        """
        Save domain entities back to database

        Flow: Domain Entities → SQLAlchemy Models → Database

        ⚠️ CRITICAL: Must handle balance updates from TimeDepositCalculator
        """
        try:
            models = [self._domain_to_model(deposit) for deposit in deposits]
            self._sql_repo.save_all_models(models)
        except Exception as e:
            raise Exception(f"Failed to save time deposits: {str(e)}")

    def create_sample_data(self) -> None:
        """
        Create sample data using infrastructure repository
        """
        try:
            self._sql_repo.create_sample_data()
        except Exception as e:
            raise Exception(f"Failed to create sample data: {str(e)}")

    # 🔄 CONVERSION METHODS - THE CRITICAL INTEGRATION LOGIC

    def _model_to_domain(self, model: TimeDepositModel) -> TimeDeposit:
        """
        Convert SQLAlchemy model to domain entity

        ⚠️ CRITICAL CONVERSIONS:
        - Decimal → float (for business logic compatibility)
        - Database ID → domain ID
        - Preserve all original field types and names
        """
        return TimeDeposit(
            id=model.id,
            planType=model.planType,  # Already string
            balance=float(model.balance),  # Convert Decimal to float for original logic
            days=model.days  # Already int
        )

    def _model_to_domain_with_withdrawals(self, model: TimeDepositModel) -> TimeDeposit:
        """
        Convert SQLAlchemy model to domain entity WITH withdrawals

        ⚠️ CRITICAL: Properly handles relationship data
        """
        # Start with base conversion
        domain = self._model_to_domain(model)

        # Add withdrawals if they exist
        if model.withdrawals:
            for withdrawal_model in model.withdrawals:
                withdrawal = Withdrawal(
                    id=withdrawal_model.id,
                    amount=float(withdrawal_model.amount),  # Convert Decimal to float
                    date=withdrawal_model.date.isoformat()  # Convert Date to ISO string
                )
                domain.withdrawals.append(withdrawal)

        return domain

    def _domain_to_model(self, domain: TimeDeposit) -> TimeDepositModel:
        """
        Convert domain entity to SQLAlchemy model

        ⚠️ CRITICAL: Must handle updated balances from TimeDepositCalculator
        This is where calculated interest gets persisted back to database
        """
        # Get existing model if it exists (for updates)
        existing_model = None
        if domain.id:
            try:
                existing_model = self._sql_repo.db.query(TimeDepositModel).filter(
                    TimeDepositModel.id == domain.id
                ).first()
            except:
                pass

        if existing_model:
            # Update existing model with potentially changed balance
            existing_model.balance = Decimal(str(domain.balance))  # Convert float back to Decimal
            existing_model.planType = domain.planType
            existing_model.days = domain.days
            return existing_model
        else:
            # Create new model
            return TimeDepositModel(
                id=domain.id,
                planType=domain.planType,
                days=domain.days,
                balance=Decimal(str(domain.balance))  # Convert float to Decimal for database
            )