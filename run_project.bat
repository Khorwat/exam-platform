@echo off
echo ==========================================
echo Starting Exam Platform (Fast Mode - Port 8001)
echo ==========================================

echo Activating virtual environment...
if exist "venv" (
    call venv\Scripts\activate
) else (
    echo Error: Virtual environment 'venv' not found!
    echo Please run the setup once first or install requirements.
    pause
    exit /b
)

echo.
echo Launching browser in 3 seconds...
timeout /t 3 >nul
start http://127.0.0.1:8001/frontend/login.html

echo.
echo Starting Django Server on Port 8001...
echo Press Ctrl+C to stop the server.
python manage.py runserver 8001

pause
