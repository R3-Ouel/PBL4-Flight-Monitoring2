@echo off
pushd "%~dp0\..\frontend-react"
echo Demarrage du frontend React (Vite)...
if not exist node_modules (
  echo Installation des dependances npm...
  call npm install
)
start "Frontend React" cmd /k "npm run dev"
popd
