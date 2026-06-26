@echo off
cd /d "%~dp0"
echo Starting File Sharing Platform...
timeout /t 2 /nobreak
start http://127.0.0.1:8000/docs
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
