@echo off
setlocal enabledelayedexpansion

:: ============================================
:: Time Deposit API - Docker Startup Script
:: ============================================

:: Navigate to project root (two levels up from scripts/windows)
cd /d "%~dp0\..\.."

:: Colors (using echo with special characters)
echo.
echo =====================================
echo   TIME DEPOSIT API - DOCKER STARTUP
echo =====================================
echo.

:: Step 1: Build Docker Images
echo [STEP 1/5] Building Docker images...
echo -----------------------------------------
docker-compose build
if %errorlevel% neq 0 (
    echo [ERROR] Failed to build Docker images
    pause
    exit /b 1
)

:: Step 2: Start Services
echo.
echo [STEP 2/5] Starting Docker services...
echo -----------------------------------------
docker-compose up -d
if %errorlevel% neq 0 (
    echo [ERROR] Failed to start Docker services
    pause
    exit /b 1
)

:: Step 3: Wait for Services
echo.
echo [STEP 3/5] Waiting for services to initialize...
echo -----------------------------------------
echo Please wait 10 seconds...
timeout /t 10 /nobreak >nul

:: Step 4: Health Check
echo.
echo [STEP 4/5] Performing health check...
echo -----------------------------------------
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Health check failed. Services may still be starting...
) else (
    echo [OK] Health check passed
)

:: Step 5: Test Endpoints
echo.
echo [STEP 5/5] Testing API endpoints...
echo -----------------------------------------
echo.
echo Testing Health Endpoint:
curl -s http://localhost:8000/health
echo.
echo.
echo Testing GET /time-deposits:
curl -s http://localhost:8000/time-deposits | python -m json.tool 2>nul || curl -s http://localhost:8000/time-deposits
echo.
echo.
echo Testing PUT /time-deposits/updateBalances:
curl -s -X PUT http://localhost:8000/time-deposits/updateBalances
echo.
echo.

:: Success Message
echo =====================================
echo   STARTUP COMPLETE - API IS READY!
echo =====================================
echo.
echo Service URLs:
echo   - API:     http://localhost:8000
echo   - Swagger: http://localhost:8000/docs
echo   - ReDoc:   http://localhost:8000/redoc
echo   - Health:  http://localhost:8000/health
echo.
echo Database:
echo   - Host: localhost
echo   - Port: 5432
echo   - Name: timedeposit_db
echo.
echo To stop services, run: stop-docker.cmd
echo =====================================
echo.
pause
