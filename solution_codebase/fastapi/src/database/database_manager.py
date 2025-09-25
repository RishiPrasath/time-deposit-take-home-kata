# database_manager.py - Database connection, table creation, and data display
import sqlite3
import os
from decimal import Decimal
from datetime import datetime

# Database file path
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "time_deposits.db")

def establish_connection():
    """
    Establish connection to SQLite database.
    Returns connection object or None if failed.
    """
    try:
        print("[INFO] Establishing database connection...")
        conn = sqlite3.connect(DATABASE_PATH)
        conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
        print(f"[SUCCESS] Connected to database: {DATABASE_PATH}")
        return conn
    except Exception as e:
        print(f"[ERROR] Failed to connect to database: {e}")
        return None

def create_tables_if_not_exists(conn):
    """
    Create tables if they don't exist.
    """
    cursor = conn.cursor()
    
    try:
        print("\n[INFO] Creating tables if they don't exist...")
        
        # Create timeDeposits table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS timeDeposits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                planType VARCHAR(50) NOT NULL,
                days INTEGER NOT NULL,
                balance DECIMAL(15,2) NOT NULL
            )
        ''')
        print("[SUCCESS] timeDeposits table ready")
        
        # Create withdrawals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS withdrawals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timeDepositId INTEGER NOT NULL,
                amount DECIMAL(15,2) NOT NULL,
                date DATE NOT NULL,
                FOREIGN KEY (timeDepositId) REFERENCES timeDeposits(id)
            )
        ''')
        print("[SUCCESS] withdrawals table ready")
        
        # Commit the changes
        conn.commit()
        print("[SUCCESS] Tables created successfully")
        
    except Exception as e:
        print(f"[ERROR] Error creating tables: {e}")
        return False
    
    return True

def display_all_data(conn):
    """
    Select and display all data from both tables.
    """
    cursor = conn.cursor()
    
    try:
        print("\n" + "="*60)
        print("DATABASE DATA DISPLAY")
        print("="*60)
        
        # Display timeDeposits data
        print("\nTIME DEPOSITS TABLE:")
        print("-" * 50)
        cursor.execute("SELECT * FROM timeDeposits ORDER BY id")
        deposits = cursor.fetchall()
        
        if deposits:
            print(f"{'ID':<4} {'Plan Type':<12} {'Days':<8} {'Balance':<15}")
            print("-" * 50)
            for deposit in deposits:
                print(f"{deposit[0]:<4} {deposit[1]:<12} {deposit[2]:<8} ${deposit[3]:>12.2f}")
            print(f"\nTotal deposits: {len(deposits)}")
        else:
            print("[INFO] No time deposits found")
        
        # Display withdrawals data
        print("\nWITHDRAWALS TABLE:")
        print("-" * 60)
        cursor.execute("SELECT * FROM withdrawals ORDER BY timeDepositId, date")
        withdrawals = cursor.fetchall()
        
        if withdrawals:
            print(f"{'ID':<4} {'Deposit ID':<12} {'Amount':<15} {'Date':<12}")
            print("-" * 60)
            for withdrawal in withdrawals:
                print(f"{withdrawal[0]:<4} {withdrawal[1]:<12} ${withdrawal[2]:>12.2f} {withdrawal[3]:<12}")
            print(f"\nTotal withdrawals: {len(withdrawals)}")
        else:
            print("[INFO] No withdrawals found")
        
        # Display summary with JOIN
        print("\nSUMMARY (Deposits with Withdrawals):")
        print("-" * 80)
        cursor.execute('''
            SELECT 
                td.id, 
                td.planType, 
                td.balance, 
                td.days,
                COUNT(w.id) as withdrawal_count,
                COALESCE(SUM(w.amount), 0) as total_withdrawn
            FROM timeDeposits td
            LEFT JOIN withdrawals w ON td.id = w.timeDepositId
            GROUP BY td.id, td.planType, td.balance, td.days
            ORDER BY td.id
        ''')
        
        summary = cursor.fetchall()
        if summary:
            print(f"{'ID':<4} {'Type':<10} {'Balance':<12} {'Days':<6} {'Withdrawals':<12} {'Total Withdrawn':<15}")
            print("-" * 80)
            for row in summary:
                print(f"{row[0]:<4} {row[1]:<10} ${row[2]:>9.2f} {row[3]:<6} {row[4]:<12} ${row[5]:>12.2f}")
        
    except Exception as e:
        print(f"[ERROR] Error displaying data: {e}")
        return False
    
    return True

def main():
    """
    Main function to run all database operations.
    """
    print("Starting Database Manager")
    print("="*60)
    
    # Step 1: Establish connection
    conn = establish_connection()
    if not conn:
        print("[ERROR] Cannot proceed without database connection")
        return
    
    try:
        # Step 2: Create tables if not exists
        if not create_tables_if_not_exists(conn):
            print("[ERROR] Failed to create tables")
            return
        
        # Step 3: Display all data
        if not display_all_data(conn):
            print("[ERROR] Failed to display data")
            return
        
        print("\n" + "="*60)
        print("[SUCCESS] Database operations completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
    
    finally:
        # Always close the connection
        conn.close()
        print("\n[INFO] Database connection closed")

if __name__ == "__main__":
    main()
