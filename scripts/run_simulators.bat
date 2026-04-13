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

REM Allow selecting which simulator to start: 1=fake, 2=mission planner, 3=both
set "CHOICE=%~1"
if "%CHOICE%"=="" (
    echo.
    echo Select simulator to start:
    echo   1) Fake simulator (simulators\fake.py)
    echo   2) Mission Planner (simulators\mission_planner.py)
    echo   3) Both
    set /P CHOICE=Entrez 1,2 ou 3 (q pour quitter): 
    if "%CHOICE%"=="" (
        echo Aucun choix fourni. Sortie.
        goto :end
    )
)

if /I "%CHOICE%"=="q" goto :end
if "%CHOICE%"=="1" goto :start_fake
if "%CHOICE%"=="2" goto :start_mp
if "%CHOICE%"=="3" goto :start_both
if /I "%CHOICE%"=="fake" goto :start_fake
if /I "%CHOICE%"=="mp" goto :start_mp

echo Choix invalide: %CHOICE%
goto :end

:start_fake
echo Starting fake simulator (simulators\fake.py)...
if exist simulators\fake.py (
    start "FakeSim" cmd /k "python simulators\fake.py"
) else (
    echo [WARN] simulators\fake.py not found
)
goto :end

:start_mp
echo Starting Mission Planner simulator...
if exist simulators\mission_planner.py (
    start "MissionPlanner" cmd /k "python simulators\mission_planner.py"
) else if exist backend\drone\mission_planner_simulation.py (
    start "MissionPlanner" cmd /k "python backend\drone\mission_planner_simulation.py"
) else (
    echo [WARN] mission planner script not found
)
goto :end

:start_both
echo Starting both simulators...
if exist simulators\fake.py (
    start "FakeSim" cmd /k "python simulators\fake.py"
) else (
    echo [WARN] simulators\fake.py not found
)
timeout /T 2 >nul
if exist simulators\mission_planner.py (
    start "MissionPlanner" cmd /k "python simulators\mission_planner.py"
) else if exist backend\drone\mission_planner_simulation.py (
    start "MissionPlanner" cmd /k "python backend\drone\mission_planner_simulation.py"
) else (
    echo [WARN] mission planner script not found
)

:end

popd
