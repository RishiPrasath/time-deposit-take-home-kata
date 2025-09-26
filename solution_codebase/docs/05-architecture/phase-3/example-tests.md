# Phase 3: Example Tests

## Service Layer Test Examples

### 1. Mock Repository for Unit Testing

```python
# tests/application/conftest.py
import pytest
from unittest.mock import Mock, MagicMock
from decimal import Decimal
from datetime import date
from app.infrastructure.database.models import TimeDepositModel, WithdrawalModel

@pytest.fixture
def mock_time_deposit_basic():
    """Create a mock basic time deposit"""
    deposit = MagicMock(spec=TimeDepositModel)
    deposit.id = 1
    deposit.planType = "basic"
    deposit.balance = Decimal("1000.00")
    deposit.days = 45
    deposit.withdrawals = []
    return deposit

@pytest.fixture
def mock_time_deposit_with_withdrawals():
    """Create a mock deposit with withdrawals"""
    deposit = MagicMock(spec=TimeDepositModel)
    deposit.id = 2
    deposit.planType = "student"
    deposit.balance = Decimal("5000.00")
    deposit.days = 90
    
    # Add mock withdrawals
    w1 = MagicMock(spec=WithdrawalModel)
    w1.id = 1
    w1.amount = Decimal("500.00")
    w1.date = date(2024, 1, 15)
    
    w2 = MagicMock(spec=WithdrawalModel)
    w2.id = 2
    w2.amount = Decimal("300.00")
    w2.date = date(2024, 2, 1)
    
    deposit.withdrawals = [w1, w2]
    return deposit
@pytest.fixture
def mock_repository():
    """Create a mock repository"""
    return Mock()
```

### 2. Service Unit Tests

```python
# tests/application/test_time_deposit_service.py
import pytest
from app.application.services.time_deposit_service import TimeDepositService
from app.application.exceptions.service_exceptions import ServiceException

class TestTimeDepositServiceUnit:
    
    def test_update_all_balances_basic_plan(self, mock_repository, mock_time_deposit_basic):
        # Arrange
        mock_repository.get_all.return_value = [mock_time_deposit_basic]
        service = TimeDepositService(mock_repository)
        
        # Act
        result = service.update_all_balances()
        
        # Assert
        assert result.success is True
        assert result.updated_count == 1
        assert mock_repository.save_all.called
        # Verify balance was updated (45 days = 1% interest)
        updated_balance = mock_repository.save_all.call_args[0][0][0].balance
        assert updated_balance == Decimal("1010.00")  # 1000 + 1%    
    def test_update_all_balances_empty_database(self, mock_repository):
        # Arrange
        mock_repository.get_all.return_value = []
        service = TimeDepositService(mock_repository)
        
        # Act
        result = service.update_all_balances()
        
        # Assert
        assert result.success is True
        assert result.updated_count == 0
        assert "No time deposits found" in result.message
        assert not mock_repository.save_all.called
    
    def test_update_all_balances_multiple_plans(self, mock_repository):
        # Arrange
        deposits = [
            self._create_deposit(1, "basic", "1000.00", 45),
            self._create_deposit(2, "student", "2000.00", 35),
            self._create_deposit(3, "premium", "3000.00", 50)
        ]
        mock_repository.get_all.return_value = deposits
        service = TimeDepositService(mock_repository)
        
        # Act
        result = service.update_all_balances()
        
        # Assert
        assert result.success is True
        assert result.updated_count == 3
        mock_repository.save_all.assert_called_once_with(deposits)    
    def test_update_all_balances_repository_error(self, mock_repository):
        # Arrange
        mock_repository.get_all.side_effect = Exception("Database connection failed")
        service = TimeDepositService(mock_repository)
        
        # Act & Assert
        with pytest.raises(ServiceException) as exc_info:
            service.update_all_balances()
        
        assert "Failed to update balances" in str(exc_info.value)
    
    def test_get_all_deposits_with_withdrawals(self, mock_repository, mock_time_deposit_with_withdrawals):
        # Arrange
        mock_repository.get_all_with_withdrawals.return_value = [mock_time_deposit_with_withdrawals]
        service = TimeDepositService(mock_repository)
        
        # Act
        result = service.get_all_deposits()
        
        # Assert
        assert len(result) == 1
        deposit = result[0]
        assert deposit.id == 2
        assert deposit.planType == "student"
        assert deposit.balance == Decimal("5000.00")
        assert len(deposit.withdrawals) == 2
        assert deposit.withdrawals[0].amount == Decimal("500.00")
    
    def _create_deposit(self, id, plan_type, balance, days):
        deposit = MagicMock()
        deposit.id = id
        deposit.planType = plan_type
        deposit.balance = Decimal(balance)
        deposit.days = days
        deposit.withdrawals = []
        return deposit
```
### 3. Mapper Tests

