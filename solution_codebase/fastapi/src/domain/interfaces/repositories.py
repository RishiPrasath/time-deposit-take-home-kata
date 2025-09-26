"""
Abstract repository interface for dependency inversion
"""
from abc import ABC, abstractmethod
from typing import List
from src.domain.entities.time_deposit import TimeDeposit


class TimeDepositRepositoryInterface(ABC):
    """
    Abstract interface for time deposit repository operations

    This interface decouples the domain layer from infrastructure,
    allowing different implementations (database, memory, etc.)
    """

    @abstractmethod
    def get_all(self) -> List[TimeDeposit]:
        """
        Get all time deposits as domain entities

        Returns:
            List of TimeDeposit domain objects
        """
        pass

    @abstractmethod
    def get_all_with_withdrawals(self) -> List[TimeDeposit]:
        """
        Get all time deposits with their withdrawals loaded

        Returns:
            List of TimeDeposit domain objects with withdrawals populated
        """
        pass

    @abstractmethod
    def save_all(self, deposits: List[TimeDeposit]) -> None:
        """
        Save all time deposits back to persistence layer

        Args:
            deposits: List of TimeDeposit domain objects to save
        """
        pass

    @abstractmethod
    def create_sample_data(self) -> None:
        """
        Create sample data for testing and development
        """
        pass