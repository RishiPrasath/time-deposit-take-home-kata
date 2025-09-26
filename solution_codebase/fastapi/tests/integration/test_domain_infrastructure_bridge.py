"""
Integration tests for Phase 1 ↔ Phase 2 bridge

These tests verify that the adapter correctly converts between:
- SQLAlchemy models (infrastructure layer)
- Domain entities (domain layer)

And that the integration preserves business logic functionality.
"""
import pytest
from decimal import Decimal
from datetime import date
from unittest.mock import Mock, MagicMock

from app.domain.entities.time_deposit import TimeDeposit, TimeDepositCalculator
from app.domain.entities.withdrawal import Withdrawal
from app.infrastructure.database.models import TimeDepositModel, WithdrawalModel
from app.infrastructure.adapters.time_deposit_repository_adapter import TimeDepositRepositoryAdapter


class TestModelToDomainConversion:
    """Test SQLAlchemy model to domain entity conversion"""

    def test_model_to_domain_conversion(self):
        """Test SQLAlchemy model converts correctly to domain entity"""
        # Create SQLAlchemy model (Phase 1)
        model = TimeDepositModel(
            id=1,
            planType="basic",
            balance=Decimal("1000.00"),
            days=45
        )

        # Mock repository
        mock_repo = Mock()
        adapter = TimeDepositRepositoryAdapter(mock_repo)

        # Convert via adapter
        domain = adapter._model_to_domain(model)

        # Verify domain entity
        assert isinstance(domain, TimeDeposit)
        assert domain.id == 1
        assert domain.planType == "basic"
        assert domain.balance == 1000.0  # Decimal → float
        assert domain.days == 45
        assert domain.withdrawals == []  # Should be initialized empty

    def test_model_to_domain_with_withdrawals(self):
        """Test conversion with withdrawals included"""
        # Create models with relationships
        withdrawal_model = WithdrawalModel(
            id=1,
            timeDepositId=1,
            amount=Decimal("500.00"),
            date=date(2024, 1, 15)
        )

        deposit_model = TimeDepositModel(
            id=1,
            planType="premium",
            balance=Decimal("2000.00"),
            days=60
        )
        deposit_model.withdrawals = [withdrawal_model]

        # Mock repository
        mock_repo = Mock()
        adapter = TimeDepositRepositoryAdapter(mock_repo)

        # Convert via adapter
        domain = adapter._model_to_domain_with_withdrawals(deposit_model)

        # Verify domain entity
        assert isinstance(domain, TimeDeposit)
        assert domain.id == 1
        assert domain.planType == "premium"
        assert domain.balance == 2000.0
        assert domain.days == 60

        # Verify withdrawals conversion
        assert len(domain.withdrawals) == 1
        withdrawal = domain.withdrawals[0]
        assert isinstance(withdrawal, Withdrawal)
        assert withdrawal.id == 1
        assert withdrawal.amount == 500.0  # Decimal → float
        assert withdrawal.date == "2024-01-15"  # Date → ISO string

    def test_domain_to_model_new_entity(self):
        """Test domain entity to SQLAlchemy model conversion (new entity)"""
        # Create domain entity
        domain = TimeDeposit(
            id=None,  # New entity
            planType="student",
            balance=1500.0,
            days=120
        )

        # Mock repository and database query
        mock_repo = Mock()
        mock_repo.db.query.return_value.filter.return_value.first.return_value = None
        adapter = TimeDepositRepositoryAdapter(mock_repo)

        # Convert via adapter
        model = adapter._domain_to_model(domain)

        # Verify model
        assert isinstance(model, TimeDepositModel)
        assert model.id is None  # New entity
        assert model.planType == "student"
        assert model.balance == Decimal("1500.0")  # float → Decimal
        assert model.days == 120

    def test_domain_to_model_existing_entity(self):
        """Test domain entity to model conversion (existing entity update)"""
        # Create existing model
        existing_model = TimeDepositModel(
            id=1,
            planType="basic",
            balance=Decimal("1000.00"),
            days=45
        )

        # Create domain entity with updated balance
        domain = TimeDeposit(
            id=1,
            planType="basic",
            balance=1008.33,  # Updated by calculator
            days=45
        )

        # Mock repository and database query
        mock_repo = Mock()
        mock_repo.db.query.return_value.filter.return_value.first.return_value = existing_model
        adapter = TimeDepositRepositoryAdapter(mock_repo)

        # Convert via adapter
        model = adapter._domain_to_model(domain)

        # Should return updated existing model
        assert model is existing_model
        assert model.id == 1
        assert model.balance == Decimal("1008.33")  # Updated balance
        assert model.planType == "basic"
        assert model.days == 45


