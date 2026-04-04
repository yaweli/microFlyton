@echo off
setlocal EnableExtensions EnableDelayedExpansion
set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "APP_DIR=%%~fI"
set "ENV_FILE=%APP_DIR%\.env.micro"
set "STARTUP_FILE=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\MicroFlyton.bat"
set "MYSQL_DIR=C:\mysql_lite"
set "MYSQL_BIN=%MYSQL_DIR%\bin"
set "PORT=8080"
set "TEMP_DELETE=%TEMP%\microflyton_delete_%RANDOM%_%RANDOM%.bat"

net session >nul 2>nul
if errorlevel 1 (
  echo ERROR: Uninstall requires Administrator privileges.
  echo Please run kic.bat as Administrator.
  exit /b 1
)

if exist "%ENV_FILE%" (
  for /f "usebackq tokens=1,* delims==" %%A in ("%ENV_FILE%") do (
    if /i "%%~A"=="PORT" set "PORT=%%~B"
  )
)

rem Remove startup shortcut
if exist "%STARTUP_FILE%" del /f /q "%STARTUP_FILE%" >nul 2>nul

rem Kill MicroFlyton server
taskkill /f /fi "WINDOWTITLE eq MicroFlyton Server*" >nul 2>nul
for /f "tokens=5" %%P in ('netstat -ano ^| findstr /r /c:":%PORT% .*LISTENING"') do (
  taskkill /f /pid %%P >nul 2>nul
)

rem Stop and remove MySQL service
echo Stopping MySQL service...
net stop MySQL_Lite >nul 2>nul

sc query MySQL_Lite >nul 2>nul
if not errorlevel 1 (
  echo Removing MySQL service...
  if exist "%MYSQL_BIN%\mysqld.exe" (
    "%MYSQL_BIN%\mysqld.exe" --remove MySQL_Lite >nul 2>nul
  ) else (
    sc delete MySQL_Lite >nul 2>nul
  )
)

rem Delete MySQL binaries - keep data folder
if exist "%MYSQL_DIR%" (
  echo Removing MySQL binaries, keeping data...
  for /d %%D in ("%MYSQL_DIR%\*") do (
    if /i not "%%~nxD"=="data" rmdir /s /q "%%D" >nul 2>nul
  )
  del /f /q "%MYSQL_DIR%\*.*" >nul 2>nul
)

rem Schedule deletion of app folder (self-deleting temp bat)
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

echo.
echo Uninstall complete.
echo Code folder removed : %APP_DIR%
echo MySQL binaries removed : %MYSQL_DIR%  (service unregistered)
echo Database preserved  : %MYSQL_DIR%\data
exit
