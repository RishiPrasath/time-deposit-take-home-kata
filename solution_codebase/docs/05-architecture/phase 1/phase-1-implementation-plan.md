# Phase 1: Infrastructure Layer Implementation Plan
## 🏗️ Foundation First - Database Layer Setup (90 minutes)

### 🎯 **Current State Analysis**

**Your Working Directory:** `C:\Users\prasa\Code\ikigai-take-home-assignment\Python\fastapi\`

**What You Currently Have:**
```
fastapi/
├── run_api.cmd           # Existing script
├── run_api.ps1          # Existing script  
├── src/                 # Existing source code
│   ├── database/        # Some database code
│   ├── domain/          # Some domain code
│   ├── main.py          # FastAPI entry point
│   └── __pycache__/     # Python cache
└── venv/               # Virtual environment
```

**What We Need to Build:**
- Clean architecture structure (separate from existing src/)
- PostgreSQL database setup with Docker
- SQLAlchemy models for exact schema requirements
- Repository pattern for data access
- Comprehensive testing for infrastructure layer

---

## 🛠️ **Phase 1 Detailed Plan**

### **Step 1.1: Project Structure Setup (20 minutes)**

#### **A. Create New Architecture Structure**
We'll create a new `app/` directory alongside your existing `src/` to implement clean architecture:

```
fastapi/
├── src/                    # Keep existing code (unchanged)
├── venv/                   # Keep existing virtual environment
├── app/                    # 🆕 NEW: Clean architecture implementation
│   └── infrastructure/     # 🆕 Infrastructure layer
│       ├── __init__.py
│       ├── database/       # 🆕 Database components
│       │   ├── __init__.py
│       │   ├── connection.py      # Database connection setup
│       │   ├── models.py          # SQLAlchemy models
│       │   └── repositories/      # Data access layer
│       │       ├── __init__.py
│       │       └── time_deposit_repository.py
│       └── config/         # 🆕 Configuration
│           ├── __init__.py
│           └── settings.py        # App settings
├── tests/                  # 🆕 Test suite
│   ├── __init__.py
│   ├── conftest.py        # Test configuration
│   └── infrastructure/    # Infrastructure tests
│       ├── __init__.py
│       └── test_time_deposit_repository.py
├── migrations/             # 🆕 Database migrations
│   ├── 001_init_database.sql
│   └── 002_sample_data.sql
├── docker-compose.yml      # 🆕 PostgreSQL setup
├── requirements.txt        # 🆕 Dependencies
└── .env                   # 🆕 Environment variables
```

#### **B. Install Required Dependencies**
```bash
# Activate virtual environment
venv\Scripts\activate

# Install infrastructure dependencies
pip install sqlalchemy psycopg2-binary python-dotenv pytest pytest-asyncio
pip install alembic  # For database migrations
```

#### **C. Docker Setup for PostgreSQL**
Create `docker-compose.yml` with PostgreSQL container for development.

---

### **Step 1.2: Database Models Implementation (30 minutes)**

#### **A. Database Connection Setup**
Create `app/infrastructure/database/connection.py`:
- PostgreSQL connection string
- SQLAlchemy engine setup
- Session management
- Connection pooling

#### **B. SQLAlchemy Models**
Create `app/infrastructure/database/models.py`:
- **TimeDepositModel** - Exact schema from requirements
- **WithdrawalModel** - With foreign key to TimeDeposits
- **Relationships** - One-to-Many (TimeDeposit → Withdrawals)
- **Constraints** - Data validation, foreign keys

**Exact Schema to Implement:**
```sql
-- timeDeposits table
CREATE TABLE timeDeposits (
    id SERIAL PRIMARY KEY,
    planType VARCHAR(50) NOT NULL CHECK (planType IN ('basic', 'student', 'premium')),
    days INTEGER NOT NULL CHECK (days >= 0),
    balance DECIMAL(15,2) NOT NULL CHECK (balance >= 0)
);

-- withdrawals table  
CREATE TABLE withdrawals (
    id SERIAL PRIMARY KEY,
    timeDepositId INTEGER NOT NULL,
    amount DECIMAL(15,2) NOT NULL CHECK (amount > 0),
    date DATE NOT NULL,
    FOREIGN KEY (timeDepositId) REFERENCES timeDeposits(id) ON DELETE CASCADE
);
```

#### **C. Database Migrations**
Create SQL scripts in `migrations/`:
- `001_init_database.sql` - Table creation
- `002_sample_data.sql` - Test data for 9 deposits + 9 withdrawals

---

### **Step 1.3: Repository Implementation (40 minutes)**

#### **A. Repository Interface Design**
Following clean architecture principles:
```python
# This will come in Phase 2 (Domain layer)
class TimeDepositRepositoryInterface(ABC):
    @abstractmethod
    def get_all(self) -> List[TimeDepositModel]: pass
    
    @abstractmethod
    def get_all_with_withdrawals(self) -> List[TimeDepositModel]: pass
    
    @abstractmethod
    def save_all(self, deposits: List[TimeDepositModel]): pass