```python
# tests/application/test_mappers.py
import pytest
from decimal import Decimal
from datetime import date
from app.application.mappers.time_deposit_mapper import TimeDepositMapper
from app.domain.entities.time_deposit import TimeDeposit
from app.infrastructure.database.models import TimeDepositModel, WithdrawalModel

class TestTimeDepositMapper:
    
    def test_model_to_domain_conversion(self):
        # Arrange
        model = TimeDepositModel(
            id=1,
            planType="basic",
            balance=Decimal("1000.00"),
            days=30
        )
        
        # Act
        domain = TimeDepositMapper.model_to_domain(model)
        
        # Assert
        assert isinstance(domain, TimeDeposit)
        assert domain.id == 1
        assert domain.planType == "basic"
        assert domain.balance == 1000.0  # Domain uses float
        assert domain.days == 30
    
    def test_domain_to_model_update(self):
        # Arrange
        domain = TimeDeposit(1, "basic", 1010.0, 30)
        model = TimeDepositModel(
            id=1,
            planType="basic",
            balance=Decimal("1000.00"),
            days=30
        )
        
        # Act
        updated_model = TimeDepositMapper.domain_to_model(domain, model)
        
        # Assert
        assert updated_model.balance == Decimal("1010.0")
        # Only balance should be updated
        assert updated_model.id == 1
        assert updated_model.planType == "basic"
        assert updated_model.days == 30
    
    def test_model_to_response_with_withdrawals(self):
        # Arrange
        model = TimeDepositModel(
            id=1,
            planType="student",
            balance=Decimal("5000.00"),
            days=90
        )
        w1 = WithdrawalModel(
            id=1,
            timeDepositId=1,
            amount=Decimal("100.00"),
            date=date(2024, 1, 15)
        )
        w2 = WithdrawalModel(
            id=2,
            timeDepositId=1,
            amount=Decimal("200.00"),
            date=date(2024, 2, 1)
        )
        model.withdrawals = [w1, w2]
        
        # Act
        response = TimeDepositMapper.model_to_response(model)
        
        # Assert
        assert response.id == 1
        assert response.planType == "student"
        assert response.balance == Decimal("5000.00")
        assert response.days == 90
        assert len(response.withdrawals) == 2
        assert response.withdrawals[0].amount == Decimal("100.00")
        assert response.withdrawals[1].date == date(2024, 2, 1)
```
### 4. Integration Test with In-Memory Database

