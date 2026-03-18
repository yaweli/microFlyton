@echo off
set APP_DIR=C:\microflyton

where python >nul 2>nul
if errorlevel 1 (
    echo Python not found. Install with:
    echo winget install --id Python.Python.3.11 -e --source winget
    exit /b 1
)

if not exist "%APP_DIR%\logs" mkdir "%APP_DIR%\logs"
if not exist "%APP_DIR%\runtime" mkdir "%APP_DIR%\runtime"

echo ok > "%APP_DIR%\runtime\installed.flag"

echo Installation completed.
