# Makefile for Time Deposit API - Docker Operations

.PHONY: help build up down restart logs test migrate seed shell db-shell clean status prod-up prod-down

# Default target
help:
	@echo "Time Deposit API - Docker Management"
	@echo ""
	@echo "Development Commands:"
	@echo "  make build      - Build Docker images"
	@echo "  make up         - Start development services"
	@echo "  make down       - Stop services"
	@echo "  make restart    - Restart services"
	@echo "  make logs       - Show logs"
	@echo "  make test       - Run tests in container"
	@echo "  make migrate    - Run database migrations"
	@echo "  make seed       - Seed database with sample data"
	@echo "  make shell      - Open bash shell in web container"
	@echo "  make db-shell   - Open PostgreSQL shell"
	@echo "  make clean      - Remove all containers and volumes"
	@echo "  make status     - Show service status"
	@echo ""
	@echo "Production Commands:"
	@echo "  make prod-up    - Start production services"
	@echo "  make prod-down  - Stop production services"

# Development commands
build:
	docker-compose build

up:
	docker-compose up -d
	@echo "✅ Services started!"
	@echo "📚 API Documentation: http://localhost:8000/docs"
	@echo "🔍 Health Check: http://localhost:8000/health"

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

test:
	docker-compose exec web pytest tests/ -v --cov=src --cov-report=term-missing

migrate:
	docker-compose exec web python -c "from src.infrastructure.database import engine; from src.domain.models import Base; Base.metadata.create_all(bind=engine); print('✅ Migrations completed!')"

seed:
	docker-compose exec postgres psql -U postgres -d timedeposit_db -f /docker-entrypoint-initdb.d/02-seed.sql

shell:
	docker-compose exec web /bin/bash

db-shell:
	docker-compose exec postgres psql -U postgres -d timedeposit_db

clean:
	docker-compose down -v
	@echo "🧹 Cleaned up all containers and volumes"

status:
	docker-compose ps

# Production commands
prod-up:
	docker-compose -f docker-compose.prod.yml up -d
	@echo "✅ Production services started!"

prod-down:
	docker-compose -f docker-compose.prod.yml down

# Quick development setup
dev-setup: build up migrate seed
	@echo "✅ Development environment ready!"
	@echo "📚 Visit http://localhost:8000/docs"

# Run all tests with coverage report
test-all:
	docker-compose exec web pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing
	@echo "📊 Coverage report generated in htmlcov/"
