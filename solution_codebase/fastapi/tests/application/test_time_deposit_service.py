import pytest
from unittest.mock import Mock, MagicMock
from decimal import Decimal
from datetime import date

from app.domain.entities.time_deposit import TimeDeposit
from app.domain.entities.withdrawal import Withdrawal
from app.application.services.time_deposit_service import TimeDepositService
from app.application.schemas.time_deposit import UpdateBalancesResponse

class TestTimeDepositService:

    @pytest.fixture
    def mock_repository(self):
        """Create a mock repository that implements the interface."""
        return Mock()

    @pytest.fixture
    def service(self, mock_repository):
        """Create service with mocked repository."""
        return TimeDepositService(mock_repository)

    def test_update_all_balances_with_existing_deposits(self, service, mock_repository):
        # Arrange
        deposits = [
            TimeDeposit(1, "basic", 1000.0, 45),
            TimeDeposit(2, "student", 2000.0, 90)
        ]
        mock_repository.get_all.return_value = deposits

        # Act
        result = service.update_all_balances()

        # Assert
        assert isinstance(result, UpdateBalancesResponse)
        assert result.success is True
        assert result.updated_count > 0
        mock_repository.save_all.assert_called_once_with(deposits)

    def test_update_all_balances_empty_database(self, service, mock_repository):
        # Arrange
        mock_repository.get_all.return_value = []

        # Act
        result = service.update_all_balances()

        # Assert
        assert result.success is True
        assert result.updated_count == 0
        assert "No time deposits found" in result.message
        assert not mock_repository.save_all.called

    def test_get_all_deposits_with_withdrawals(self, service, mock_repository):
        # Arrange
        deposit = TimeDeposit(1, "basic", 1000.0, 45)
        withdrawal = Withdrawal(1, 100.0, "2024-01-15")
        deposit.withdrawals = [withdrawal]

        mock_repository.get_all_with_withdrawals.return_value = [deposit]

        # Act
        result = service.get_all_deposits()

        # Assert
        assert len(result) == 1
        assert result[0].id == 1
        assert result[0].planType == "basic"  # Exact field name
        assert len(result[0].withdrawals) == 1

    def test_get_all_deposits_empty_database(self, service, mock_repository):
        # Arrange
        mock_repository.get_all_with_withdrawals.return_value = []

        # Act
        result = service.get_all_deposits()

        # Assert
        assert len(result) == 0

    def test_update_all_balances_multiple_plans(self, service, mock_repository):
        # Arrange
        deposits = [
            TimeDeposit(1, "basic", 1000.0, 45),
            TimeDeposit(2, "student", 2000.0, 90),
            TimeDeposit(3, "premium", 3000.0, 60)
        ]
        mock_repository.get_all.return_value = deposits

        # Act
        result = service.update_all_balances()

        # Assert
        assert result.success is True
        assert result.updated_count == 3
        mock_repository.save_all.assert_called_once_with(deposits)