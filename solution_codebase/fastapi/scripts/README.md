# 📁 Scripts Directory

This directory contains helper scripts for managing the Time Deposit API Docker environment.

## 🗂️ Directory Structure

```
scripts/
├── windows/           # Windows batch scripts
│   ├── start-docker.cmd
│   └── stop-docker.cmd
├── linux/            # Linux/Mac bash scripts
│   ├── start-docker.sh
│   └── stop-docker.sh
├── init_database.py  # Database initialization (Python)
├── seed_data.sql     # Sample data for PostgreSQL
└── validate_phase1.py # Validation script
```

## 🚀 Quick Start Scripts

### Windows Users

Navigate to `scripts/windows/` and run:

```cmd
# Start all services and test endpoints
start-docker.cmd

# Stop all services
stop-docker.cmd
```

### Linux/Mac Users

Navigate to `scripts/linux/` and run:

```bash
# Make scripts executable (first time only)
chmod +x *.sh

# Start all services and test endpoints
./start-docker.sh

# Stop all services
./stop-docker.sh
```

## 📝 Script Features

### start-docker (.cmd/.sh)
- Builds Docker images
- Starts PostgreSQL and FastAPI services
- Waits for services to be ready
- Performs health checks
- Tests all API endpoints
- Displays service URLs

### stop-docker (.cmd/.sh)
- Confirms shutdown action
- Stops all running containers
- Removes containers (preserves volumes)
- Shows cleanup status

## 🔧 Database Scripts

### init_database.py
- Python script for database initialization
- Creates tables and relationships
- Can be run standalone or via Docker

### seed_data.sql
- SQL script with sample data
- Automatically loaded by Docker on startup
- Contains sample time deposits and withdrawals

### validate_phase1.py
- Validation script for Phase 1 requirements
- Checks database schema and API endpoints

## 💡 Usage Tips

1. **First Time Setup**: Always run the start script first to build images
2. **Check Logs**: If services fail, check `docker-compose logs`
3. **Port Conflicts**: Ensure ports 8000 and 5432 are free
4. **Clean Restart**: Use `docker-compose down -v` to remove all data

## 🛠️ Troubleshooting

If scripts fail to run:

### Windows
- Ensure Docker Desktop is running
- Run Command Prompt as Administrator if needed
- Check that curl is installed

### Linux/Mac
- Ensure Docker is running: `docker info`
- Make scripts executable: `chmod +x *.sh`
- Check Docker permissions: `sudo usermod -aG docker $USER`

## 📚 Related Documentation

- Main README: `../../README.md`
- Docker Guide: `../../DOCKER_README.md`
- API Documentation: http://localhost:8000/docs (when running)
