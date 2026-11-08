@echo off
title AI Portfolio Analytics REST API
echo Starting FastAPI REST Server on http://localhost:8000 ...
echo Interactive API docs at http://localhost:8000/docs
"%~dp0python_env\python.exe" -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
pause
