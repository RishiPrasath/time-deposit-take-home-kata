#!/bin/bash
# Docker development helper script

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Commands
case "$1" in
    build)
        print_status "Building Docker images..."
        docker-compose build
        ;;
    
    up)
        print_status "Starting services..."
        docker-compose up -d
        print_status "Services started. API available at http://localhost:8000"
        print_status "API Documentation at http://localhost:8000/docs"
        ;;
    
    down)
        print_status "Stopping services..."
        docker-compose down
        ;;
    
    restart)
        print_status "Restarting services..."
        docker-compose restart
        ;;
    
    logs)
        docker-compose logs -f ${2:-}
        ;;
    
    test)
        print_status "Running tests in container..."
        docker-compose exec web pytest tests/ -v
        ;;
    
    migrate)
        print_status "Running database migrations..."
        docker-compose exec web python -c "
from src.infrastructure.database import engine
from src.domain.models import Base
Base.metadata.create_all(bind=engine)
print('Migrations completed!')
"
        ;;
    
    seed)
        print_status "Seeding database..."
        docker-compose exec postgres psql -U postgres -d timedeposit_db -f /docker-entrypoint-initdb.d/02-seed.sql
        ;;
    
    shell)
        print_status "Opening shell in web container..."
        docker-compose exec web /bin/bash
        ;;
    
    db-shell)
        print_status "Opening PostgreSQL shell..."
        docker-compose exec postgres psql -U postgres -d timedeposit_db
        ;;
    
    clean)
        print_warning "This will remove all containers and volumes!"
        read -p "Are you sure? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]
        then
            docker-compose down -v
            print_status "Cleaned up all containers and volumes"
        fi
        ;;
    
    status)
        print_status "Service status:"
        docker-compose ps
        ;;
    
    *)
        echo "Usage: $0 {build|up|down|restart|logs|test|migrate|seed|shell|db-shell|clean|status}"
        echo ""
        echo "Commands:"
        echo "  build    - Build Docker images"
        echo "  up       - Start all services"
        echo "  down     - Stop all services"
        echo "  restart  - Restart all services"
        echo "  logs     - Show logs (optionally specify service)"
        echo "  test     - Run tests in container"
        echo "  migrate  - Run database migrations"
        echo "  seed     - Seed database with sample data"
        echo "  shell    - Open bash shell in web container"
        echo "  db-shell - Open PostgreSQL shell"
        echo "  clean    - Remove all containers and volumes"
        echo "  status   - Show service status"
        exit 1
        ;;
esac
