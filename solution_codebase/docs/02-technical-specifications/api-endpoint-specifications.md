# API Endpoint Specifications

## 📋 Endpoint Overview

| Endpoint | Method | Purpose | Core Logic |
|----------|--------|---------|------------|
| `/deposits/update-balances` | PUT/POST | Calculate and add monthly interest to all time deposit balances | Use existing `TimeDepositCalculator.update_balance()` |
| `/deposits` | GET | Retrieve all time deposits with withdrawal history | Fetch deposits + related withdrawals from database |

## 🗄️ Database Tables Involved

### timeDeposits Table
```sql
CREATE TABLE timeDeposits (
    id INTEGER PRIMARY KEY,
    planType VARCHAR(50) NOT NULL,    -- 'basic', 'student', 'premium'
    days INTEGER NOT NULL,            -- Days since deposit creation
    balance DECIMAL(10,2) NOT NULL    -- Current balance (gets updated by calculator)
);
```

### withdrawals Table  
```sql
CREATE TABLE withdrawals (
    id INTEGER PRIMARY KEY,
    timeDepositId INTEGER NOT NULL,   -- Foreign key to timeDeposits.id
    amount DECIMAL(10,2) NOT NULL,    -- Amount withdrawn
    date DATE NOT NULL,               -- When withdrawal occurred
    FOREIGN KEY (timeDepositId) REFERENCES timeDeposits(id)
);
```

**Key Relationship**: Each time deposit can have multiple withdrawals (one-to-many)

---

## 🔄 Endpoint 1: Update All Deposit Balances

### Basic Information
- **URL**: `/deposits/update-balances` or `/time-deposits/update-balances`
- **Method**: `PUT` or `POST`
- **Purpose**: Calculate and add monthly interest to all time deposit balances using existing business logic

### Input Specification
| Input Type | Required | Format | Description |
|------------|----------|---------|-------------|
| **Request Body** | ❌ No | `{}` (empty) | No input parameters needed |
| **Headers** | ✅ Yes | `Content-Type: application/json` | Standard JSON headers |

### Process Flow (Step-by-Step)
```
1. 📊 FETCH: SELECT id, planType, days, balance FROM timeDeposits
2. 🔄 CONVERT: Transform database records into TimeDeposit objects
3. ⚡ CALCULATE: Call TimeDepositCalculator.update_balance(deposits[])
   
   For each deposit:
   ├── IF days <= 30: Skip (no interest for first 30 days)
   ├── IF planType = 'basic': Add (balance × 0.01 ÷ 12) interest
   ├── IF planType = 'student' AND days < 366: Add (balance × 0.03 ÷ 12) interest  
   ├── IF planType = 'premium' AND days > 45: Add (balance × 0.05 ÷ 12) interest
   └── UPDATE: balance = balance + calculated_interest (rounded to 2 decimals)

4. 💾 SAVE: UPDATE timeDeposits SET balance = ? WHERE id = ? (for each deposit)
5. ✅ RESPOND: Return success message with count
```

### What Gets Modified
- **✅ MODIFIED**: `timeDeposits.balance` (updated with interest)
- **❌ NOT TOUCHED**: `withdrawals` table (completely unchanged)
- **❌ NOT TOUCHED**: `timeDeposits.id`, `planType`, `days` (only balance changes)

### Interest Calculation Rules
| Plan Type | Annual Rate | Monthly Rate | Conditions |
|-----------|-------------|--------------|------------|
| **Basic** | 1% | 0.083% | After 30 days |
| **Student** | 3% | 0.25% | After 30 days, stops after 365 days |
| **Premium** | 5% | 0.417% | After 45 days (30 day + 15 day delay) |

### Example Process
**Before Update:**
```sql
timeDeposits table:
id | planType | days | balance
1  | basic    | 60   | 10000.00
2  | student  | 100  | 5000.00
3  | premium  | 50   | 20000.00
```

**Calculator Logic:**
- ID 1: Basic, 60 days → $10,000 × 0.01 ÷ 12 = $8.33 interest
- ID 2: Student, 100 days → $5,000 × 0.03 ÷ 12 = $12.50 interest  
- ID 3: Premium, 50 days → $20,000 × 0.05 ÷ 12 = $83.33 interest

