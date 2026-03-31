@echo off
setlocal EnableExtensions EnableDelayedExpansion
set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "APP_DIR=%%~fI"
title Command Prompt - kic

:menu
call :load_env
cls
echo ==================================
echo KIC Console
echo Project: %APP_DIR%
echo Database: %DB_PATH%
echo Version: 2026.03.30
echo ==================================
echo.
echo Commands:
echo sql      - Open SQLite terminal
echo install  - Prepare folders and DB path
echo run      - Run MicroFlyton
echo register - Register MicroFlyton in Windows startup
echo delete   - Delete and uninstall MicroFlyton code
echo pull     - Pull latest code from GitHub safely
echo.
echo Press Enter on empty command to exit.
echo.
set "CMD_IN="
set /p "CMD_IN=Enter command: "
if not defined CMD_IN exit /b 0
if /i "!CMD_IN!"=="sql" goto run_sql
if /i "!CMD_IN!"=="install" goto install_app
if /i "!CMD_IN!"=="run" goto run_app
if /i "!CMD_IN!"=="register" goto register_app
if /i "!CMD_IN!"=="delete" goto delete_app
if /i "!CMD_IN!"=="pull" goto pull_app
echo.
echo Unknown command: !CMD_IN!
pause
goto menu

:load_env
set "ENV_FILE=%APP_DIR%\.env.micro"
set "DB_PATH_RAW=C:\sqlite_microflyton\microflyton.db"
set "PORT=8080"
if exist "%ENV_FILE%" (
  for /f "usebackq tokens=1,* delims==" %%A in ("%ENV_FILE%") do (
    if /i "%%~A"=="DB_PATH" set "DB_PATH_RAW=%%~B"
    if /i "%%~A"=="PORT" set "PORT=%%~B"
  )
)
set "FIRST_CHAR=%DB_PATH_RAW:~0,1%"
if "%FIRST_CHAR%"=="." (
  set "DB_PATH=%APP_DIR%\%DB_PATH_RAW%"
) else (
  set "DB_PATH=%DB_PATH_RAW%"
)
for %%I in ("%DB_PATH%") do set "DB_PATH=%%~fI"
exit /b 0

:install_app
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
echo This console will close to finish uninstall safely.
echo ************************************************************
echo.
set "CONFIRM_DELETE="
set /p "CONFIRM_DELETE=Type y to continue: "
if /i not "!CONFIRM_DELETE!"=="y" (
  echo Delete aborted.
  pause
  goto menu
)
start "" /min cmd /c ""%SCRIPT_DIR%cleanup_uninstall.bat""
exit

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
set "SQLITE_EXE="
where sqlite3 >nul 2>nul
if not errorlevel 1 set "SQLITE_EXE=sqlite3"
if not defined SQLITE_EXE (
  echo.
  echo ERROR: sqlite3 was not found in PATH.
  echo Install SQLite CLI or open the DB with another SQLite tool.
  echo.
  pause
  goto menu
)
if not exist "%DB_PATH%" (
  echo.
  echo WARNING: Database file does not exist yet:
  echo %DB_PATH%
  echo.
  choice /c YN /m "Continue anyway"
  if errorlevel 2 goto menu
)
"%SQLITE_EXE%" "%DB_PATH%"
goto menu
