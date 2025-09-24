import sqlite3
import os

print("=== SQLite Database Setup and Test ===\n")

# Remove old database if it exists
if os.path.exists('time_deposits.db'):
    os.remove('time_deposits.db')
    print("Removed old database file")

# Create database
print("1. Creating fresh database...")
conn = sqlite3.connect('time_deposits.db')
cursor = conn.cursor()

# Enable foreign key constraints
cursor.execute("PRAGMA foreign_keys = ON")

# Create timeDeposits table
print("2. Creating timeDeposits table...")
cursor.execute('''
    CREATE TABLE timeDeposits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        planType VARCHAR(50) NOT NULL,
        days INTEGER NOT NULL,
        balance DECIMAL(10,2) NOT NULL
    )
''')

# Create withdrawals table
print("3. Creating withdrawals table...")
cursor.execute('''
    CREATE TABLE withdrawals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timeDepositId INTEGER NOT NULL,
        amount DECIMAL(10,2) NOT NULL,
        date DATE NOT NULL,
        FOREIGN KEY (timeDepositId) REFERENCES timeDeposits(id)
    )
''')

# Insert sample time deposits
print("4. Inserting sample time deposits...")
sample_deposits = [
    ('basic', 60, 10000.00),
    ('student', 100, 5000.00),
    ('premium', 50, 20000.00),
    ('basic', 200, 15000.00)
]

cursor.executemany('INSERT INTO timeDeposits (planType, days, balance) VALUES (?, ?, ?)', sample_deposits)

# Get the inserted IDs to show
cursor.execute("SELECT id FROM timeDeposits ORDER BY id")
deposit_ids = [row[0] for row in cursor.fetchall()]
print(f"   Created deposits with IDs: {deposit_ids}")

# Insert sample withdrawals
print("5. Inserting sample withdrawals...")
sample_withdrawals = [
    (1, 500.00, '2024-03-15'),
    (1, 200.00, '2024-04-01'),
    (2, 100.00, '2024-03-20'),
    (4, 1000.00, '2024-02-10')
]

cursor.executemany('INSERT INTO withdrawals (timeDepositId, amount, date) VALUES (?, ?, ?)', sample_withdrawals)

# Commit all changes
conn.commit()

print("\n=== DATABASE TESTING ===\n")

# Test 1: Check if tables exist
print("TEST 1: Checking if tables exist...")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for table in tables:
    print(f"  [OK] Table: {table[0]}")

# Test 2: Count records
print()
print("TEST 2: Counting records...")
cursor.execute("SELECT COUNT(*) FROM timeDeposits")
deposit_count = cursor.fetchone()[0]
print(f"  [OK] Time deposits: {deposit_count}")

cursor.execute("SELECT COUNT(*) FROM withdrawals")
withdrawal_count = cursor.fetchone()[0]
print(f"  [OK] Withdrawals: {withdrawal_count}")

# Test 3: Show all time deposits
print()
print("TEST 3: All time deposits:")
cursor.execute("SELECT id, planType, days, balance FROM timeDeposits ORDER BY id")
deposits = cursor.fetchall()
for deposit in deposits:
    print(f"  ID: {deposit[0]} | Type: {deposit[1]} | Days: {deposit[2]} | Balance: ${deposit[3]:.2f}")

# Test 4: Show all withdrawals
print()
print("TEST 4: All withdrawals:")
cursor.execute("SELECT id, timeDepositId, amount, date FROM withdrawals ORDER BY timeDepositId, date")
withdrawals = cursor.fetchall()
for withdrawal in withdrawals:
    print(f"  ID: {withdrawal[0]} | DepositID: {withdrawal[1]} | Amount: ${withdrawal[2]:.2f} | Date: {withdrawal[3]}")

# Test 5: JOIN query (what your API will do)
print()
print("TEST 5: JOIN query (deposits with withdrawals):")
cursor.execute('''
    SELECT 
        td.id, 
        td.planType, 
        td.balance, 
        td.days,
        w.id as withdrawal_id,
        w.amount as withdrawal_amount,
        w.date as withdrawal_date
    FROM timeDeposits td
    LEFT JOIN withdrawals w ON td.id = w.timeDepositId
    ORDER BY td.id, w.date
''')

results = cursor.fetchall()
current_deposit = None
for row in results:
    if current_deposit != row[0]:
        current_deposit = row[0]
        print(f"  Deposit {row[0]} ({row[1]}): ${row[2]:.2f}, {row[3]} days")
    
    if row[4] is not None:
        print(f"    -> Withdrawal {row[4]}: ${row[5]:.2f} on {row[6]}")

# Test 6: Verify foreign key constraints work
print()
print("TEST 6: Testing foreign key constraints...")
try:
    cursor.execute("INSERT INTO withdrawals (timeDepositId, amount, date) VALUES (999, 100.00, '2024-01-01')")
    conn.commit()
    print("  [ERROR] Foreign key constraint NOT working")
except sqlite3.IntegrityError:
    print("  [OK] Foreign key constraint working")

conn.close()

# Check file was created
file_size = os.path.getsize('time_deposits.db')
print()
print(f"[SUCCESS] Database file created: time_deposits.db ({file_size} bytes)")
print()
print("*** All tests completed successfully! ***")