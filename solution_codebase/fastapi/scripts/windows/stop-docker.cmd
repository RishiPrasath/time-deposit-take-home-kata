@echo off
setlocal enabledelayedexpansion

:: ============================================
:: Time Deposit API - Docker Shutdown Script
:: ============================================

:: Navigate to project root (two levels up from scripts/windows)
cd /d "%~dp0\..\.."

echo.
echo =====================================
echo   TIME DEPOSIT API - DOCKER SHUTDOWN
echo =====================================
echo.

:: Confirm shutdown
set /p confirm="Are you sure you want to stop all services? (Y/N): "
if /i not "%confirm%"=="Y" (
    echo Shutdown cancelled.
    pause
    exit /b 0
)

echo.
echo [STEP 1/3] Stopping Docker containers...
echo -----------------------------------------
docker-compose stop
if %errorlevel% neq 0 (
    echo [WARNING] Some services may not have stopped cleanly
)

echo.
echo [STEP 2/3] Removing Docker containers...
echo -----------------------------------------
docker-compose down
if %errorlevel% neq 0 (
    echo [ERROR] Failed to remove containers
    pause
    exit /b 1
)

echo.
echo [STEP 3/3] Checking for remaining containers...
echo -----------------------------------------
docker-compose ps

echo.
echo =====================================
echo   SHUTDOWN COMPLETE
echo =====================================
echo.
echo All services have been stopped.
echo.
echo Options:
echo   - Run 'start-docker.cmd' to restart
echo   - Run 'docker-compose down -v' to also remove volumes
echo =====================================
echo.
pause
