@echo off
setlocal
title WIN-VIPER 2026 PRO - Initialization

:: Define Paths
set "ROOT_DIR=%~dp0"
set "MAIN_DIR=%ROOT_DIR%Main"
set "SCRIPT_PATH=%MAIN_DIR%\WinViper_Pro.py"

echo Checking system environment for Python 3...

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python is not installed.
    echo [!] Redirecting to download the latest stable version...
    start https://www.python.org/downloads/
    echo Please install Python and ensure "Add Python to PATH" is checked.
    pause
    exit
)

:: Navigate to the Main folder
cd /d "%MAIN_DIR%"

:: Run the script
echo [SUCCESS] Python detected. Launching WIN-VIPER 2026 PRO...
python "%SCRIPT_PATH%"

pause