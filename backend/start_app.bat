@echo off
echo 🏀 NBA Dashboard Startup
echo ================================
echo.

REM Controleer of Python geïnstalleerd is
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is niet geïnstalleerd of niet in PATH
    pause
    exit /b 1
)

REM Installeer dependencies
echo 🔧 Installeren van dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Fout bij installeren dependencies
    pause
    exit /b 1
)

echo ✅ Dependencies geïnstalleerd!
echo.
echo 🚀 Starten van Flask app...
echo.

REM Start Flask app
python start_app.py

pause 