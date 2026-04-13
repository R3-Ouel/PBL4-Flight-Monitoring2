@echo off
pushd "%~dp0\.."

echo Skipping process-kill step (disabled for parsing safety).

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
if not "%CHOICE%"=="" goto :handle_choice

:menu
cls
echo.
echo Select simulator to start:
echo   1) Fake simulator (simulators\fake.py)
echo   2) Mission Planner (simulators\mission_planner.py)
echo   3) Both
echo   q) Quit
echo.
set /P CHOICE=Entrez 1,2,3 ou q: 
if "%CHOICE%"=="" goto :menu

:handle_choice
if /I "%CHOICE%"=="q" goto :end
if "%CHOICE%"=="1" goto :start_fake
if "%CHOICE%"=="2" goto :start_mp
if "%CHOICE%"=="3" goto :start_both
if /I "%CHOICE%"=="fake" goto :start_fake
if /I "%CHOICE%"=="mp" goto :start_mp

echo.
echo Choix invalide: %CHOICE%
set "CHOICE="
timeout /T 2 >nul
goto :menu

:start_fake
echo Starting fake simulator (simulators\fake.py)...
if exist simulators\fake.py (
    start "FakeSim" cmd /k "python simulators\fake.py"
) else (
    echo [WARN] simulators\fake.py not found
)
set "CHOICE="
goto :menu

:start_mp
echo Starting Mission Planner simulator...
if exist simulators\mission_planner.py (
    start "MissionPlanner" cmd /k "python simulators\mission_planner.py"
) else if exist backend\drone\mission_planner_simulation.py (
    start "MissionPlanner" cmd /k "python backend\drone\mission_planner_simulation.py"
) else (
    echo [WARN] mission planner script not found
)
set "CHOICE="
goto :menu

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
set "CHOICE="
goto :menu

:end
popd
