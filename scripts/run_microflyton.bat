@echo off
setlocal EnableExtensions EnableDelayedExpansion
set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "APP_DIR=%%~fI"
set "ENV_FILE=%APP_DIR%\.env.micro"
set "HOST=127.0.0.1"
set "PORT=8080"
set "START_URL="
if exist "%ENV_FILE%" (
  for /f "usebackq tokens=1,* delims==" %%A in ("%ENV_FILE%") do (
    if /i "%%~A"=="HOST" set "HOST=%%~B"
    if /i "%%~A"=="PORT" set "PORT=%%~B"
    if /i "%%~A"=="START_URL" set "START_URL=%%~B"
  )
)
if not defined START_URL set "START_URL=http://%HOST%:%PORT%/pages/index.html"

if not exist "%APP_DIR%\server\server.py" (
  echo ERROR: %APP_DIR%\server\server.py was not found.
  exit /b 1
)

netstat -ano | findstr /r /c:":%PORT% .*LISTENING" >nul
if %errorlevel%==0 (
  start "" "%START_URL%"
  echo MicroFlyton server is already running.
  exit /b 0
)

start "MicroFlyton Server" cmd /c "cd /d %APP_DIR% && set AUTO_OPEN_BROWSER=0 && python server\server.py"
timeout /t 2 /nobreak >nul
start "" "%START_URL%"
echo MicroFlyton started.
exit /b 0
