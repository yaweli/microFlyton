@echo off
setlocal EnableExtensions

set "APP_DIR=C:\microflyton"
set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "STARTUP_FILE=%STARTUP_DIR%\MicroFlyton.bat"

if not exist "%APP_DIR%\scripts\run_microflyton.bat" (
    echo ERROR: run_microflyton.bat was not found in:
    echo %APP_DIR%\scripts
    exit /b 1
)

(
echo @echo off
echo call "%APP_DIR%\scripts\run_microflyton.bat"
) > "%STARTUP_FILE%"

echo Startup registration completed.
echo MicroFlyton will start automatically when Windows starts.
exit /b 0
