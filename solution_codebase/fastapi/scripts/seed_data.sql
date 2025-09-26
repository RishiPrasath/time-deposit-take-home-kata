-- seed_data.sql - Sample data for Time Deposit System
-- This file is executed after init.sql in Docker container

-- Insert sample time deposits
INSERT INTO "timeDeposits" (id, "planType", balance, days) VALUES
(1, 'Basic', 10000.00, 45),
(2, 'Student', 5000.00, 90),
(3, 'Premium', 20000.00, 60),
(4, 'Basic', 15000.00, 365),
(5, 'Student', 3000.00, 180),
(6, 'Premium', 50000.00, 400)
ON CONFLICT (id) DO NOTHING;

-- Insert sample withdrawals
INSERT INTO withdrawals (id, "timeDepositId", amount, date) VALUES
(1, 1, 500.00, '2024-01-15'),
(2, 1, 300.00, '2024-02-20'),
(3, 2, 200.00, '2024-03-10'),
(4, 3, 1000.00, '2024-04-05'),
(5, 4, 750.00, '2024-05-12'),
(6, 5, 150.00, '2024-06-18')
ON CONFLICT (id) DO NOTHING;

-- Reset sequences to ensure proper ID generation
SELECT setval('"timeDeposits_id_seq"', (SELECT MAX(id) FROM "timeDeposits"), true);
SELECT setval('withdrawals_id_seq', (SELECT MAX(id) FROM withdrawals), true);

-- Verify data insertion
DO $$
BEGIN
    RAISE NOTICE 'Sample data inserted successfully!';
    RAISE NOTICE 'Time Deposits count: %', (SELECT COUNT(*) FROM "timeDeposits");
    RAISE NOTICE 'Withdrawals count: %', (SELECT COUNT(*) FROM withdrawals);
END $$;
