from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError

from app.infrastructure.database.models import TimeDepositModel, WithdrawalModel


class TimeDepositRepository:
    """
    Repository for managing time deposit database operations.

    This class implements the data access layer for time deposits,
    providing methods to retrieve, update, and manage time deposits
    and their associated withdrawals.
    """

    def __init__(self, db: Session):
        """
        Initialize repository with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def get_all(self) -> List[TimeDepositModel]:
        """
        Get all time deposits without withdrawals.

        This method is used for balance update operations where
        withdrawal data is not needed.

        Returns:
            List of all time deposit models
        """
        try:
            return self.db.query(TimeDepositModel).all()
        except SQLAlchemyError as e:
            raise Exception(f"Failed to fetch time deposits: {str(e)}")

    def get_all_with_withdrawals(self) -> List[TimeDepositModel]:
        """
        Get all time deposits with their associated withdrawals.

        Uses eager loading (joinedload) to fetch withdrawals in a single query,
        avoiding N+1 query problem.

        Returns:
            List of time deposit models with withdrawals loaded
        """
        try:
            return (
                self.db.query(TimeDepositModel)
                .options(joinedload(TimeDepositModel.withdrawals))
                .all()
            )
        except SQLAlchemyError as e:
            raise Exception(f"Failed to fetch time deposits with withdrawals: {str(e)}")

    def get_by_id(self, deposit_id: int) -> Optional[TimeDepositModel]:
        """
        Get a single time deposit by ID.

        Args:
            deposit_id: The ID of the time deposit to retrieve

        Returns:
            TimeDepositModel if found, None otherwise
        """
        try:
            return (
                self.db.query(TimeDepositModel)
                .filter(TimeDepositModel.id == deposit_id)
                .first()
            )
        except SQLAlchemyError as e:
            raise Exception(f"Failed to fetch time deposit by ID: {str(e)}")

    def save_all(self, deposits: List[TimeDepositModel]) -> None:
        """
        Save multiple time deposits in a single transaction.

        This method updates existing deposits or creates new ones
        based on whether they have an ID.

        Args:
            deposits: List of time deposit models to save
        """
        try:
            for deposit in deposits:
                if deposit.id:
                    # Update existing deposit
                    self.db.merge(deposit)
                else:
                    # Add new deposit
                    self.db.add(deposit)

            self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Failed to save time deposits: {str(e)}")

    def save_all_models(self, models: List[TimeDepositModel]) -> None:
        """
        Save all models back to database

        Used by adapter to persist domain entity changes

        Args:
            models: List of TimeDepositModel objects to save
        """
        try:
            for model in models:
                # Merge handles both updates and inserts
                self.db.merge(model)
            self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Failed to save time deposit models: {str(e)}")

    def update_balance(self, deposit_id: int, new_balance: Decimal) -> None:
        """
        Update the balance of a specific time deposit.

        Args:
            deposit_id: The ID of the deposit to update
            new_balance: The new balance value
        """
        try:
            deposit = self.get_by_id(deposit_id)
            if deposit:
                deposit.balance = new_balance
                self.db.commit()
            else:
                raise ValueError(f"Time deposit with ID {deposit_id} not found")
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Failed to update balance: {str(e)}")

    def create_sample_data(self) -> None:
        """
        Create sample time deposits and withdrawals for testing.

        This method creates 9 time deposits with various plan types
        and 9 associated withdrawals as specified in the requirements.
        """
        try:
            # Clear existing data
            self.db.query(WithdrawalModel).delete()
            self.db.query(TimeDepositModel).delete()

            # Create sample time deposits
            deposits = [
                # Basic plan deposits
                TimeDepositModel(id=1, planType='basic', days=45, balance=Decimal('10000.00')),
                TimeDepositModel(id=2, planType='basic', days=25, balance=Decimal('5000.50')),
                TimeDepositModel(id=3, planType='basic', days=90, balance=Decimal('25000.75')),

                # Student plan deposits
                TimeDepositModel(id=4, planType='student', days=60, balance=Decimal('8000.00')),
                TimeDepositModel(id=5, planType='student', days=400, balance=Decimal('15000.25')),
                TimeDepositModel(id=6, planType='student', days=15, balance=Decimal('3000.00')),

                # Premium plan deposits
                TimeDepositModel(id=7, planType='premium', days=50, balance=Decimal('50000.00')),
                TimeDepositModel(id=8, planType='premium', days=30, balance=Decimal('20000.00')),
                TimeDepositModel(id=9, planType='premium', days=100, balance=Decimal('75000.50')),
            ]

            for deposit in deposits:
                self.db.add(deposit)

            # Create sample withdrawals
            withdrawals = [
                # Withdrawals from basic deposit #1
                WithdrawalModel(id=1, timeDepositId=1, amount=Decimal('500.00'),
                              date=date(2024, 1, 15)),
                WithdrawalModel(id=2, timeDepositId=1, amount=Decimal('200.00'),
                              date=date(2024, 2, 1)),

                # Withdrawals from student deposit #4
                WithdrawalModel(id=3, timeDepositId=4, amount=Decimal('1000.00'),
                              date=date(2024, 1, 20)),
                WithdrawalModel(id=4, timeDepositId=4, amount=Decimal('250.75'),
                              date=date(2024, 3, 5)),

                # Withdrawals from premium deposit #7
                WithdrawalModel(id=5, timeDepositId=7, amount=Decimal('2500.00'),
                              date=date(2024, 1, 10)),
                WithdrawalModel(id=6, timeDepositId=7, amount=Decimal('1000.00'),
                              date=date(2024, 1, 25)),
                WithdrawalModel(id=7, timeDepositId=7, amount=Decimal('500.00'),
                              date=date(2024, 2, 15)),

                # Additional withdrawals for testing
                WithdrawalModel(id=8, timeDepositId=3, amount=Decimal('1500.00'),
                              date=date(2024, 2, 28)),
                WithdrawalModel(id=9, timeDepositId=5, amount=Decimal('750.25'),
                              date=date(2024, 3, 10)),
            ]

            for withdrawal in withdrawals:
                self.db.add(withdrawal)

            self.db.commit()

        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Failed to create sample data: {str(e)}")

    def delete_all(self) -> None:
        """
        Delete all time deposits and withdrawals.

        WARNING: This will permanently delete all data!
        """
        try:
            self.db.query(WithdrawalModel).delete()
            self.db.query(TimeDepositModel).delete()
            self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise Exception(f"Failed to delete all data: {str(e)}")