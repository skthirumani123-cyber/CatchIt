@echo off
title BusFlow - Smart Bus Schedule & Management System
echo ======================================================================
echo    Starting BusFlow - Smart Bus Schedule & Management System
echo ======================================================================
echo.
set PYTHON_EXE=C:\Users\manu\AppData\Local\Programs\Python\Python311\python.exe

if not exist "%PYTHON_EXE%" (
    echo [ERROR] Python not found at %PYTHON_EXE%
    pause
    exit /b 1
)

echo [OK] Using Python 3.11 from: %PYTHON_EXE%
echo [OK] Starting Flask Application on http://127.0.0.1:5000 ...
echo.
"%PYTHON_EXE%" app.py
pause