```

#### **B. Concrete Repository Implementation**
Create `app/infrastructure/database/repositories/time_deposit_repository.py`:
- **get_all()** - Fetch all time deposits (for balance updates)
- **get_all_with_withdrawals()** - Fetch deposits with JOIN to withdrawals
- **save_all()** - Update multiple deposits in transaction
- **create_sample_data()** - Insert test data (for development)

#### **C. Key Repository Methods:**
```python
class TimeDepositRepository:
    def __init__(self, db_session):
        self.db = db_session
    
    def get_all(self) -> List[TimeDepositModel]:
        """Get all deposits for balance calculations"""
        return self.db.query(TimeDepositModel).all()
    
    def get_all_with_withdrawals(self) -> List[TimeDepositModel]:
        """Get all deposits with their withdrawals (using JOIN)"""
        return self.db.query(TimeDepositModel).options(
            joinedload(TimeDepositModel.withdrawals)
        ).all()
    
    def save_all(self, deposits: List[TimeDepositModel]):
        """Update multiple deposits in a transaction"""
        for deposit in deposits:
            self.db.merge(deposit)
        self.db.commit()
```

---

### **Step 1.4: Testing Strategy (Phase 1 Focus)**

#### **A. Test Database Setup**
Create `tests/conftest.py`:
- SQLite in-memory database for tests
- Test session fixtures
- Sample data fixtures

#### **B. Repository Tests**
Create `tests/infrastructure/test_time_deposit_repository.py`:
```python
def test_create_time_deposit():
    """Test basic deposit creation"""
    
def test_get_all_deposits():
    """Test fetching all deposits"""
    
def test_get_with_withdrawals():
    """Test JOIN query for deposits + withdrawals"""
    
def test_update_balances():
    """Test batch updates"""
    
def test_foreign_key_constraints():
    """Test database constraints work"""
```

#### **C. Database Integration Tests**
- Test actual PostgreSQL connection
- Test migration scripts
- Test sample data insertion

---

## 🧪 **Phase 1 Validation Criteria**

After completing Phase 1, you should be able to run these commands successfully:

### **Infrastructure Tests:**
```bash
# Test database operations
python -m pytest tests/infrastructure/ -v

# Expected Results:
# ✅ Database connection established
# ✅ Models create tables correctly  
# ✅ Repository operations work
# ✅ Sample data inserted/retrieved
# ✅ Foreign key relationships function
```

### **Database Validation:**
```bash
# Start PostgreSQL container
docker-compose up postgres -d

# Connect to database and verify
psql -h localhost -U postgres -d timedeposit_db -c "\dt"

# Should show:
# timeDeposits table
# withdrawals table
```

### **Sample Data Validation:**
```bash
# Run sample data script
python scripts/create_sample_data.py

# Query sample data
psql -h localhost -U postgres -d timedeposit_db -c "SELECT * FROM timeDeposits LIMIT 5;"
```

---

## 🎯 **Phase 1 Success Checklist**

- [ ] **Project Structure Created** - Clean architecture folders
- [ ] **Dependencies Installed** - SQLAlchemy, PostgreSQL driver, testing
- [ ] **Docker Setup** - PostgreSQL container running
- [ ] **Database Models** - Exact schema implemented in SQLAlchemy
- [ ] **Repository Layer** - CRUD operations working
- [ ] **Migration Scripts** - Database creation and sample data
- [ ] **Test Suite** - Infrastructure tests passing
- [ ] **Database Connection** - Can connect and query PostgreSQL
- [ ] **Sample Data** - 9 deposits + 9 withdrawals inserted
- [ ] **Validation Complete** - All Phase 1 criteria met

---

## ⚡ **What Happens After Phase 1**

Once Phase 1 is complete, you'll have:
- **Solid database foundation** with PostgreSQL
- **Working repository layer** for data access  
- **Comprehensive test suite** for infrastructure
- **Sample data** for testing business logic

**Then we move to Phase 2**: Copy your existing domain classes (TimeDeposit, TimeDepositCalculator) without any modifications, ensuring no breaking changes.

---

## 🚨 **Key Principles for Phase 1**

1. **Database First** - Everything else depends on data storage working
2. **Test Everything** - Each component tested before moving on
3. **Exact Schema** - Must match requirements precisely
4. **No Business Logic** - Pure data access and infrastructure
5. **Sample Data** - Realistic test data covering all scenarios

---

## 🤔 **Questions to Consider Before Starting**

1. **Do you want to use PostgreSQL** (production) or **start with SQLite** (simpler)?
2. **Do you have Docker installed** for PostgreSQL container?
3. **Should we keep your existing src/ code** or work alongside it?
4. **Any specific database preferences** or constraints?

---

**Ready to begin Phase 1? Let me know which approach you'd prefer and I'll guide you through each step!** 🚀
