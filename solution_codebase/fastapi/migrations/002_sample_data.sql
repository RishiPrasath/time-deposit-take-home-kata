-- Migration 002: Insert Sample Data
-- Creates 9 time deposits and 9 withdrawals for testing

-- Clear existing data (if any)
DELETE FROM withdrawals;
DELETE FROM "timeDeposits";

-- Reset sequences
ALTER SEQUENCE "timeDeposits_id_seq" RESTART WITH 1;
ALTER SEQUENCE withdrawals_id_seq RESTART WITH 1;

-- Insert sample time deposits
INSERT INTO "timeDeposits" (id, "planType", days, balance) VALUES
-- Basic plan deposits
(1, 'basic', 45, 10000.00),    -- Eligible for interest (45 > 30)
(2, 'basic', 25, 5000.50),     -- Not eligible yet (25 < 30)
(3, 'basic', 90, 25000.75),    -- Long-term basic deposit

-- Student plan deposits
(4, 'student', 60, 8000.00),   -- Eligible for student interest
(5, 'student', 400, 15000.25), -- Over 1 year (interest stopped)
(6, 'student', 15, 3000.00),   -- Too early for interest

-- Premium plan deposits
(7, 'premium', 50, 50000.00),  -- Eligible for premium interest (50 > 45)
(8, 'premium', 30, 20000.00),  -- Not eligible yet (30 < 45)
(9, 'premium', 100, 75000.50); -- Long-term premium deposit

-- Update sequence to continue from 10
SELECT setval('"timeDeposits_id_seq"', 9, true);

-- Insert sample withdrawals
INSERT INTO withdrawals (id, "timeDepositId", amount, date) VALUES
-- Withdrawals from basic deposit #1
(1, 1, 500.00, '2024-01-15'),
(2, 1, 200.00, '2024-02-01'),

-- Withdrawals from student deposit #4
(3, 4, 1000.00, '2024-01-20'),
(4, 4, 250.75, '2024-03-05'),

-- Withdrawals from premium deposit #7
(5, 7, 2500.00, '2024-01-10'),
(6, 7, 1000.00, '2024-01-25'),
(7, 7, 500.00, '2024-02-15'),

-- Additional withdrawals for testing
(8, 3, 1500.00, '2024-02-28'),
(9, 5, 750.25, '2024-03-10');

-- Update sequence to continue from 10
SELECT setval('withdrawals_id_seq', 9, true);

-- Verify data insertion
DO $$
DECLARE
    deposit_count INTEGER;
    withdrawal_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO deposit_count FROM "timeDeposits";
    SELECT COUNT(*) INTO withdrawal_count FROM withdrawals;

    RAISE NOTICE 'Sample data inserted successfully:';
    RAISE NOTICE '  - Time Deposits: %', deposit_count;
    RAISE NOTICE '  - Withdrawals: %', withdrawal_count;
END $$;