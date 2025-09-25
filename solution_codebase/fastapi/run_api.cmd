@echo off
REM Windows CMD script to run FastAPI application
REM Usage: run_api.cmd

echo Starting Time Deposit FastAPI Application...
echo =============================================

REM Change to the script directory
cd /d "%~dp0"

REM Activate virtual environment and run the application
call venv\Scripts\activate.bat
python src\main.py

REM Keep window open if there's an error
if %ERRORLEVEL% neq 0 (
    echo.
    echo Error occurred! Press any key to exit...
    pause >nul
)
