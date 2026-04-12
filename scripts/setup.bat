@echo off
setlocal enabledelayedexpansion

title Flight Mechanics Setup - Install Python 3.14 (backend) and 3.9.7 (simulators)

echo Starting setup: install Python interpreters and create venvs...

pushd "%~dp0\.."
set REPO_ROOT=%CD%

set INSTALL_DIR=%REPO_ROOT%\backend\python
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

set PY314_URL=https://www.python.org/ftp/python/3.14.0/python-3.14.0-amd64.exe
set PY397_URL=https://www.python.org/ftp/python/3.9.7/python-3.9.7-amd64.exe

set PY314_INSTALLER=%TEMP%\python-3.14.0-amd64.exe
set PY397_INSTALLER=%TEMP%\python-3.9.7-amd64.exe

set PY314_TARGET=%INSTALL_DIR%\python314
set PY397_TARGET=%INSTALL_DIR%\python397

set PY314_EXE=%PY314_TARGET%\python.exe
set PY397_EXE=%PY397_TARGET%\python.exe

echo.
if exist "%PY314_EXE%" (
    echo Python 3.14 already installed at %PY314_EXE%
) else (
    echo Downloading Python 3.14 installer...
    powershell -Command "Try { Invoke-WebRequest -Uri '%PY314_URL%' -OutFile '%PY314_INSTALLER%' -UseBasicParsing } Catch { Exit 1 }"
    if exist "%PY314_INSTALLER%" (
        echo Installing Python 3.14 to %PY314_TARGET% (quiet)...
        powershell -Command "Start-Process -FilePath '%PY314_INSTALLER%' -ArgumentList '/quiet','InstallAllUsers=0','TargetDir=\"%PY314_TARGET%\"','PrependPath=0','Include_pip=1' -Wait"
    ) else (
        echo [WARN] Failed to download Python 3.14 installer. Please download manually to %PY314_INSTALLER%
    )
)

echo.
if exist "%PY397_EXE%" (
    echo Python 3.9.7 already installed at %PY397_EXE%
) else (
    echo Downloading Python 3.9.7 installer...
    powershell -Command "Try { Invoke-WebRequest -Uri '%PY397_URL%' -OutFile '%PY397_INSTALLER%' -UseBasicParsing } Catch { Exit 1 }"
    if exist "%PY397_INSTALLER%" (
        echo Installing Python 3.9.7 to %PY397_TARGET% (quiet)...
        powershell -Command "Start-Process -FilePath '%PY397_INSTALLER%' -ArgumentList '/quiet','InstallAllUsers=0','TargetDir=\"%PY397_TARGET%\"','PrependPath=0','Include_pip=1' -Wait"
    ) else (
        echo [WARN] Failed to download Python 3.9.7 installer. Please download manually to %PY397_INSTALLER%
    )
)

echo.
REM Create backend venv using Python 3.14 if available
if exist "%PY314_EXE%" (
    echo Creating backend venv using Python 3.14...
    "%PY314_EXE%" -m venv "%REPO_ROOT%\backend\venv"
    if exist "%REPO_ROOT%\backend\venv\Scripts\activate.bat" (
        call "%REPO_ROOT%\backend\venv\Scripts\activate.bat"
        python -m pip install --upgrade pip setuptools wheel
        if exist "%REPO_ROOT%\backend\requirements.txt" (
            pip install -r "%REPO_ROOT%\backend\requirements.txt"
        )
    )
) else (
    echo [WARN] Python 3.14 not found; falling back to system python for backend venv.
    python -m venv "%REPO_ROOT%\backend\venv"
    if exist "%REPO_ROOT%\backend\venv\Scripts\activate.bat" (
        call "%REPO_ROOT%\backend\venv\Scripts\activate.bat"
        python -m pip install --upgrade pip setuptools wheel
        if exist "%REPO_ROOT%\backend\requirements.txt" pip install -r "%REPO_ROOT%\backend\requirements.txt"
    )
)

echo.
REM Create simulators venv using Python 3.9.7 if available
if exist "%PY397_EXE%" (
    echo Creating simulators venv using Python 3.9.7...
    "%PY397_EXE%" -m venv "%REPO_ROOT%\simulators\venv"
    if exist "%REPO_ROOT%\simulators\venv\Scripts\activate.bat" (
        call "%REPO_ROOT%\simulators\venv\Scripts\activate.bat"
        python -m pip install --upgrade pip setuptools wheel
        if exist "%REPO_ROOT%\simulators\requirements.txt" (
            pip install -r "%REPO_ROOT%\simulators\requirements.txt"
        )
    )
) else (
    echo [WARN] Python 3.9.7 not found; falling back to system python for simulators venv.
    python -m venv "%REPO_ROOT%\simulators\venv"
    if exist "%REPO_ROOT%\simulators\venv\Scripts\activate.bat" (
        call "%REPO_ROOT%\simulators\venv\Scripts\activate.bat"
        python -m pip install --upgrade pip setuptools wheel
        if exist "%REPO_ROOT%\simulators\requirements.txt" pip install -r "%REPO_ROOT%\simulators\requirements.txt"
    )
)

echo.
echo Setup finished.
popd
pause
