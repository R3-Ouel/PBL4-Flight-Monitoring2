@echo off
REM Lance le frontend puis (après >=10s) le backend

echo Démarrage du frontend...
start "Frontend" powershell -NoExit -Command "Set-Location -Path '%~dp0frontend'; flutter pub get; flutter run -d windows"

echo Attente d'au moins 20 secondes avant de démarrer le backend...
timeout /T 20. /NOBREAK >nul

echo Démarrage du backend...
start "Backend" powershell -NoExit -Command "& '%~dp0backend\run_backend.bat'"

echo Terminé.
