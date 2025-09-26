# Time Deposit API - Refactoring Kata Solution

A RESTful API for managing time deposits with automated interest calculations, built using Clean Architecture principles.

## 🛠️ Tech Stack

- **FastAPI** - Python web framework for building APIs
- **PostgreSQL** - Relational database
- **Docker & Docker Compose** - Containerization and orchestration
- **SQLAlchemy** - ORM for database operations

## 📋 Features

### API Endpoints

1. **GET /time-deposits**
   - Returns all time deposits with their associated withdrawals
   - Response includes: id, planType, balance, days, and withdrawals array

2. **PUT /time-deposits/updateBalances**
   - Updates balances for all time deposits based on interest calculations
   - Interest rates:
     - Basic Plan: 1% monthly
     - Student Plan: 3% monthly (stops after 1 year)
     - Premium Plan: 5% monthly (starts after 45 days)
   - No interest for first 30 days on all plans

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/RishiPrasath/time-deposit-take-home-kata.git
cd time-deposit-take-home-kata/solution_codebase/fastapi

# Start the application
docker-compose up -d

# The API is now running at http://localhost:8000
# API Documentation available at http://localhost:8000/docs
```

### Using Helper Scripts

**Windows:**
```cmd
cd solution_codebase\fastapi
scripts\windows\start-docker.cmd
```

**Linux/Mac:**
```bash
cd solution_codebase/fastapi
chmod +x scripts/linux/*.sh
./scripts/linux/start-docker.sh
```

## 📝 API Documentation

Once running, access the interactive API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🧪 Testing

```bash
# Run tests in Docker
docker-compose exec web pytest tests/ -v

# Stop the application
docker-compose down
```

## 📁 Project Structure

```
solution_codebase/fastapi/
├── src/                # Application source code
├── tests/              # Test suite
├── scripts/            # Helper scripts for Windows/Linux
├── docker-compose.yml  # Docker orchestration
└── requirements.txt    # Python dependencies
```

## 📄 Requirements Met

- ✅ Two RESTful API endpoints implemented
- ✅ PostgreSQL database with required schema
- ✅ Interest calculation logic per plan type
- ✅ No breaking changes to existing code
- ✅ Clean Architecture implementation
- ✅ Fully containerized with Docker

## Author

**Rishi Prasath** - [GitHub](https://github.com/RishiPrasath)
