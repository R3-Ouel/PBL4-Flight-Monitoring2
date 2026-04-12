@echo off
REM Start backend FastAPI (uvicorn) using backend venv if available

pushd "%~dp0\.."

if exist backend\venv\Scripts\activate.bat (
    call backend\venv\Scripts\activate.bat
) else (
    echo [WARN] backend\venv not found; using system python
)

pushd backend
echo Starting backend (uvicorn main:app)
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
popd

popd
