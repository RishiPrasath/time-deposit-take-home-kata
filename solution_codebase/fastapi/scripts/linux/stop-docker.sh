#!/bin/bash

# ============================================
# Time Deposit API - Docker Shutdown Script
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
echo "  TIME DEPOSIT API - DOCKER SHUTDOWN"
echo "====================================="
echo ""

# Confirm shutdown
read -p "Are you sure you want to stop all services? (Y/N): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Shutdown cancelled."
    exit 0
fi

echo ""
echo -e "${BLUE}[STEP 1/3]${NC} Stopping Docker containers..."
echo "-----------------------------------------"
docker-compose stop
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}[WARNING]${NC} Some services may not have stopped cleanly"
fi

echo ""
echo -e "${BLUE}[STEP 2/3]${NC} Removing Docker containers..."
echo "-----------------------------------------"
docker-compose down
if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR]${NC} Failed to remove containers"
    exit 1
fi

echo ""
echo -e "${BLUE}[STEP 3/3]${NC} Checking for remaining containers..."
echo "-----------------------------------------"
docker-compose ps

echo ""
echo -e "${GREEN}====================================="
echo "  SHUTDOWN COMPLETE"
echo "=====================================${NC}"
echo ""
echo "All services have been stopped."
echo ""
echo "Options:"
echo "  - Run './start-docker.sh' to restart"
echo "  - Run 'docker-compose down -v' to also remove volumes"
echo "====================================="
echo ""
