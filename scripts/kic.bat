@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "APP_DIR=%%~fI"

:menu
call :load_env
cls
echo ==================================
echo KIC Console
echo Project: %APP_DIR%
echo Database: %DB_HOST%/%DB_NAME%  user:%DB_USER%
echo Version: 2026.04.04
echo ==================================
echo.
echo Commands:
echo s  - sql      - Open SQLite terminal
echo i  - install  - Prepare folders and DB path
echo r  - run      - Run MicroFlyton service
echo u  - pull     - Pull latest code from GitHub safely
echo rg - register - Register MicroFlyton in Windows startup
echo delete        - Delete and uninstall MicroFlyton code
echo.
echo Press Enter on empty command to exit.
echo.

set "CMD_IN="
set /p "CMD_IN=Enter command: "
if not defined CMD_IN exit /b 0

if /i "!CMD_IN!"=="s"        goto run_sql
if /i "!CMD_IN!"=="sql"      goto run_sql

if /i "!CMD_IN!"=="i"        goto install_app
if /i "!CMD_IN!"=="install"  goto install_app

if /i "!CMD_IN!"=="r"        goto run_app
if /i "!CMD_IN!"=="run"      goto run_app

if /i "!CMD_IN!"=="u"        goto pull_app
if /i "!CMD_IN!"=="pull"     goto pull_app

if /i "!CMD_IN!"=="rg"       goto register_app
if /i "!CMD_IN!"=="register" goto register_app

if /i "!CMD_IN!"=="delete"   goto delete_app

echo.
echo Unknown command: !CMD_IN!
pause
goto menu

:load_env
set "ENV_FILE=%APP_DIR%\.env.micro"
set "DB_HOST=127.0.0.1"
set "DB_USER=fly"
set "DB_PASS=1964"
set "DB_NAME=fly"
set "PORT=8080"

if exist "%ENV_FILE%" (
  for /f "usebackq tokens=1,* delims==" %%A in ("%ENV_FILE%") do (
    if /i "%%~A"=="hostname" set "DB_HOST=%%~B"
    if /i "%%~A"=="username" set "DB_USER=%%~B"
    if /i "%%~A"=="password" set "DB_PASS=%%~B"
    if /i "%%~A"=="database" set "DB_NAME=%%~B"
    if /i "%%~A"=="PORT"     set "PORT=%%~B"
  )
)

exit /b 0

:install_app
net session >nul 2>nul
if errorlevel 1 (
  echo.
  echo ERROR: Install requires Administrator privileges.
  echo Please run kic.bat as Administrator.
  echo.
  pause
  goto menu
)
call "%SCRIPT_DIR%install_microflyton.bat"
pause
goto menu

:run_app
call "%SCRIPT_DIR%run_microflyton.bat"
pause
goto menu

:register_app
call "%SCRIPT_DIR%register_startup.bat"
pause
goto menu

:delete_app
echo.
echo ************************************************************
echo WARNING: You are about to delete the MicroFlyton code folder.
echo Startup registration will be removed.
echo The external database will be kept.
echo ************************************************************
echo.
set "CONFIRM_DELETE="
set /p "CONFIRM_DELETE=Type y to continue: "
if /i not "!CONFIRM_DELETE!"=="y" (
  echo Delete aborted.
  pause
  goto menu
)
call "%SCRIPT_DIR%cleanup_uninstall.bat"
exit /b 0

:pull_app
where git >nul 2>nul
if errorlevel 1 (
  echo.
  echo ERROR: git was not found in PATH.
  echo.
  pause
  goto menu
)

if not exist "%APP_DIR%\.git" (
  echo.
  echo ERROR: This folder is not a git working tree.
  echo.
  pause
  goto menu
)

git -C "%APP_DIR%" ls-files --error-unmatch "server/data/microflyton.db" >nul 2>nul
if not errorlevel 1 (
  echo.
  echo ERROR: server/data/microflyton.db is tracked by git.
  echo Pull aborted to protect runtime data.
  echo.
  pause
  goto menu
)

netstat -ano | findstr /r /c:":%PORT% .*LISTENING" >nul
if %errorlevel%==0 (
  echo.
  echo ERROR: Port %PORT% appears to be in use.
  echo Stop the running MicroFlyton server before pull.
  echo.
  pause
  goto menu
)

echo.
echo Pulling latest code...
git -C "%APP_DIR%" pull --ff-only
if errorlevel 1 (
  echo.
  echo Pull failed.
  pause
  goto menu
)

echo.
echo Re-applying install setup...
call "%SCRIPT_DIR%install_microflyton.bat"
if errorlevel 1 (
  echo.
  echo Install refresh failed after pull.
  pause
  goto menu
)

echo.
echo Pull completed.
pause
goto menu

:run_sql
call :load_env

set "MYSQL_EXE=C:\mysql_lite\bin\mysql.exe"
if not exist "%MYSQL_EXE%" (
  where mysql >nul 2>nul
  if not errorlevel 1 (
    set "MYSQL_EXE=mysql"
  ) else (
    echo.
    echo ERROR: mysql.exe not found.
    echo Run install first to set up MySQL.
    echo.
    pause
    goto menu
  )
)

echo.
echo Opening MySQL: %DB_HOST%/%DB_NAME%  user:%DB_USER%
echo Type \q to exit.
echo.
"%MYSQL_EXE%" --protocol=TCP -h%DB_HOST% -u%DB_USER% -p%DB_PASS% %DB_NAME%

echo.
echo MySQL session closed.
pause
goto menu
