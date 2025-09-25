# PowerShell script to run FastAPI application
# Usage: .\run_api.ps1

Write-Host "Starting Time Deposit FastAPI Application..." -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green

# Get the directory where the script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Check if virtual environment exists
if (!(Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "Virtual environment not found! Please ensure venv folder exists." -ForegroundColor Red
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

# Activate virtual environment and run the application
try {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
    
    Write-Host "Starting FastAPI server..." -ForegroundColor Yellow
    Write-Host "API will be available at: http://127.0.0.1:8000" -ForegroundColor Cyan
    Write-Host "API Documentation at: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Magenta
    Write-Host ""
    
    python src\main.py
}
catch {
    Write-Host "Error occurred: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}
