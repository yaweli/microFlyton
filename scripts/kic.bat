@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "APP_DIR=%%~fI"

set "ENV_FILE=%APP_DIR%\.env.micro"
if not exist "%ENV_FILE%" set "ENV_FILE=%APP_DIR%\.env.micro.example"

set "DB_PATH_RAW="
if exist "%ENV_FILE%" (
    for /f "usebackq tokens=1,* delims==" %%A in ("%ENV_FILE%") do (
        if /i "%%~A"=="DB_PATH" set "DB_PATH_RAW=%%~B"
    )
)

if not defined DB_PATH_RAW set "DB_PATH_RAW=.\Server\data\microflyton.db"

set "FIRST_CHAR=%DB_PATH_RAW:~0,1%"
if "%FIRST_CHAR%"=="." (
    set "DB_PATH=%APP_DIR%\%DB_PATH_RAW%"
) else (
    set "DB_PATH=%DB_PATH_RAW%"
)

for %%I in ("%DB_PATH%") do set "DB_PATH=%%~fI"

:menu
cls
echo ==================================
echo KIC Console
echo Project: %APP_DIR%
echo Database: %DB_PATH%
echo ==================================
echo.
echo Commands:
echo   sql   - Open SQLite terminal
echo   exit  - Exit
echo.

set /p "CMD_IN=Enter command: "

if /i "%CMD_IN%"=="sql" goto run_sql
if /i "%CMD_IN%"=="exit" exit /b 0

echo.
echo Unknown command: %CMD_IN%
pause
goto menu

:run_sql
set "SQLITE_EXE="
where sqlite3 >nul 2>nul
if not errorlevel 1 set "SQLITE_EXE=sqlite3"

if not defined SQLITE_EXE (
    if exist "%SCRIPT_DIR%sqlite3.exe" set "SQLITE_EXE=%SCRIPT_DIR%sqlite3.exe"
)

if not defined SQLITE_EXE (
    echo.
    echo ERROR: sqlite3 was not found in PATH.
    echo Install it or place sqlite3.exe inside:
    echo %SCRIPT_DIR%
    echo.
    echo Suggested install command:
    echo winget install SQLite.SQLite
    echo.
    pause
    goto menu
)

if not exist "%DB_PATH%" (
    echo.
    echo WARNING: Database file does not exist yet:
    echo %DB_PATH%
    echo.
    echo SQLite may create a new empty database if you continue.
    choice /c YN /m "Continue anyway"
    if errorlevel 2 goto menu
)

echo.
echo Opening SQLite:
echo %DB_PATH%
echo.
echo Type .tables to list tables
echo Type .schema to view schema
echo Type .exit to return to KIC Console
echo.

"%SQLITE_EXE%" "%DB_PATH%"

echo.
echo SQLite session closed.
pause
goto menu