**After Update:**
```sql
timeDeposits table:
id | planType | days | balance
1  | basic    | 60   | 10008.33  (+ $8.33)
2  | student  | 100  | 5012.50   (+ $12.50)
3  | premium  | 50   | 20083.33  (+ $83.33)
```

### Edge Cases & Validation
| Scenario | Behavior | Response |
|----------|----------|----------|
| **No deposits in database** | Skip calculation, return success | `200 OK` with message |
| **Database connection fails** | Return error | `500 Internal Server Error` |
| **Invalid plan types in DB** | Calculator ignores unknown types | `200 OK` (graceful degradation) |
| **Negative balances** | Calculator processes normally | `200 OK` (business logic handles) |
| **Very large balance numbers** | Use proper decimal precision | `200 OK` with rounded values |

### Output Specification
| Status Code | Response Body | Scenario |
|-------------|---------------|----------|
| **200 OK** | `{"message": "Balances updated successfully", "updatedCount": 5}` | Success |
| **200 OK** | `{"message": "No deposits to update", "updatedCount": 0}` | Empty database |
| **500 Internal Server Error** | `{"error": "Database connection failed"}` | System error |

---

## 📊 Endpoint 2: Get All Time Deposits

### Basic Information
- **URL**: `/deposits` or `/time-deposits`
- **Method**: `GET`
- **Purpose**: Retrieve all time deposits with their complete withdrawal history

### Input Specification
| Input Type | Required | Format | Description |
|------------|----------|---------|-------------|
| **Query Parameters** | ❌ No | N/A | No filtering parameters needed |
| **Request Body** | ❌ No | N/A | GET request - no body |

### Process Flow (Step-by-Step)
```
1. 📊 FETCH DEPOSITS: 
   SELECT id, planType, balance, days FROM timeDeposits ORDER BY id

2. 📝 FETCH WITHDRAWALS:
   SELECT id, timeDepositId, amount, date FROM withdrawals ORDER BY timeDepositId, date

3. 🔗 JOIN DATA: Group withdrawals by timeDepositId and attach to deposits

4. 📋 FORMAT RESPONSE: Create JSON objects with required schema

5. ✅ RETURN: JSON array of deposits with nested withdrawals
```

### Database Queries Involved

#### Query 1: Get All Deposits
```sql
SELECT id, planType, balance, days 
FROM timeDeposits 
ORDER BY id;
```

#### Query 2: Get All Withdrawals  
```sql
SELECT id, timeDepositId, amount, date 
FROM withdrawals 
ORDER BY timeDepositId, date;
```

#### Alternative: Single Join Query
```sql
SELECT 
    td.id as deposit_id,
    td.planType, 
    td.balance, 
    td.days,
    w.id as withdrawal_id,
    w.amount as withdrawal_amount,
    w.date as withdrawal_date
FROM timeDeposits td
LEFT JOIN withdrawals w ON td.id = w.timeDepositId
ORDER BY td.id, w.date;
```

### Required Response Schema
Each deposit object must include:
- `id` (Integer) - from timeDeposits.id
- `planType` (String) - from timeDeposits.planType
- `balance` (Number) - from timeDeposits.balance  
- `days` (Integer) - from timeDeposits.days
- `withdrawals` (Array) - collection of withdrawal objects

### Withdrawal Object Schema
Each withdrawal must include:
- `id` (Integer) - from withdrawals.id
- `amount` (Number) - from withdrawals.amount
- `date` (String) - from withdrawals.date (formatted)

### Sample Database State
```sql
-- timeDeposits table
id | planType | balance   | days
1  | basic    | 10008.33  | 60
2  | student  | 5012.50   | 100  
3  | premium  | 20083.33  | 50

-- withdrawals table  
id | timeDepositId | amount  | date
1  | 1            | 500.00  | 2024-03-15
2  | 1            | 200.00  | 2024-04-01
3  | 2            | 100.00  | 2024-03-20
```

