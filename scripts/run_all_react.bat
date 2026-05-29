@echo off
pushd "%~dp0\.."

echo Demarrage du frontend React...
start "Frontend React" powershell -NoExit -Command "Set-Location -Path '%CD%\frontend-react'; if (-not (Test-Path node_modules)) { npm install }; npm run dev"

echo Attente de 5 secondes avant le backend...
timeout /T 5 /NOBREAK >nul

echo Demarrage du backend...
start "Backend" cmd /k "%~dp0run_backend.bat"

popd
