@echo off
REM Relance uniquement la simulation puis relance le frontend (backend déjà lancé)

echo Tentative d'arret des processus 'simulator.py' existants...
powershell -Command "Get-CimInstance Win32_Process | Where-Object { ($_.Name -match 'python') -and ($_.CommandLine -match 'simulator.py') } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"

timeout /T 1 >nul

echo Démarrage du simulateur (venv)...
start "Simulator" powershell -NoExit -Command "& '%~dp0backend\venv\Scripts\python.exe' '%~dp0backend\hardware\simulator.py'"

timeout /T 2 >nul

echo Démarrage du frontend...
start "Frontend" powershell -NoExit -Command "Set-Location -Path '%~dp0frontend'; flutter pub get; flutter run -d windows"

echo Terminé.
