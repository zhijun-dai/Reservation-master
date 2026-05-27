@echo off
cd /d "%~dp0"
echo ================================
echo   Installing dependencies...
echo ================================
echo.

python --version >/dev/null 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python first.
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Found Python
python -m venv .venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment.
    pause
    exit /b 1
)

echo [OK] Virtual environment created
call .venv\Scripts\pip install -r backendequirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo ================================
echo   Done! You can now run the app.
echo   Double-click: qidong.bat
echo ================================
pause
