@echo off
setlocal
cd /d "%~dp0"

if not exist "backend\.venv\Scripts\python.exe" (
  echo Backend virtual environment was not found.
  echo Run these commands first:
  echo   cd backend
  echo   python -m venv .venv
  echo   .venv\Scripts\python.exe -m pip install -r requirements-dev.txt
  pause
  exit /b 1
)

start "MERN AI Backend" cmd /k call "%~dp0backend\run-backend-8001.cmd"
start "MERN AI Frontend" cmd /k call "%~dp0frontend\run-frontend.cmd"
