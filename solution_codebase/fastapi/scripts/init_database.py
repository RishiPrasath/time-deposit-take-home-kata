#!/usr/bin/env python3
"""
Database initialization script.

This script sets up the database with tables and optional sample data.
"""

import sys
import os

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database.connection import engine, init_database
from app.infrastructure.database.repositories.time_deposit_repository import TimeDepositRepository
from app.infrastructure.database.connection import SessionLocal
from app.infrastructure.database.models import Base


def create_tables():
    """Create all database tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully")


def insert_sample_data():
    """Insert sample data for testing."""
    print("\nInserting sample data...")
    db = SessionLocal()
    try:
        repo = TimeDepositRepository(db)
        repo.create_sample_data()
        print("✅ Sample data inserted successfully")

        # Display summary
        deposits = repo.get_all_with_withdrawals()
        print(f"\n📊 Database Summary:")
        print(f"  - Total Time Deposits: {len(deposits)}")

        withdrawal_count = sum(len(d.withdrawals) for d in deposits)
        print(f"  - Total Withdrawals: {withdrawal_count}")

        for deposit in deposits:
            print(f"\n  Deposit #{deposit.id}:")
            print(f"    - Plan Type: {deposit.planType}")
            print(f"    - Balance: ${deposit.balance:.2f}")
            print(f"    - Days: {deposit.days}")
            print(f"    - Withdrawals: {len(deposit.withdrawals)}")

    finally:
        db.close()


def main():
    """Main function."""
    print("=" * 60)
    print("DATABASE INITIALIZATION SCRIPT")
    print("=" * 60)

    try:
        # Create tables
        create_tables()

        # Ask user if they want sample data
        response = input("\nDo you want to insert sample data? (y/n): ")
        if response.lower() == 'y':
            insert_sample_data()

        print("\n" + "=" * 60)
        print("✨ Database initialization completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()