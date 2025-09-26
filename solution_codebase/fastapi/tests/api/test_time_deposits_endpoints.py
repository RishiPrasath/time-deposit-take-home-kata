"""
Tests for Time Deposits API endpoints with clean architecture integration.
"""
import pytest
from fastapi.testclient import TestClient
from decimal import Decimal
from datetime import date

from src.main import app
from src.infrastructure.database.connection import Base
from src.infrastructure.database.models import TimeDepositModel, WithdrawalModel
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Create a separate test database
test_engine = create_engine(
    "sqlite:///./test_api.db",
    connect_args={"check_same_thread": False}
)

TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Override the dependency in the app
def get_test_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

from src.dependencies import get_database
app.dependency_overrides[get_database] = get_test_db

client = TestClient(app)

@pytest.fixture(scope="function")
def setup_database():
    """Create tables and provide a clean database for each test."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def sample_time_deposits(setup_database):
    """Create sample time deposits in the database."""
    db = TestSessionLocal()
    try:
        # Create sample time deposits
        deposits = [
            TimeDepositModel(
                id=1,
                planType="basic",
                balance=Decimal("1000.00"),
                days=35
            ),
            TimeDepositModel(
                id=2,
                planType="student",
                balance=Decimal("2000.00"),
                days=40
            ),
            TimeDepositModel(
                id=3,
                planType="premium",
                balance=Decimal("3000.00"),
                days=50
            ),
        ]

        for deposit in deposits:
            db.add(deposit)

        # Add some withdrawals
        withdrawals = [
            WithdrawalModel(
                id=1,
                timeDepositId=1,
                amount=Decimal("100.00"),
                date=date(2024, 1, 15)
            ),
            WithdrawalModel(
                id=2,
                timeDepositId=2,
                amount=Decimal("200.00"),
                date=date(2024, 1, 20)
            ),
        ]

        for withdrawal in withdrawals:
            db.add(withdrawal)

        db.commit()
        return deposits
    finally:
        db.close()

class TestTimeDepositsEndpoints:
    """Test suite for time deposits API endpoints."""

    def test_root_endpoint(self):
        """Test the root endpoint returns correct information."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Ikigai Time Deposit API is running!" in data["message"]
        assert data["architecture"] == "Clean Architecture with FastAPI"
        assert "endpoints" in data

    def test_health_endpoint(self):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["architecture"] == "Clean Architecture"

    def test_get_all_deposits_empty(self, setup_database):
        """Test getting all deposits when database is empty."""
        response = client.get("/time-deposits")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_all_deposits_with_data(self, sample_time_deposits):
        """Test getting all deposits with sample data."""
        response = client.get("/time-deposits")
        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) == 3

        # Check first deposit
        first_deposit = data[0]
        assert first_deposit["id"] == 1
        assert first_deposit["planType"] == "basic"
        assert float(first_deposit["balance"]) == 1000.00
        assert first_deposit["days"] == 35
        assert len(first_deposit["withdrawals"]) == 1

        # Check withdrawal format
        withdrawal = first_deposit["withdrawals"][0]
        assert withdrawal["id"] == 1
        assert float(withdrawal["amount"]) == 100.00
        assert withdrawal["date"] == "2024-01-15"

    def test_update_balances_empty(self, setup_database):
        """Test updating balances when database is empty."""
        response = client.put("/time-deposits/updateBalances")
        assert response.status_code == 200
        data = response.json()
        assert data["updatedCount"] == 0
        assert "success" in data["status"]

    def test_update_balances_with_data(self, sample_time_deposits):
        """Test updating balances with sample data."""
        response = client.put("/time-deposits/updateBalances")
        assert response.status_code == 200
        data = response.json()

        # Should update deposits that meet interest criteria
        assert data["updatedCount"] >= 0
        assert "success" in data["status"]
        assert "message" in data

        # Verify balances were updated by fetching deposits
        response = client.get("/time-deposits")
        deposits = response.json()

        # Basic plan (35 days) should get 1% monthly interest
        basic_deposit = next(d for d in deposits if d["id"] == 1)
        assert float(basic_deposit["balance"]) > 1000.00

        # Student plan (40 days) should get 3% monthly interest
        student_deposit = next(d for d in deposits if d["id"] == 2)
        assert float(student_deposit["balance"]) > 2000.00

        # Premium plan (50 days) should get 5% monthly interest (after 45 days)
        premium_deposit = next(d for d in deposits if d["id"] == 3)
        assert float(premium_deposit["balance"]) > 3000.00

    def test_update_balances_no_interest_before_threshold(self, setup_database):
        """Test that no interest is applied before threshold days."""
        db = TestSessionLocal()
        try:
            # Create deposits with days below threshold
            deposits = [
                TimeDepositModel(
                    id=1,
                    planType="basic",
                    balance=Decimal("1000.00"),
                    days=25  # Below 30 days
                ),
                TimeDepositModel(
                    id=2,
                    planType="premium",
                    balance=Decimal("2000.00"),
                    days=40  # Below 45 days for premium
                ),
            ]

            for deposit in deposits:
                db.add(deposit)
            db.commit()
        finally:
            db.close()

        # Update balances
        response = client.put("/time-deposits/updateBalances")
        assert response.status_code == 200

        # Check balances remain unchanged
        response = client.get("/time-deposits")
        deposits = response.json()

        basic_deposit = next(d for d in deposits if d["id"] == 1)
        assert float(basic_deposit["balance"]) == 1000.00  # No interest

        premium_deposit = next(d for d in deposits if d["id"] == 2)
        assert float(premium_deposit["balance"]) == 2000.00  # No interest yet

    def test_api_response_schema(self, sample_time_deposits):
        """Test that API responses match expected schema."""
        # Test GET /time-deposits schema
        response = client.get("/time-deposits")
        deposits = response.json()

        for deposit in deposits:
            assert "id" in deposit
            assert "planType" in deposit
            assert "balance" in deposit
            assert "days" in deposit
            assert "withdrawals" in deposit
            assert isinstance(deposit["withdrawals"], list)

            for withdrawal in deposit["withdrawals"]:
                assert "id" in withdrawal
                assert "amount" in withdrawal
                assert "date" in withdrawal

        # Test PUT /time-deposits/updateBalances schema
        response = client.put("/time-deposits/updateBalances")
        data = response.json()

        assert "message" in data
        assert "updatedCount" in data
        assert "status" in data