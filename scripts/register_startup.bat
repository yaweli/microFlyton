@echo off
setlocal EnableExtensions EnableDelayedExpansion
set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "APP_DIR=%%~fI"
set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "STARTUP_FILE=%STARTUP_DIR%\MicroFlyton.bat"
if not exist "%STARTUP_DIR%" mkdir "%STARTUP_DIR%"
(
  echo @echo off
  echo call "%APP_DIR%\scripts\run_microflyton.bat"
) > "%STARTUP_FILE%"
echo Startup registration created:
echo %STARTUP_FILE%
exit /b 0
