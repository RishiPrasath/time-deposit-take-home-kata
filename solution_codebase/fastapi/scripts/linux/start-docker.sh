#!/bin/bash

# ============================================
# Time Deposit API - Docker Startup Script
# ============================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Navigate to project root (two levels up from scripts/linux)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR/../.."

echo ""
echo "====================================="
echo "  TIME DEPOSIT API - DOCKER STARTUP"
echo "====================================="
echo ""

# Step 1: Build Docker Images
echo -e "${BLUE}[STEP 1/5]${NC} Building Docker images..."
echo "-----------------------------------------"
docker-compose build
if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR]${NC} Failed to build Docker images"
    exit 1
fi

# Step 2: Start Services
echo ""
echo -e "${BLUE}[STEP 2/5]${NC} Starting Docker services..."
echo "-----------------------------------------"
docker-compose up -d
if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR]${NC} Failed to start Docker services"
    exit 1
fi

# Step 3: Wait for Services
echo ""
echo -e "${BLUE}[STEP 3/5]${NC} Waiting for services to initialize..."
echo "-----------------------------------------"
echo "Please wait 10 seconds..."
sleep 10

# Step 4: Health Check
echo ""
echo -e "${BLUE}[STEP 4/5]${NC} Performing health check..."
echo "-----------------------------------------"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}[OK]${NC} Health check passed"
else
    echo -e "${YELLOW}[WARNING]${NC} Health check failed. Services may still be starting..."
fi

# Step 5: Test Endpoints
echo ""
echo -e "${BLUE}[STEP 5/5]${NC} Testing API endpoints..."
echo "-----------------------------------------"
echo ""
echo "Testing Health Endpoint:"
curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8000/health
echo ""
echo ""
echo "Testing GET /time-deposits:"
curl -s http://localhost:8000/time-deposits | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8000/time-deposits
echo ""
echo ""
echo "Testing PUT /time-deposits/updateBalances:"
curl -s -X PUT http://localhost:8000/time-deposits/updateBalances | python3 -m json.tool 2>/dev/null || curl -s -X PUT http://localhost:8000/time-deposits/updateBalances
echo ""
echo ""

# Success Message
echo -e "${GREEN}====================================="
echo "  STARTUP COMPLETE - API IS READY!"
echo "=====================================${NC}"
echo ""
echo "Service URLs:"
echo "  - API:     http://localhost:8000"
echo "  - Swagger: http://localhost:8000/docs"
echo "  - ReDoc:   http://localhost:8000/redoc"
echo "  - Health:  http://localhost:8000/health"
echo ""
echo "Database:"
echo "  - Host: localhost"
echo "  - Port: 5432"
echo "  - Name: timedeposit_db"
echo ""
echo "To stop services, run: ./stop-docker.sh"
echo "====================================="
echo ""
