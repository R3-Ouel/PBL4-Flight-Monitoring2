@echo off
setlocal enabledelayedexpansion

title Flight Mechanics Setup - Installing Environment

echo.
echo ============================================
echo  Flight Mechanics Environment Setup
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.11 from https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe
    pause
    exit /b 1
)

REM Create virtual environment
echo [1/4] Creating Python virtual environment...
if exist venv (
    echo Virtual environment already exists, skipping creation
) else (
    python -m venv venv
    echo [✓] Virtual environment created
)
echo.

REM Activate virtual environment and install dependencies
echo [2/4] Activating virtual environment and installing packages...
call cd backend
venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [✓]  dependencies installed
echo.
echo Setup complete! You can now activate the virtual environment using "call venv\Scripts\activate.bat" and run your Python scripts.
pause