```python
# tests/application/test_service_integration.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decimal import Decimal

from app.infrastructure.database.models import Base, TimeDepositModel, WithdrawalModel
from app.infrastructure.database.repositories.time_deposit_repository import TimeDepositRepository
from app.application.services.time_deposit_service import TimeDepositService

class TestServiceDatabaseIntegration:
    
    @pytest.fixture
    def in_memory_db(self):
        """Create in-memory SQLite database for testing"""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        yield session
        session.close()
    
    @pytest.fixture
    def repository(self, in_memory_db):
        return TimeDepositRepository(in_memory_db)
    
    @pytest.fixture
    def service(self, repository):
        return TimeDepositService(repository)    
    @pytest.fixture
    def seed_test_data(self, in_memory_db):
        """Seed database with test data"""
        deposits = [
            TimeDepositModel(planType="basic", balance=Decimal("1000.00"), days=45),
            TimeDepositModel(planType="student", balance=Decimal("2000.00"), days=90),
            TimeDepositModel(planType="premium", balance=Decimal("5000.00"), days=50)
        ]
        
        # Add withdrawals to second deposit
        withdrawal = WithdrawalModel(
            timeDepositId=2,
            amount=Decimal("500.00"),
            date=date(2024, 1, 15)
        )
        deposits[1].withdrawals.append(withdrawal)
        
        in_memory_db.add_all(deposits)
        in_memory_db.commit()
        
        return deposits
    
    def test_full_update_workflow_with_real_database(self, service, seed_test_data, in_memory_db):
        # Act - Update all balances
        result = service.update_all_balances()
        
        # Assert - Operation succeeded
        assert result.success is True
        assert result.updated_count == 3
        
        # Verify actual database changes
        updated_deposits = in_memory_db.query(TimeDepositModel).order_by(TimeDepositModel.id).all()
        
        # Basic plan: 45 days = 1% interest
        assert updated_deposits[0].balance == Decimal("1010.00")
        
        # Student plan: 90 days = 3% interest
        assert updated_deposits[1].balance == Decimal("2060.00")
        
        # Premium plan: 50 days = 5% interest (after 45 days)
        assert updated_deposits[2].balance == Decimal("5250.00")
    
    def test_get_all_deposits_with_real_database(self, service, seed_test_data):
        # Act - Get all deposits
        result = service.get_all_deposits()
        
        # Assert
        assert len(result) == 3
        
        # Check first deposit (no withdrawals)
        assert result[0].id == 1
        assert result[0].planType == "basic"
        assert len(result[0].withdrawals) == 0
        
        # Check second deposit (has withdrawal)
        assert result[1].id == 2
        assert result[1].planType == "student"
        assert len(result[1].withdrawals) == 1
        assert result[1].withdrawals[0].amount == Decimal("500.00")
        
        # Check third deposit
        assert result[2].id == 3
        assert result[2].planType == "premium"
```

### 5. Schema Validation Tests

```python
# tests/application/test_schemas.py
import pytest
from decimal import Decimal
from datetime import date
from pydantic import ValidationError

from app.application.schemas.time_deposit import (
    WithdrawalResponse,
    TimeDepositResponse,
    UpdateBalancesResponse
)

class TestSchemas:
    
    def test_withdrawal_response_validation(self):
        # Valid data
        withdrawal = WithdrawalResponse(
            id=1,
            amount=Decimal("100.50"),
            date=date(2024, 1, 15)
        )
        assert withdrawal.amount == Decimal("100.50")
        
        # Invalid data - missing required field
        with pytest.raises(ValidationError):
            WithdrawalResponse(id=1, amount=Decimal("100.00"))
    
    def test_time_deposit_response_validation(self):
        # Valid data with withdrawals
        deposit = TimeDepositResponse(
            id=1,
            planType="basic",
            balance=Decimal("1000.00"),
            days=30,
            withdrawals=[
                WithdrawalResponse(
                    id=1,
                    amount=Decimal("100.00"),
                    date=date(2024, 1, 15)
                )
            ]
        )
        assert deposit.planType == "basic"
        assert len(deposit.withdrawals) == 1
        
        # Valid data without withdrawals (should default to empty list)
        deposit2 = TimeDepositResponse(
            id=2,
            planType="student",
            balance=Decimal("2000.00"),
            days=60
        )
        assert deposit2.withdrawals == []
    
    def test_update_response_validation(self):
        # Valid response
        response = UpdateBalancesResponse(
            success=True,
            message="Updated 5 deposits",
            updated_count=5,
            timestamp=date.today()
        )
        assert response.success is True
        assert response.updated_count == 5
```