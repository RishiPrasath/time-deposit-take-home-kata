# 🐳 Docker Setup Guide - Time Deposit API

## Quick Start (Development)

### Windows (PowerShell)
```powershell
# Build and start all services
.\docker-dev.ps1 build
.\docker-dev.ps1 up

# Or using docker-compose directly
docker-compose up -d
```

### Linux/Mac (Bash)
```bash
# Make script executable
chmod +x docker-dev.sh

# Build and start all services
./docker-dev.sh build
./docker-dev.sh up

# Or using Make
make dev-setup
```

## Available Commands

### PowerShell Script (Windows)
```powershell
.\docker-dev.ps1 build      # Build Docker images
.\docker-dev.ps1 up         # Start services
.\docker-dev.ps1 down       # Stop services
.\docker-dev.ps1 logs       # View logs
.\docker-dev.ps1 test       # Run tests
.\docker-dev.ps1 migrate    # Run migrations
.\docker-dev.ps1 seed       # Seed database
.\docker-dev.ps1 shell      # Open container shell
.\docker-dev.ps1 db-shell   # Open PostgreSQL shell
.\docker-dev.ps1 clean      # Remove all containers/volumes
.\docker-dev.ps1 status     # Check service status
```

### Make Commands (Linux/Mac/Windows with Make)
```bash
make build       # Build Docker images
make up          # Start services
make down        # Stop services
make logs        # View logs
make test        # Run tests
make migrate     # Run migrations
make seed        # Seed database
make shell       # Open container shell
make db-shell    # Open PostgreSQL shell
make clean       # Remove all containers/volumes
make status      # Check service status
make dev-setup   # Complete dev setup (build, up, migrate, seed)
```

## Service URLs

- **API**: http://localhost:8000
- **API Documentation (Swagger)**: http://localhost:8000/docs
- **API Documentation (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **PostgreSQL**: localhost:5432 (5433 in dev override)

## Environment Files

### Development (.env.development)
```env
DB_NAME=timedeposit_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_PORT=5432
API_PORT=8000
ENV=development
```

### Production (.env.production)
```env
DB_NAME=timedeposit_prod_db
DB_USER=timedeposit_user
DB_PASSWORD=<SECURE_PASSWORD>
DB_PORT=5432
API_PORT=8000
ENV=production
SECRET_KEY=<SECURE_SECRET_KEY>
```

## Docker Architecture

### Services
1. **postgres**: PostgreSQL 14 database
   - Health checks enabled
   - Auto-initialization with schema
   - Sample data seeding

2. **web**: FastAPI application
   - Hot-reload in development
   - Multi-stage build for optimization
   - Health check endpoint
   - Non-root user in production

3. **nginx** (Production only): Reverse proxy
   - Load balancing
   - SSL termination
   - Static file serving

## Production Deployment

### Using docker-compose.prod.yml
```bash
# Copy and configure production environment
cp .env.production .env
# Edit .env with production values

# Start production services
docker-compose -f docker-compose.prod.yml up -d

# Or using helper script
.\docker-dev.ps1 prod-up  # Windows
make prod-up              # Linux/Mac
```

### Production Considerations
- Change all default passwords in .env.production
- Configure SSL certificates in nginx/ssl/
- Set up proper logging and monitoring
- Configure backup strategy for PostgreSQL
- Use Docker Swarm or Kubernetes for orchestration

## Testing in Docker

### Run All Tests
```bash
# Using docker-compose
docker-compose exec web pytest tests/ -v

# Using helper scripts
.\docker-dev.ps1 test  # Windows
make test              # Linux/Mac
```

### Run with Coverage
```bash
docker-compose exec web pytest tests/ -v --cov=src --cov-report=html
```

## Database Management

### Access PostgreSQL Shell
```bash
docker-compose exec postgres psql -U postgres -d timedeposit_db
```

### Common Database Commands
```sql
-- List all time deposits
SELECT * FROM "timeDeposits";

-- List all withdrawals
SELECT * FROM withdrawals;

-- Check foreign key relationships
SELECT 
    td.id, 
    td."planType", 
    td.balance, 
    COUNT(w.id) as withdrawal_count
FROM "timeDeposits" td
LEFT JOIN withdrawals w ON td.id = w."timeDepositId"
GROUP BY td.id, td."planType", td.balance;
```

## Troubleshooting

### Port Conflicts
If you get port conflict errors:
1. Check if PostgreSQL is running locally: `netstat -an | findstr 5432`
2. Stop local PostgreSQL or change port in docker-compose.override.yml
3. For API port conflicts, change API_PORT in .env

### Database Connection Issues
```bash
# Check if database is ready
docker-compose exec postgres pg_isready

# View database logs
docker-compose logs postgres

# Rebuild database
docker-compose down -v
docker-compose up -d
```

### Container Won't Start
```bash
# Check logs for specific service
docker-compose logs web
docker-compose logs postgres

# Rebuild images
docker-compose build --no-cache

# Remove everything and start fresh
docker-compose down -v
docker system prune -a
docker-compose up --build
```

## Development Workflow

### 1. Initial Setup
```bash
# Clone repository
git clone <repository-url>
cd time-deposit-take-home-kata/solution_codebase/fastapi

# Start services
docker-compose up -d

# Verify health
curl http://localhost:8000/health
```

### 2. Making Changes
- Code changes in `src/` are auto-reloaded (development mode)
- Database schema changes require migration:
  ```bash
  docker-compose exec web python -c "..."
  ```

### 3. Testing Changes
```bash
# Run specific test file
docker-compose exec web pytest tests/test_api.py -v

# Run with debugging
docker-compose exec web pytest tests/ -v -s
```

### 4. Viewing Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f postgres
```

## Security Best Practices

1. **Never commit .env files with production credentials**
2. **Use Docker secrets for sensitive data in production**
3. **Run containers as non-root user (already configured)**
4. **Keep base images updated**
5. **Implement rate limiting and authentication in production**
6. **Use HTTPS with proper SSL certificates**
7. **Regular security scanning of images**

## Performance Optimization

### Docker Build Optimization
- Multi-stage builds implemented
- Layer caching optimized
- Minimal base images (slim/alpine)

### Runtime Optimization
- Connection pooling configured
- Database indexes created
- Resource limits set in production

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review logs: `docker-compose logs`
3. Verify environment variables in .env
4. Ensure Docker and Docker Compose are up to date
