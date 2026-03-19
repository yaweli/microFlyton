@echo off
setlocal EnableExtensions

set "APP_DIR=C:\microflyton"
set "SERVER_DIR=%APP_DIR%\Server"
set "LOG_DIR=%SERVER_DIR%\logs"
set "URL=http://127.0.0.1:8080/pages/index.html"
set "PORT=8080"

if not exist "%SERVER_DIR%\server.py" (
    echo ERROR: %SERVER_DIR%\server.py was not found.
    exit /b 1
)

if not exist "%LOG_DIR%" (
    mkdir "%LOG_DIR%"
)

netstat -ano | findstr ":%PORT%" >nul
if %errorlevel%==0 (
    start "" "%URL%"
    echo MicroFlyton is already running.
    exit /b 0
)

start "MicroFlyton Server" cmd /k "cd /d %SERVER_DIR% && python server.py"

timeout /t 2 /nobreak >nul

start "" "%URL%"

echo MicroFlyton started.
exit /b 0
