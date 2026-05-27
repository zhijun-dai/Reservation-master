@echo off
cd /d "%~dp0"
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Install Python first
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)
python -m venv .venv
.venv\Scripts\pip install -r backend\requirements.txt
echo Done. Run qidong.bat
pause