### Edge Cases & Validation
| Scenario | Behavior | Response |
|----------|----------|----------|
| **No deposits in database** | Return empty array | `200 OK` with `[]` |
| **Deposit has no withdrawals** | Include empty withdrawals array | `200 OK` with `"withdrawals": []` |
| **Database connection fails** | Return error | `500 Internal Server Error` |
| **Orphaned withdrawals** | Include only valid deposit-withdrawal relationships | `200 OK` (filtered data) |
| **Invalid date formats in DB** | Convert to ISO string or handle gracefully | `200 OK` with formatted dates |
| **NULL/missing values** | Use defaults or exclude field | `200 OK` with clean data |

### Output Specification

#### Success Response (200 OK)
```json
[
  {
    "id": 1,
    "planType": "basic",
    "balance": 10008.33,
    "days": 60,
    "withdrawals": [
      {
        "id": 1,
        "amount": 500.00,
        "date": "2024-03-15"
      },
      {
        "id": 2,  
        "amount": 200.00,
        "date": "2024-04-01"
      }
    ]
  },
  {
    "id": 2,
    "planType": "student", 
    "balance": 5012.50,
    "days": 100,
    "withdrawals": [
      {
        "id": 3,
        "amount": 100.00,
        "date": "2024-03-20"
      }
    ]
  },
  {
    "id": 3,
    "planType": "premium",
    "balance": 20083.33,
    "days": 50,
    "withdrawals": []
  }
]
```

#### Empty Database (200 OK)
```json
[]
```

#### Error Response (500 Internal Server Error)
```json
{
  "error": "Database connection failed",
  "message": "Unable to retrieve deposits at this time"
}
```

---

## 🔧 Technical Implementation Notes

### Database Operations Summary

#### For Update Balances Endpoint:
```sql
-- 1. Fetch deposits for calculator
SELECT id, planType, balance, days FROM timeDeposits WHERE id IS NOT NULL;

-- 2. Update balances after calculation (per deposit)
UPDATE timeDeposits SET balance = ? WHERE id = ?;

-- Note: withdrawals table is NEVER touched by this endpoint
```

#### For Get Deposits Endpoint:
```sql
-- Option 1: Two separate queries (recommended for clarity)
SELECT id, planType, balance, days FROM timeDeposits ORDER BY id;
SELECT id, timeDepositId, amount, date FROM withdrawals ORDER BY timeDepositId, date;

-- Option 2: Single LEFT JOIN (if ORM supports grouping)
SELECT 
  td.id, td.planType, td.balance, td.days,
  w.id as withdrawal_id, w.amount, w.date
FROM timeDeposits td
LEFT JOIN withdrawals w ON td.id = w.timeDepositId
ORDER BY td.id, w.date;
```

### Key Implementation Constraints

#### ⚠️ CRITICAL: DO NOT Modify These
- `TimeDeposit` class structure
- `TimeDepositCalculator.update_balance` method signature  
- Existing interest calculation logic

#### ✅ MUST Implement
- Database persistence layer (repositories)
- Object-relational mapping between DB and domain objects
- REST API endpoints with proper HTTP status codes
- Clean architecture separation (domain/application/infrastructure)

#### 📊 Data Integrity Rules
- `timeDeposits.id` must be unique and auto-increment
- `withdrawals.timeDepositId` must reference valid `timeDeposits.id`
- All monetary amounts use DECIMAL(10,2) for precision
- Dates stored in ISO format (YYYY-MM-DD)

### Performance Considerations
- **Update Endpoint**: Processes ALL deposits (could be slow with large datasets)
- **Get Endpoint**: N+1 query problem if using separate withdrawal queries per deposit
- **Indexing**: Create indexes on `withdrawals.timeDepositId` and `timeDeposits.id`
- **Transactions**: Wrap balance updates in database transactions for consistency

### Architecture Requirements
- **Repository Pattern**: Abstract database access behind interfaces
- **Service Layer**: Orchestrate calculator + repository operations
- **Dependency Injection**: Wire up components cleanly
- **Error Handling**: Return appropriate HTTP status codes
- **Extensibility**: Design to accommodate future interest calculation complexities
