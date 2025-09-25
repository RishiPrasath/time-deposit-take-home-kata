from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.infrastructure.database.connection import Base


class TimeDepositModel(Base):
    """
    SQLAlchemy model for time deposits table.

    Represents a time deposit account with a specific plan type,
    number of days active, and current balance.
    """
    __tablename__ = "timeDeposits"

    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Plan type: must be one of 'basic', 'student', or 'premium'
    planType = Column(
        String(50),
        nullable=False,
        index=True
    )

    # Number of days the deposit has been active
    days = Column(
        Integer,
        nullable=False
    )

    # Current balance of the deposit
    balance = Column(
        Numeric(15, 2),
        nullable=False
    )

    # Relationship to withdrawals (one-to-many)
    withdrawals = relationship(
        "WithdrawalModel",
        back_populates="timeDeposit",
        cascade="all, delete-orphan",
        lazy="select"
    )

    # Table-level constraints
    __table_args__ = (
        CheckConstraint(
            "planType IN ('basic', 'student', 'premium')",
            name="check_plan_type"
        ),
        CheckConstraint(
            "days >= 0",
            name="check_days_positive"
        ),
        CheckConstraint(
            "balance >= 0",
            name="check_balance_positive"
        ),
    )

    def __repr__(self):
        return f"<TimeDeposit(id={self.id}, planType={self.planType}, balance={self.balance}, days={self.days})>"


class WithdrawalModel(Base):
    """
    SQLAlchemy model for withdrawals table.

    Represents a withdrawal transaction from a time deposit account.
    """
    __tablename__ = "withdrawals"

    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Foreign key to time deposits table
    timeDepositId = Column(
        Integer,
        ForeignKey("timeDeposits.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Amount withdrawn
    amount = Column(
        Numeric(15, 2),
        nullable=False
    )

    # Date of withdrawal
    date = Column(
        Date,
        nullable=False,
        index=True
    )

    # Relationship to time deposit (many-to-one)
    timeDeposit = relationship(
        "TimeDepositModel",
        back_populates="withdrawals"
    )

    # Table-level constraints
    __table_args__ = (
        CheckConstraint(
            "amount > 0",
            name="check_amount_positive"
        ),
    )

    def __repr__(self):
        return f"<Withdrawal(id={self.id}, timeDepositId={self.timeDepositId}, amount={self.amount}, date={self.date})>"