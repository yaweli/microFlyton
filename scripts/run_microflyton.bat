@echo off
setlocal EnableExtensions

set "APP_DIR=C:\microflyton"
set "URL=http://127.0.0.1:8080/pages/index.html"
set "PORT=8080"

if not exist "%APP_DIR%" (
    echo ERROR: %APP_DIR% was not found.
    exit /b 1
)

cd /d "%APP_DIR%"

netstat -ano | findstr ":%PORT%" >nul
if %errorlevel%==0 (
    start "" "%URL%"
    echo MicroFlyton is already running.
    exit /b 0
)

start "MicroFlyton Server" cmd /k "cd /d %APP_DIR% && python -m http.server %PORT% --bind 127.0.0.1"

timeout /t 2 /nobreak >nul

start "" "%URL%"

echo MicroFlyton started.
exit /b 0
