# Ikigai Time Deposit Challenge - Problem Breakdown

## 📊 Current State Analysis

### What's Already Implemented
The junior developer has provided a **basic domain logic** with these components:

#### 1. **TimeDeposit Class** (Core Domain Model)
```typescript
class TimeDeposit {
  id: number
  planType: string    // 'basic', 'student', 'premium'
  balance: number     // Current balance
  days: number        // Days since deposit
}
```

#### 2. **TimeDepositCalculator Class** (Business Logic)
```typescript
updateBalance(deposits: TimeDeposit[]) {
  // ✅ Already implements monthly interest calculation
  // ✅ Handles all 3 plan types (basic, student, premium)
  // ✅ Applies correct business rules:
  //     - No interest for first 30 days
  //     - Basic: 1% annual (0.01/12 monthly)
  //     - Student: 3% annual, stops after 1 year
  //     - Premium: 5% annual, starts after 45 days
}
```

## 🎯 What You Need to Build

### Missing Components

#### 1. **REST API Layer** 🚨
- **Endpoint 1**: `PUT/POST /deposits/update-balances` 
  - Updates balances for ALL deposits using existing calculator
- **Endpoint 2**: `GET /deposits`
  - Returns all deposits with withdrawal history

#### 2. **Database Layer** 🚨
- **timeDeposits table**:
  ```sql
  CREATE TABLE timeDeposits (
    id INTEGER PRIMARY KEY,
    planType VARCHAR(50) NOT NULL,
    days INTEGER NOT NULL,
    balance DECIMAL(10,2) NOT NULL
  );
  ```
- **withdrawals table**:
  ```sql
  CREATE TABLE withdrawals (
    id INTEGER PRIMARY KEY,
    timeDepositId INTEGER NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    date DATE NOT NULL,
    FOREIGN KEY (timeDepositId) REFERENCES timeDeposits(id)
  );
  ```

#### 3. **Repository/Data Access Layer** 🚨
- Methods to CRUD time deposits
- Methods to CRUD withdrawals
- Method to fetch deposits with their withdrawals

#### 4. **Service Layer** 🚨
- Orchestrate calculator + repository operations
- Handle business workflows

## 🏗️ Architecture Requirements

### Must Follow
- **Clean/Hexagonal Architecture**
- **SOLID Principles**
- **No breaking changes** to existing classes

### Recommended Structure
```
src/
├── domain/
│   ├── TimeDeposit.ts              # ✅ Already exists
│   └── TimeDepositCalculator.ts    # ✅ Already exists
├── application/
│   └── TimeDepositService.ts       # 🚨 Build this
├── infrastructure/
│   ├── database/
│   │   ├── TimeDepositRepository.ts # 🚨 Build this
│   │   └── WithdrawalRepository.ts  # 🚨 Build this
│   └── web/
│       └── TimeDepositController.ts # 🚨 Build this
└── main.ts                         # 🚨 Build this
```

## 🎯 Key Challenges & Constraints

### ⚠️ Critical Constraints
1. **DO NOT modify** `TimeDeposit` class
2. **DO NOT change** `updateBalance` method signature
3. **DO NOT break** existing calculator behavior
4. **Build EXACTLY 2 endpoints** (no more, no less)

### 🧩 Design Challenges
1. **Extensibility**: Design must support future interest calculation complexities
2. **Database Integration**: Need to persist/retrieve data while using existing calculator
3. **API Response Format**: Must include withdrawal history in GET response
4. **Architecture**: Must follow clean architecture patterns

## 📋 Implementation Checklist

### Phase 1: Foundation
- [ ] Choose database (SQLite for simplicity?)
- [ ] Set up database schema and connections
- [ ] Create repository interfaces and implementations

### Phase 2: Service Layer
- [ ] Build TimeDepositService that uses existing calculator
- [ ] Implement withdrawal tracking
- [ ] Handle deposit retrieval with withdrawal history

### Phase 3: API Layer
- [ ] Choose web framework (Express.js for TypeScript?)
- [ ] Build update-balances endpoint
- [ ] Build get-all-deposits endpoint with required schema

### Phase 4: Integration
- [ ] Wire up dependency injection
- [ ] Add proper error handling
- [ ] Write integration tests
- [ ] Document how to run the application

## 📊 Expected API Responses

### GET /deposits Response Schema
```json
[
  {
    "id": 1,
    "planType": "basic",
    "balance": 1234.56,
    "days": 45,
    "withdrawals": [
      {
        "id": 1,
        "amount": 100.00,
        "date": "2024-09-20"
      }
    ]
  }
]
```

### PUT/POST /deposits/update-balances
- Updates all deposits using `TimeDepositCalculator.updateBalance()`
- Returns success status

## 🚀 Success Criteria

1. ✅ Two working REST endpoints
2. ✅ Database persistence working
3. ✅ Existing calculator logic unchanged and functional
4. ✅ Clean architecture with proper separation of concerns
5. ✅ Application runs with clear instructions
6. ✅ No breaking changes to existing classes

## 💡 Technology Recommendations

- **TypeScript** (since you have the files there)
- **Express.js** for web API
- **SQLite** for database (simple, no setup)
- **TypeORM** or **Prisma** for database access
- **Jest** for testing

This challenge tests your ability to **refactor and extend existing code** while building a complete application architecture around it.
