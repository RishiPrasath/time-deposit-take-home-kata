# Time Deposits for Beginners: What They Are and How They Work

A **time deposit** (also called a Certificate of Deposit or CD) is like a savings account with a twist: you promise to leave your money in the bank for a specific amount of time, and in return, the bank pays you a higher interest rate than a regular savings account. Think of it as making a deal with the bank - "I'll let you use my money for 6 months, and you'll pay me extra for that privilege."

## How Time Deposits Work in Simple Terms

### The Basic Deal
1. **You put money in**: You give the bank some money (could be $500, $5,000, or $50,000)
2. **You pick a time period**: You choose how long to leave it there (3 months, 1 year, 2 years, etc.)
3. **The bank pays you interest**: They give you extra money (like 4% per year) for letting them use your money
4. **You wait**: Your money sits there earning interest until the time is up
5. **You get it back**: When the time is up, you get all your original money PLUS the extra interest money

### Why Do Banks Offer This?
Banks need money to lend to other people (for mortgages, car loans, business loans, etc.). When you put money in a time deposit, you're basically saying "Here's some money you can count on having for the next 12 months." Since the bank knows they'll have your money for a guaranteed period, they can pay you more interest than a regular savings account.

## What Are Withdrawals in Banking?

A **withdrawal** is simply taking money OUT of your account. It's the opposite of a deposit (putting money in).

### Types of Withdrawals in Time Deposits

#### 1. Normal Withdrawal (When Time is Up)
- **When**: After your chosen time period ends (called "maturity")
- **Cost**: No penalty - you get all your money plus interest
- **Example**: You put $10,000 in a 1-year CD at 4% interest. After 1 year, you withdraw $10,400

#### 2. Early Withdrawal (Breaking the Promise)
- **When**: Before your chosen time period ends
- **Cost**: You pay a penalty (like a fee for breaking the deal)
- **Example**: You put $10,000 in a 1-year CD, but need the money after 6 months. You might lose 3 months of interest as a penalty

#### 3. Partial Withdrawal (Taking Some Money Out)
- **When**: Taking out only part of your money early
- **Cost**: Usually the same penalty as early withdrawal
- **Example**: You have $10,000 in a CD but only take out $2,000 early

## Understanding the Database Tables for Your Challenge

Now that you understand the basics, let's look at what the two database tables represent:

### timeDeposits Table - The Main Accounts
This table stores information about each time deposit account:

```
Example Data:
ID: 1
Customer: John Smith  
Amount: $25,000
Plan Type: Basic (1% interest per year)
Days: 45 (how many days since he put the money in)
Current Balance: $25,031.25 (original + interest earned so far)
```

**What this means**: John put $25,000 in a basic plan 45 days ago, and it's earned $31.25 so far.

### withdrawals Table - The Transaction History
This table stores every time someone took money out:

```
Example Data:
Withdrawal ID: 1
Which Account: John's account (ID 1)
Amount Taken: $5,000
Date: March 15, 2024
Type: Early withdrawal (he took it out before time was up)
```

**What this means**: John took out $5,000 from his account on March 15th, and since it was early, he probably paid a penalty.

## The Three Plan Types in Your Challenge

### Basic Plan (1% interest per year)
- **Who it's for**: Regular people, beginners
- **Interest rate**: 1% per year
- **Rules**: No interest for the first 30 days, then 1% starts

### Student Plan (3% interest per year) 
- **Who it's for**: Students (better rate to help them save)
- **Interest rate**: 3% per year
- **Rules**: No interest for first 30 days, stops paying interest after 1 year

### Premium Plan (5% interest per year)
- **Who it's for**: People with lots of money
- **Interest rate**: 5% per year  
- **Rules**: No interest for first 30 days, doesn't start until day 45

## Real-World Example: Sarah's Time Deposit Journey

Let's follow Sarah through a complete time deposit experience:

### Day 0: Sarah Opens Her Account
- Sarah deposits $20,000 into a Student plan
- The bank creates a record in the `timeDeposits` table
- Her balance starts at exactly $20,000
- Days = 0, no interest yet

### Day 35: First Interest Calculation
- Sarah has had the account for 35 days (past the 30-day waiting period)
- Student plan pays 3% per year = 0.25% per month
- Monthly interest = $20,000 × 0.25% = $50
- Her balance becomes $20,050

### Day 120: Sarah Needs Money (Early Withdrawal)
- Sarah needs $5,000 for an emergency
- She makes an early withdrawal
- The bank creates a record in the `withdrawals` table:
  - Amount: $5,000
  - Date: Day 120
  - Type: Early withdrawal
- She pays a penalty (maybe loses 2 months of interest = $100)
- Her remaining balance: $15,050 - $100 penalty = $14,950

### Day 365: One Year Complete
- Student plan stops earning interest after 1 year
- Her final balance stays at whatever it was on day 365
- No more interest from now on (that's the student plan rule)

## Why This System Needs a Database

The bank needs to track:
1. **Who has accounts** (timeDeposits table)
2. **How much money they have**
3. **What type of plan they chose** 
4. **How long they've had the account**
5. **Every time they take money out** (withdrawals table)
6. **Calculate interest properly** based on the rules

## Your Coding Challenge in Simple Terms

You're building a system that:
1. **Stores time deposit accounts** in a database (like Sarah's account above)
2. **Tracks withdrawals** in another database table
3. **Calculates interest** using the existing calculator (already built for you!)
4. **Provides two web endpoints**:
   - One to update all account balances (add interest to everyone's accounts)
   - One to show all accounts and their withdrawal history

**The key insight**: You're not building the interest calculation (that's done). You're building the web interface and database storage around the existing calculation logic.

Think of it like building a website interface for a calculator that already works perfectly - you just need to save the data and show it to users through web pages.
