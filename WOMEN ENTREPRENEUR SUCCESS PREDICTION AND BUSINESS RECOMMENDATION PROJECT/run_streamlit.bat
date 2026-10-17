@echo off
title Launching Rural Women Entrepreneurship Platform
echo ========================================================
echo Starting Streamlit Web App...
echo ========================================================

set "PY_EXE="

:: 1. Check direct installed Python path on this PC
if exist "%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe" (
    set "PY_EXE=%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe"
    goto :RUN
)

:: 2. Check py launcher
py -0 >nul 2>nul
if %ERRORLEVEL% equ 0 (
    py -m streamlit run app.py
    pause
    exit /b
)

:: 3. Check general python command if not the WindowsApps stub
for /f "tokens=*" %%i in ('where python 2^>nul') do (
    echo %%i | findstr /i "WindowsApps" >nul
    if errorlevel 1 (
        set "PY_EXE=%%i"
        goto :RUN
    )
)

:RUN
if defined PY_EXE (
    "%PY_EXE%" -m streamlit run app.py
    pause
    exit /b
)

echo.
echo [ERROR] Working Python installation not detected.
echo Please run: python -m pip install -r requirements.txt
pause
