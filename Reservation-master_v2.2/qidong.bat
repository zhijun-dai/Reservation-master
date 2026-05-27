@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    .venv\Scripts\python.exe Start.py
    goto end
)
if exist ".venv\bin\python.exe" (
    .venv\bin\python.exe Start.py
    goto end
)
python Start.py
if errorlevel 1 (
    echo Failed. Install Python first.
    pause
)
:end
