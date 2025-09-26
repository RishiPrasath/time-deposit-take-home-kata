# Docker development helper script for Windows PowerShell

# Colors for output
function Write-Status {
    param($Message)
    Write-Host "[INFO] " -ForegroundColor Green -NoNewline
    Write-Host $Message
}

function Write-Error-Message {
    param($Message)
    Write-Host "[ERROR] " -ForegroundColor Red -NoNewline
    Write-Host $Message
}

function Write-Warning-Message {
    param($Message)
    Write-Host "[WARNING] " -ForegroundColor Yellow -NoNewline
    Write-Host $Message
}

# Main command switch
$Command = $args[0]
$ServiceName = $args[1]

switch ($Command) {
    "build" {
        Write-Status "Building Docker images..."
        docker-compose build
    }
    
    "up" {
        Write-Status "Starting services..."
        docker-compose up -d
        Write-Status "Services started. API available at http://localhost:8000"
        Write-Status "API Documentation at http://localhost:8000/docs"
    }
    
    "down" {
        Write-Status "Stopping services..."
        docker-compose down
    }
    
    "restart" {
        Write-Status "Restarting services..."
        docker-compose restart
    }
    
    "logs" {
        if ($ServiceName) {
            docker-compose logs -f $ServiceName
        } else {
            docker-compose logs -f
        }
    }
    
    "test" {
        Write-Status "Running tests in container..."
        docker-compose exec web pytest tests/ -v
    }
    
    "migrate" {
        Write-Status "Running database migrations..."
        $migrationScript = @"
from src.infrastructure.database import engine
from src.domain.models import Base
Base.metadata.create_all(bind=engine)
print('Migrations completed!')
"@
        docker-compose exec web python -c $migrationScript
    }
    
    "seed" {
        Write-Status "Seeding database..."
        docker-compose exec postgres psql -U postgres -d timedeposit_db -f /docker-entrypoint-initdb.d/02-seed.sql
    }
    
    "shell" {
        Write-Status "Opening shell in web container..."
        docker-compose exec web /bin/bash
    }
    
    "db-shell" {
        Write-Status "Opening PostgreSQL shell..."
        docker-compose exec postgres psql -U postgres -d timedeposit_db
    }
    
    "clean" {
        Write-Warning-Message "This will remove all containers and volumes!"
        $confirmation = Read-Host "Are you sure? (y/N)"
        if ($confirmation -eq 'y' -or $confirmation -eq 'Y') {
            docker-compose down -v
            Write-Status "Cleaned up all containers and volumes"
        }
    }
    
    "status" {
        Write-Status "Service status:"
        docker-compose ps
    }
    
    "prod-up" {
        Write-Status "Starting production services..."
        docker-compose -f docker-compose.prod.yml up -d
        Write-Status "Production services started"
    }
    
    "prod-down" {
        Write-Status "Stopping production services..."
        docker-compose -f docker-compose.prod.yml down
    }
    
    default {
        Write-Host "Usage: .\docker-dev.ps1 {build|up|down|restart|logs|test|migrate|seed|shell|db-shell|clean|status|prod-up|prod-down}"
        Write-Host ""
        Write-Host "Commands:"
        Write-Host "  build     - Build Docker images"
        Write-Host "  up        - Start all services (development)"
        Write-Host "  down      - Stop all services"
        Write-Host "  restart   - Restart all services"
        Write-Host "  logs      - Show logs (optionally specify service)"
        Write-Host "  test      - Run tests in container"
        Write-Host "  migrate   - Run database migrations"
        Write-Host "  seed      - Seed database with sample data"
        Write-Host "  shell     - Open bash shell in web container"
        Write-Host "  db-shell  - Open PostgreSQL shell"
        Write-Host "  clean     - Remove all containers and volumes"
        Write-Host "  status    - Show service status"
        Write-Host "  prod-up   - Start production services"
        Write-Host "  prod-down - Stop production services"
    }
}
