@echo off
setlocal EnableExtensions

:: ============================================================
::  WIN-VIPER 2026 PRO - EXE LAUNCHER
::  Iron Will Interactive
:: ============================================================

title WIN-VIPER 2026 PRO - Launcher
color 0B

set "ROOT_DIR=%~dp0"
set "MAIN_DIR=%ROOT_DIR%Main"
set "EXE_NAME=WinViper_Pro_2026.exe"
set "EXE_PATH=%MAIN_DIR%\%EXE_NAME%"

cls
echo.
echo  ============================================================
echo   WIN-VIPER 2026 PRO
echo   Iron Will Interactive - Windows Optimization Launcher
echo  ============================================================
echo.

if not exist "%MAIN_DIR%" (
    echo [ERROR] Missing Main folder.
    echo Expected: "%MAIN_DIR%"
    echo.
    echo Extract the full WIN-VIPER folder before running this launcher.
    echo Do not run it directly from inside the ZIP preview window.
    echo.
    pause
    exit /b 1
)

if not exist "%EXE_PATH%" (
    echo [ERROR] Missing executable.
    echo Expected: "%EXE_PATH%"
    echo.
    echo Make sure this file exists:
    echo Main\%EXE_NAME%
    echo.
    pause
    exit /b 1
)

:: Detect admin rights. If not elevated, relaunch this same BAT as admin.
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Administrator permissions are recommended for WIN-VIPER.
    echo [INFO] Requesting UAC elevation...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

pushd "%MAIN_DIR%" >nul

echo [OK] Running with Administrator permissions.
echo [OK] Launching: %EXE_NAME%
echo.

start "WIN-VIPER 2026 PRO" /wait "%EXE_PATH%"
set "APP_EXIT=%ERRORLEVEL%"

popd >nul

echo.
echo [DONE] WIN-VIPER closed with exit code: %APP_EXIT%
echo.
pause
exit /b %APP_EXIT%
