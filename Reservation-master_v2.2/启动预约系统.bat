@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    .venv\Scripts\python.exe Start.py
    goto end
)
if exist ".venvin\python.exe" (
    .venvin\python.exe Start.py
    goto end
)
python Start.py
if errorlevel 1 (
    echo Failed to start. Make sure Python is installed.
    pause
)
:end
