# Time Deposit Management System - Phase 1 Infrastructure

This project implements a FastAPI-based time deposit management system using clean architecture principles.

## Phase 1: Infrastructure Layer ✅

The infrastructure layer provides the foundational database and data access components.

### 🏗️ Architecture Overview

```
app/
├── infrastructure/          # Infrastructure Layer
│   ├── database/           # Database components
│   │   ├── connection.py   # Database connection setup
│   │   ├── models.py       # SQLAlchemy models
│   │   └── repositories/   # Data access layer
│   │       └── time_deposit_repository.py
│   └── config/            # Configuration
│       └── settings.py    # Application settings
```

### 🗄️ Database Schema

#### Time Deposits Table
```sql
CREATE TABLE "timeDeposits" (
    id SERIAL PRIMARY KEY,
    "planType" VARCHAR(50) NOT NULL CHECK ("planType" IN ('basic', 'student', 'premium')),
    days INTEGER NOT NULL CHECK (days >= 0),
    balance DECIMAL(15,2) NOT NULL CHECK (balance >= 0)
);
```

#### Withdrawals Table
```sql
CREATE TABLE withdrawals (
    id SERIAL PRIMARY KEY,
    "timeDepositId" INTEGER NOT NULL REFERENCES "timeDeposits"(id) ON DELETE CASCADE,
    amount DECIMAL(15,2) NOT NULL CHECK (amount > 0),
    date DATE NOT NULL
);
```

### 🚀 Quick Start

#### 1. Install Dependencies
```bash
# Activate virtual environment
.\venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

#### 2. Start PostgreSQL (with Docker)
```bash
# Start PostgreSQL container
docker-compose up postgres -d

# Check container status
docker ps
```

#### 3. Initialize Database
```bash
# Run initialization script
python scripts/init_database.py

# Or manually run migrations
psql -h localhost -U postgres -d timedeposit_db -f migrations/001_init_database.sql
psql -h localhost -U postgres -d timedeposit_db -f migrations/002_sample_data.sql
```

#### 4. Run Tests
```bash
# Run infrastructure tests
python -m pytest tests/infrastructure/ -v

# Run all tests with coverage
python -m pytest tests/ -v --cov=app
```

#### 5. Validate Implementation
```bash
# Run Phase 1 validation
python scripts/validate_phase1.py
```

### 🧪 Testing

The infrastructure layer includes comprehensive tests:
- Database connection tests
- Model relationship tests
- Repository CRUD operation tests
- Constraint validation tests

### 📊 Sample Data

The system includes 9 sample time deposits and 9 withdrawals for testing:
- 3 basic plan deposits
- 3 student plan deposits
- 3 premium plan deposits

### 🐳 Docker Support

#### PostgreSQL Only
```bash
docker-compose up postgres -d
```

#### Full Application (when complete)
```bash
docker-compose up
```

### 🔧 Configuration

Environment variables in `.env`:
- `DATABASE_URL`: PostgreSQL connection string
- `DATABASE_URL_TEST`: Test database connection
- `POSTGRES_*`: PostgreSQL configuration
- `APP_*`: Application settings

### 📝 Next Steps: Phase 2

With Phase 1 complete, you can now proceed to Phase 2 (Domain Layer):
1. Copy existing TimeDeposit and TimeDepositCalculator classes
2. Create domain interfaces
3. Implement business logic tests

### 🔍 Validation Checklist

- [x] Project structure created
- [x] PostgreSQL setup with Docker
- [x] SQLAlchemy models implemented
- [x] Repository pattern implemented
- [x] Database migration scripts
- [x] Comprehensive test suite
- [x] Configuration management
- [x] Sample data creation
- [x] Documentation

### 🛠️ Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Start database
docker-compose up postgres -d

# Initialize database
python scripts/init_database.py

# Run tests
python -m pytest tests/infrastructure/ -v

# Validate implementation
python scripts/validate_phase1.py

# Format code
black app/ tests/

# Type checking
mypy app/
```

## Business Requirements

### Interest Calculation Rules
- **Basic Plan**: 1% monthly interest after 30 days
- **Student Plan**: 3% monthly interest after 30 days, stops after 1 year
- **Premium Plan**: 5% monthly interest after 45 days

### API Requirements (Future Phases)
- `PUT /time-deposits/balances` - Update all deposit balances
- `GET /time-deposits` - Get all deposits with withdrawals