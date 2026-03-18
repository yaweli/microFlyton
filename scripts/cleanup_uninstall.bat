@echo off
setlocal EnableExtensions

set "APP_DIR=C:\microflyton"
set "STARTUP_FILE=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\MicroFlyton.bat"

if exist "%STARTUP_FILE%" del /f /q "%STARTUP_FILE%"

if exist "%APP_DIR%" (
    rmdir /s /q "%APP_DIR%"
)

echo MicroFlyton uninstalled.
exit /b 0