class TestAdapterIntegration:
    """Test full adapter integration with mocked repository"""

    def test_get_all_integration(self):
        """Test get_all method integration"""
        # Mock repository with sample data
        mock_models = [
            TimeDepositModel(id=1, planType="basic", balance=Decimal("1000.00"), days=45),
            TimeDepositModel(id=2, planType="student", balance=Decimal("2000.00"), days=180)
        ]

        mock_repo = Mock()
        mock_repo.get_all.return_value = mock_models
        adapter = TimeDepositRepositoryAdapter(mock_repo)

        # Get all via adapter
        domains = adapter.get_all()

        # Verify conversion
        assert len(domains) == 2
        assert all(isinstance(d, TimeDeposit) for d in domains)
        assert domains[0].balance == 1000.0
        assert domains[1].balance == 2000.0
        mock_repo.get_all.assert_called_once()

    def test_save_all_integration(self):
        """Test save_all method integration"""
        # Create domain entities with updated balances
        domains = [
            TimeDeposit(id=1, planType="basic", balance=1008.33, days=45),
            TimeDeposit(id=2, planType="student", balance=2050.00, days=180)
        ]

        # Mock repository
        mock_repo = Mock()
        mock_repo.db.query.return_value.filter.return_value.first.return_value = None
        mock_repo.save_all_models = Mock()
        adapter = TimeDepositRepositoryAdapter(mock_repo)

        # Save via adapter
        adapter.save_all(domains)

        # Verify save_all_models was called with converted models
        mock_repo.save_all_models.assert_called_once()
        saved_models = mock_repo.save_all_models.call_args[0][0]
        assert len(saved_models) == 2
        assert all(isinstance(m, TimeDepositModel) for m in saved_models)


class TestBusinessLogicWithAdapter:
    """Test that business logic works with adapter-converted data"""

    def test_business_logic_with_adapter_data(self):
        """
        CRITICAL TEST: Verify original business logic works with adapter data

        This tests the complete flow:
        1. Mock database data → SQLAlchemy models
        2. Adapter converts models → domain entities
        3. Original calculator processes domain entities
        4. Adapter converts updated entities → models
        """
        # Mock database models
        mock_models = [
            TimeDepositModel(id=1, planType="basic", balance=Decimal("1000.00"), days=45),
            TimeDepositModel(id=2, planType="student", balance=Decimal("2000.00"), days=180),
            TimeDepositModel(id=3, planType="premium", balance=Decimal("3000.00"), days=60)
        ]

        # Mock existing models for updates
        existing_models = {
            1: mock_models[0],
            2: mock_models[1],
            3: mock_models[2]
        }

        # Mock repository
        mock_repo = Mock()
        mock_repo.get_all.return_value = mock_models
        mock_repo.save_all_models = Mock()

        # Mock database queries for existing entities
        def mock_query_side_effect(model_class):
            mock_query = Mock()

            def mock_filter_side_effect(condition):
                # Extract the ID from the condition
                # This is a simplified mock - in real tests you'd need more sophisticated mocking
                mock_filtered = Mock()
                mock_filtered.first.return_value = existing_models.get(1) if "1" in str(condition) else \
                    existing_models.get(2) if "2" in str(condition) else existing_models.get(3)
                return mock_filtered

            mock_query.filter.side_effect = mock_filter_side_effect
            return mock_query

        mock_repo.db.query.side_effect = mock_query_side_effect

        adapter = TimeDepositRepositoryAdapter(mock_repo)

        # Step 1: Get data via adapter (models → domain entities)
        domains = adapter.get_all()

        # Step 2: Apply original business logic
        calculator = TimeDepositCalculator()
        calculator.update_balance(domains)

        # Step 3: Save updated data via adapter (domain entities → models)
        adapter.save_all(domains)

        # Verify the flow worked
        mock_repo.get_all.assert_called_once()
        mock_repo.save_all_models.assert_called_once()

        # Verify business logic was applied (cumulative interest behavior)
        # The interest accumulates step by step in the loop
        interest_step1 = (1000.0 * 0.01) / 12  # 0.833...
        interest_step2 = interest_step1 + (2000.0 * 0.03) / 12  # 5.833...
        interest_step3 = interest_step2 + (3000.0 * 0.05) / 12  # 18.333...

        expected_balances = [
            round(1000.0 + ((interest_step1 * 100) / 100), 2),
            round(2000.0 + ((interest_step2 * 100) / 100), 2),
            round(3000.0 + ((interest_step3 * 100) / 100), 2)
        ]

        for i, domain in enumerate(domains):
            assert domain.balance == expected_balances[i]

        print(f"End-to-end integration test passed!")
        print(f"Interest steps: {interest_step1:.6f}, {interest_step2:.6f}, {interest_step3:.6f}")
        print(f"Final balances: {[d.balance for d in domains]}")


def test_data_type_conversions():
    """Test critical data type conversions"""
    # Test Decimal ↔ float conversions
    original_decimal = Decimal("1234.56")
    converted_float = float(original_decimal)
    back_to_decimal = Decimal(str(converted_float))

    assert converted_float == 1234.56
    assert back_to_decimal == Decimal("1234.56")

    # Test date → ISO string conversion
    test_date = date(2024, 3, 15)
    iso_string = test_date.isoformat()
    assert iso_string == "2024-03-15"

    print("Data type conversions work correctly")


if __name__ == "__main__":
    """Run integration tests manually"""
    print("Running Integration Bridge Tests...")

    # Run tests
    test_converter = TestModelToDomainConversion()
    test_converter.test_model_to_domain_conversion()
    test_converter.test_model_to_domain_with_withdrawals()
    test_converter.test_domain_to_model_new_entity()
    test_converter.test_domain_to_model_existing_entity()

    test_adapter = TestAdapterIntegration()
    test_adapter.test_get_all_integration()
    test_adapter.test_save_all_integration()

    test_business = TestBusinessLogicWithAdapter()
    test_business.test_business_logic_with_adapter_data()

    test_data_type_conversions()

    print("\nAll integration tests passed! Bridge works correctly.")