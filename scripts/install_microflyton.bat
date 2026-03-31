@echo off
setlocal EnableExtensions EnableDelayedExpansion
set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "APP_DIR=%%~fI"
set "ENV_FILE=%APP_DIR%\.env.micro"
set "TARGET_DB_DIR=C:\sqlite_microflyton"
set "TARGET_DB=%TARGET_DB_DIR%\microflyton.db"
set "OLD_DB=%APP_DIR%\server\data\microflyton.db"
set "LOG_DIR=%APP_DIR%\server\logs"
set "DATA_DIR=%APP_DIR%\server\data"
set "TMP_ENV=%TEMP%\microflyton_env_%RANDOM%_%RANDOM%.tmp"

echo [1/5] Checking Python...
where python >nul 2>nul
if errorlevel 1 (
  echo ERROR: python was not found in PATH.
  echo Install Python 3.11+ and rerun this script.
  exit /b 1
)

echo [2/5] Validating environment file...
if not exist "%ENV_FILE%" (
  echo ERROR: %ENV_FILE% was not found.
  exit /b 1
)

echo [3/5] Creating folders...
if not exist "%TARGET_DB_DIR%" mkdir "%TARGET_DB_DIR%"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
if not exist "%DATA_DIR%" mkdir "%DATA_DIR%"

echo [4/5] Updating DB path in .env.micro...
set "FOUND_DB_PATH=0"
(
  for /f "usebackq delims=" %%L in ("%ENV_FILE%") do (
    set "LINE=%%L"
    if /i "!LINE:~0,8!"=="DB_PATH=" (
      echo DB_PATH=%TARGET_DB%
      set "FOUND_DB_PATH=1"
    ) else (
      echo %%L
    )
  )
  if "!FOUND_DB_PATH!"=="0" echo DB_PATH=%TARGET_DB%
) > "%TMP_ENV%"
move /y "%TMP_ENV%" "%ENV_FILE%" >nul

echo [5/5] Checking database migration...
if exist "%TARGET_DB%" (
  echo External database already exists:
  echo %TARGET_DB%
) else (
  if exist "%OLD_DB%" (
    copy /y "%OLD_DB%" "%TARGET_DB%" >nul
    echo Migrated database to:
    echo %TARGET_DB%
  ) else (
    echo No existing database was found.
    echo A new database will be initialized on first server start.
  )
)

where git >nul 2>nul
if not errorlevel 1 (
  git -C "%APP_DIR%" rev-parse --is-inside-work-tree >nul 2>nul
  if not errorlevel 1 (
    git -C "%APP_DIR%" update-index --skip-worktree ".env.micro" >nul 2>nul
  )
)

echo.
echo Installation completed.
echo Code path : %APP_DIR%
echo Data path : %TARGET_DB%
exit /b 0
