@echo off
setlocal EnableExtensions EnableDelayedExpansion
set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "APP_DIR=%%~fI"
set "ENV_FILE=%APP_DIR%\.env.micro"
set "TMP_ENV=%TEMP%\microflyton_env_%RANDOM%_%RANDOM%.tmp"

set "MYSQL_VERSION=8.0.36"
set "MYSQL_DIR=C:\mysql_lite"
set "MYSQL_BIN=%MYSQL_DIR%\bin"
set "MYSQL_URL=https://dev.mysql.com/get/Downloads/MySQL-8.0/mysql-%MYSQL_VERSION%-winx64.zip"

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

echo [3/5] Installing MySQL...
if exist "%MYSQL_BIN%\mysqld.exe" (
  echo MySQL already installed at %MYSQL_DIR%
  goto mysql_start
)

if not exist "%MYSQL_DIR%" mkdir "%MYSQL_DIR%"
cd /d "%MYSQL_DIR%"

echo Downloading MySQL v%MYSQL_VERSION%...
curl -L -o mysql.zip "%MYSQL_URL%"
if errorlevel 1 (
  echo ERROR: Download failed. Check internet connection.
  exit /b 1
)

echo Extracting...
tar -xf mysql.zip --strip-components=1
del mysql.zip

echo Creating config...
(
  echo [mysqld]
  echo basedir=%MYSQL_DIR:\=/%
  echo datadir=%MYSQL_DIR:\=/%/data
  echo port=3306
  echo innodb_buffer_pool_size=128M
  echo max_connections=10
) > "%MYSQL_DIR%\my.ini"

echo Initializing database...
"%MYSQL_BIN%\mysqld.exe" --initialize-insecure --console --defaults-file="%MYSQL_DIR%\my.ini"
if errorlevel 1 (
  echo ERROR: MySQL initialization failed.
  exit /b 1
)

echo Installing Windows service...
"%MYSQL_BIN%\mysqld.exe" --install MySQL_Lite --defaults-file="%MYSQL_DIR%\my.ini"

:mysql_start
echo Starting MySQL service...
net start MySQL_Lite 2>nul
if errorlevel 2 (
  echo ERROR: Could not start MySQL_Lite service.
  exit /b 1
)

echo Waiting for MySQL to be ready...
set "READY=0"
for /l %%i in (1,1,15) do (
  if "!READY!"=="0" (
    "%MYSQL_BIN%\mysql.exe" -u root --protocol=TCP --host=127.0.0.1 --connect-timeout=2 --execute="SELECT 1;" >nul 2>nul
    if not errorlevel 1 set "READY=1"
    if "!READY!"=="0" (
      echo   attempt %%i/15...
      timeout /t 2 /nobreak >nul
    )
  )
)
if "!READY!"=="0" (
  echo ERROR: MySQL did not respond after 30 seconds.
  exit /b 1
)

echo [4/5] Initializing database and tables...
"%MYSQL_BIN%\mysql.exe" -u root --protocol=TCP --host=127.0.0.1 < "%SCRIPT_DIR%init_tables.sql"
if errorlevel 1 (
  echo ERROR: Database initialization failed.
  exit /b 1
)

echo [5/5] Updating .env.micro for MySQL...
python -c "
import sys
env_file = sys.argv[1]
lines = open(env_file, encoding='utf-8').readlines()
set_keys = {'DB_BACKEND':'mysql','hostname':'127.0.0.1','username':'fly','password':'1964','database':'fly','is_mic':'0'}
remove_keys = {'DB_PATH'}
result = []
seen = set()
for line in lines:
    s = line.strip()
    if not s or s.startswith('#') or '=' not in s:
        result.append(line)
        continue
    k = s.split('=',1)[0].strip()
    if k in remove_keys:
        continue
    if k in set_keys:
        result.append(f'{k}={set_keys[k]}\n')
        seen.add(k)
    else:
        result.append(line)
for k,v in set_keys.items():
    if k not in seen:
        result.append(f'{k}={v}\n')
open(env_file,'w',encoding='utf-8').writelines(result)
print('env updated')
" "%ENV_FILE%"
if errorlevel 1 (
  echo WARNING: Could not update .env.micro
  exit /b 1
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
echo MySQL     : %MYSQL_DIR%
echo Database  : fly  /  user: fly  /  password: 1964
exit /b 0
