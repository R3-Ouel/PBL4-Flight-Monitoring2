@echo off
pushd "%~dp0\.."

echo Stopping existing simulator processes (if any)...
powershell -Command "Get-CimInstance Win32_Process | Where-Object { ($_.Name -match 'python') -and ($_.CommandLine -match 'fake.py|mission_planner|simulator.py|mission_planner_simulation.py') } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }" 2>nul

timeout /T 1 >nul

REM Prefer simulators\venv (Python 3.9.7), then backend\sim_venv, then backend\venv
if exist simulators\venv\Scripts\activate.bat (
    call simulators\venv\Scripts\activate.bat
) else if exist backend\sim_venv\Scripts\activate.bat (
    call backend\sim_venv\Scripts\activate.bat
) else if exist backend\venv\Scripts\activate.bat (
    call backend\venv\Scripts\activate.bat
) else (
    echo [WARN] No virtualenv found; using system python
)

echo Starting fake simulator (simulators\fake.py)...
if exist simulators\fake.py (
    start "FakeSim" cmd /k "python simulators\fake.py"
) else (
    echo [WARN] simulators\fake.py not found
)

timeout /T 2 >nul

REM mission planner may be under simulators/ or backend/drone/
if exist simulators\mission_planner.py (
    start "MissionPlanner" cmd /k "python simulators\mission_planner.py"
) else if exist backend\drone\mission_planner_simulation.py (
    start "MissionPlanner" cmd /k "python backend\drone\mission_planner_simulation.py"
) else (
    echo [WARN] mission planner script not found
)

popd
