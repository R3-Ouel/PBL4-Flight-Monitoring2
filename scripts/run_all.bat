@echo off
pushd "%~dp0\.."

echo Démarrage du frontend...
start "Frontend" powershell -NoExit -Command "Set-Location -Path '%CD%\frontend'; flutter pub get; flutter run -d windows"

echo Attente d'au moins 20 secondes avant de démarrer le backend...
timeout /T 20 /NOBREAK >nul

echo Démarrage du backend...
start "Backend" cmd /k "%~dp0run_backend.bat"

popd
