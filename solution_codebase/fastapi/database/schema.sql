-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- timeDeposits table
CREATE TABLE timeDeposits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    planType VARCHAR(50) NOT NULL,
    days INTEGER NOT NULL,
    balance DECIMAL(10,2) NOT NULL
);

-- withdrawals table
CREATE TABLE withdrawals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timeDepositId INTEGER NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    date DATE NOT NULL,
    FOREIGN KEY (timeDepositId) REFERENCES timeDeposits(id)
);

-- Sample data for timeDeposits
INSERT INTO timeDeposits (planType, days, balance) VALUES
('basic', 60, 10000.00),
('student', 100, 5000.00),
('premium', 50, 20000.00),
('basic', 200, 15000.00);

-- Sample data for withdrawals
INSERT INTO withdrawals (timeDepositId, amount, date) VALUES
(1, 500.00, '2024-03-15'),
(1, 200.00, '2024-04-01'),
(2, 100.00, '2024-03-20'),
(4, 1000.00, '2024-02-10');