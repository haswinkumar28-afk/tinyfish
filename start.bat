@echo off
title CampusCopilot Launcher
echo ===================================================
echo Starting CampusCopilot Backend & Frontend...
echo ===================================================
cd /d "%~dp0"

echo [1/2] Starting FastAPI Backend on port 8000...
start "CampusCopilot Backend" cmd /k "cd /d %~dp0 && .venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000"

echo [2/2] Starting Vite Frontend on port 3000...
start "CampusCopilot Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo Waiting for servers to initialize...
timeout /t 3 /nobreak >nul

echo Opening browser at http://localhost:3000...
start http://localhost:3000

echo ===================================================
echo CampusCopilot is now live at http://localhost:3000
echo ===================================================
