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
REM We create the venv inside the `backend` folder so backend scripts use the correct env
pushd "%~dp0backend" >nul 2>&1 || (
    echo [ERROR] backend folder not found
    exit /b 1
)
if exist venv (
    echo Virtual environment already exists in backend\venv, skipping creation
) else (
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        popd >nul 2>&1
        exit /b 1
    )
    echo [✓] Virtual environment created at backend\venv
)
echo.

REM Activate virtual environment and install dependencies
echo [2/4] Activating virtual environment and installing packages in backend\venv...
call "%CD%\venv\Scripts\activate.bat"
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    popd >nul 2>&1
    exit /b 1
)

echo Upgrading pip...
python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    echo [ERROR] Failed to upgrade pip
    popd >nul 2>&1
    exit /b 1
)

echo Installing Python requirements from backend\requirements.txt...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install Python dependencies from requirements.txt
    popd >nul 2>&1
    pause
    exit /b 1
)

echo [✓] Python dependencies installed
popd >nul 2>&1
echo.
echo Setup complete! Activate backend virtualenv with:
echo    call backend\venv\Scripts\activate.bat
pause