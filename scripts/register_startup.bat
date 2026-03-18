@echo off
setlocal EnableExtensions

set "APP_DIR=C:\microflyton"
set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT_PATH=%STARTUP_DIR%\MicroFlyton.bat"

(
echo @echo off
echo call "%APP_DIR%\scripts\run_microflyton.bat"
) > "%SHORTCUT_PATH%"

echo Startup registration completed.
