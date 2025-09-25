-- Migration 001: Initialize Database Schema
-- Creates timeDeposits and withdrawals tables with proper constraints

-- Drop tables if they exist (for fresh start)
DROP TABLE IF EXISTS withdrawals CASCADE;
DROP TABLE IF EXISTS "timeDeposits" CASCADE;

-- Create timeDeposits table
CREATE TABLE "timeDeposits" (
    id SERIAL PRIMARY KEY,
    "planType" VARCHAR(50) NOT NULL,
    days INTEGER NOT NULL,
    balance DECIMAL(15,2) NOT NULL,

    -- Constraints
    CONSTRAINT check_plan_type CHECK ("planType" IN ('basic', 'student', 'premium')),
    CONSTRAINT check_days_positive CHECK (days >= 0),
    CONSTRAINT check_balance_positive CHECK (balance >= 0)
);

-- Create withdrawals table
CREATE TABLE withdrawals (
    id SERIAL PRIMARY KEY,
    "timeDepositId" INTEGER NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    date DATE NOT NULL,

    -- Constraints
    CONSTRAINT check_amount_positive CHECK (amount > 0),

    -- Foreign key relationship
    CONSTRAINT fk_time_deposit
        FOREIGN KEY ("timeDepositId")
        REFERENCES "timeDeposits"(id)
        ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX idx_timedeposits_plantype ON "timeDeposits"("planType");
CREATE INDEX idx_withdrawals_timedeposit ON withdrawals("timeDepositId");
CREATE INDEX idx_withdrawals_date ON withdrawals(date);

-- Comments for documentation
COMMENT ON TABLE "timeDeposits" IS 'Stores time deposit accounts with different plan types';
COMMENT ON TABLE withdrawals IS 'Stores withdrawal transactions for time deposits';

COMMENT ON COLUMN "timeDeposits"."planType" IS 'Type of deposit plan: basic, student, or premium';
COMMENT ON COLUMN "timeDeposits".days IS 'Number of days the deposit has been active';
COMMENT ON COLUMN "timeDeposits".balance IS 'Current balance of the deposit';

COMMENT ON COLUMN withdrawals."timeDepositId" IS 'Reference to the parent time deposit';
COMMENT ON COLUMN withdrawals.amount IS 'Amount withdrawn (must be positive)';
COMMENT ON COLUMN withdrawals.date IS 'Date when the withdrawal was made';