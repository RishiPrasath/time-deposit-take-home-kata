import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decimal import Decimal
from datetime import date

from app.infrastructure.database.models import Base, TimeDepositModel, WithdrawalModel
from app.infrastructure.database.repositories.time_deposit_repository import TimeDepositRepository
from app.infrastructure.adapters.time_deposit_repository_adapter import TimeDepositRepositoryAdapter
from app.application.services.time_deposit_service import TimeDepositService

class TestServiceIntegration:

    @pytest.fixture
    def test_db(self):
        """Create in-memory SQLite database for testing"""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        return SessionLocal()

    @pytest.fixture
    def service(self, test_db):
        """Create service with real repository chain"""
        sql_repo = TimeDepositRepository(test_db)
        adapter = TimeDepositRepositoryAdapter(sql_repo)
        return TimeDepositService(adapter)

    def test_full_update_workflow(self, service, test_db):
        # Create test data
        deposits = [
            TimeDepositModel(planType="basic", balance=Decimal("1000.00"), days=45),
            TimeDepositModel(planType="student", balance=Decimal("2000.00"), days=90)
        ]
        test_db.add_all(deposits)
        test_db.commit()

        # Store original balances
        original_balances = [d.balance for d in deposits]

        # Update balances
        result = service.update_all_balances()

        # Verify
        assert result.success is True
        assert result.updated_count > 0

        # Check updated balances in database
        updated_deposits = test_db.query(TimeDepositModel).all()
        for i, deposit in enumerate(updated_deposits):
            # Balance should have increased due to interest
            assert deposit.balance > original_balances[i]

    def test_get_all_deposits_integration(self, service, test_db):
        # Create test data with withdrawal
        deposit = TimeDepositModel(planType="basic", balance=Decimal("1000.00"), days=45)
        test_db.add(deposit)
        test_db.commit()

        withdrawal = WithdrawalModel(
            timeDepositId=deposit.id,
            amount=Decimal("100.00"),
            date=date.today()
        )
        test_db.add(withdrawal)
        test_db.commit()

        # Test service
        result = service.get_all_deposits()

        # Verify
        assert len(result) == 1
        assert result[0].id == deposit.id
        assert result[0].planType == "basic"
        assert len(result[0].withdrawals) == 1