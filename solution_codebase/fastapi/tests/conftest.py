"""
Test configuration and fixtures for pytest.
"""

import pytest
from typing import Generator
from datetime import date
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from src.infrastructure.database.models import Base, TimeDepositModel, WithdrawalModel


# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_engine():
    """Create a test database engine."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    return engine


@pytest.fixture(scope="function")
def test_db(test_engine) -> Generator[Session, None, None]:
    """
    Create a test database session.

    This fixture creates a fresh database for each test,
    ensuring test isolation.
    """
    # Create tables
    Base.metadata.create_all(bind=test_engine)

    # Create session
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    db = TestSessionLocal()

    try:
        yield db
    finally:
        db.close()
        # Drop tables after test
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def sample_deposits(test_db: Session) -> list[TimeDepositModel]:
    """
    Create sample time deposits for testing.

    Returns a list of time deposit models that have been
    added to the test database.
    """
    deposits = [
        TimeDepositModel(
            planType='basic',
            days=45,
            balance=Decimal('10000.00')
        ),
        TimeDepositModel(
            planType='student',
            days=60,
            balance=Decimal('8000.00')
        ),
        TimeDepositModel(
            planType='premium',
            days=50,
            balance=Decimal('50000.00')
        ),
    ]

    for deposit in deposits:
        test_db.add(deposit)

    test_db.commit()

    # Refresh to get IDs
    for deposit in deposits:
        test_db.refresh(deposit)

    return deposits


@pytest.fixture
def sample_withdrawals(test_db: Session, sample_deposits: list[TimeDepositModel]) -> list[WithdrawalModel]:
    """
    Create sample withdrawals for testing.

    Depends on sample_deposits fixture to ensure deposits exist first.
    """
    withdrawals = [
        WithdrawalModel(
            timeDepositId=sample_deposits[0].id,
            amount=Decimal('500.00'),
            date=date(2024, 1, 15)
        ),
        WithdrawalModel(
            timeDepositId=sample_deposits[0].id,
            amount=Decimal('200.00'),
            date=date(2024, 2, 1)
        ),
        WithdrawalModel(
            timeDepositId=sample_deposits[1].id,
            amount=Decimal('1000.00'),
            date=date(2024, 1, 20)
        ),
    ]

    for withdrawal in withdrawals:
        test_db.add(withdrawal)

    test_db.commit()

    # Refresh to get IDs
    for withdrawal in withdrawals:
        test_db.refresh(withdrawal)

    return withdrawals


@pytest.fixture
def empty_db(test_db: Session) -> Session:
    """
    Provide an empty test database session.

    This is useful for tests that need to start with no data.
    """
    return test_db


@pytest.fixture
def populated_db(test_db: Session, sample_deposits: list[TimeDepositModel],
                sample_withdrawals: list[WithdrawalModel]) -> Session:
    """
    Provide a test database with sample data.

    This fixture ensures both deposits and withdrawals are created
    before the test runs.
    """
    return test_db