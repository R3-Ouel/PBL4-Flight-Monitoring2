@echo off
REM Lance le backend FastAPI et le simulateur dans des fenêtres séparées

cd /d %~dp0

REM Démarre le serveur Uvicorn
start "FastAPI" cmd /k "venv\Scripts\activate.bat && python -m uvicorn main:app --host 127.0.0.1 --port 8000"

REM Démarre le simulateur (qui POST vers /push)
start "Simulator" cmd /k "venv\Scripts\activate.bat && python hardware\simulator.py"

echo Backend started in separate windows.
exit /b 0
