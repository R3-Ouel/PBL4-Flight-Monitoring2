@echo off
REM Lance le backend FastAPI et le simulateur dans des fenêtres séparées

cd /d %~dp0

REM Démarre le serveur Uvicorn
start "FastAPI" cmd /k "venv\Scripts\activate.bat && python -m uvicorn main:app --host 127.0.0.1 --port 8000"

REM Choix de la simulation: si argument 'mp' ou 'sim' fourni, on l'utilise, sinon prompt
if "%1"=="mp" goto MP
if "%1"=="sim" goto SIM

echo Choix de la simulation:
echo  1. Locale (hardware\simulator.py)
echo  2. Mission Planner / SITL (hardware\mission_planner_simulation.py)
set /p SIM_CHOICE=Entrez 1 ou 2 (default 1): 
if "%SIM_CHOICE%"=="2" goto MP

:SIM
start "Simulator" cmd /k "venv\Scripts\activate.bat && python hardware\simulator.py"
goto END

:MP
start "MissionPlanner" cmd /k "venv\Scripts\activate.bat && python hardware\mission_planner_simulation.py"

:END
echo Backend started in separate windows.
exit /b 0
