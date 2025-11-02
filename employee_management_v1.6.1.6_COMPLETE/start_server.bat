@echo off
chcp 65001 >nul 2>&1
echo ========================================
echo Starting Employee Management System...
echo ========================================
echo.
echo Server will start at: http://127.0.0.1:8000
echo Press Ctrl+C to stop the server
echo.
python manage.py runserver
pause
