@echo off
setlocal EnableExtensions EnableDelayedExpansion
set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "APP_DIR=%%~fI"
set "ENV_FILE=%APP_DIR%\.env.micro"
set "STARTUP_FILE=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\MicroFlyton.bat"
set "PORT=8080"
set "TEMP_DELETE=%TEMP%\microflyton_delete_%RANDOM%_%RANDOM%.bat"

if exist "%ENV_FILE%" (
  for /f "usebackq tokens=1,* delims==" %%A in ("%ENV_FILE%") do (
    if /i "%%~A"=="PORT" set "PORT=%%~B"
  )
)

if exist "%STARTUP_FILE%" del /f /q "%STARTUP_FILE%" >nul 2>nul

taskkill /f /fi "WINDOWTITLE eq MicroFlyton Server*" >nul 2>nul
for /f "tokens=5" %%P in ('netstat -ano ^| findstr /r /c:":%PORT% .*LISTENING"') do (
  taskkill /f /pid %%P >nul 2>nul
)

(
  echo @echo off
  echo cd /d C:\
  echo :retry
  echo if not exist "%APP_DIR%" goto done
  echo rmdir /s /q "%APP_DIR%" ^>nul 2^>nul
  echo if exist "%APP_DIR%" timeout /t 1 /nobreak ^>nul
  echo if exist "%APP_DIR%" goto retry
  echo :done
  echo del /f /q "%%~f0" ^>nul 2^>nul
) > "%TEMP_DELETE%"

start "" /min cmd /c "%TEMP_DELETE%"

echo Uninstall scheduled.
echo Project folder will be removed:
echo %APP_DIR%
echo Database in C:\sqlite_microflyton is preserved.
exit
