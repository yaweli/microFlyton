@echo off
setlocal EnableExtensions EnableDelayedExpansion

net session >nul 2>nul
if errorlevel 1 (
  echo ERROR: This script must be run as Administrator.
  echo Right-click the script and select "Run as administrator".
  pause
  exit /b 1
)

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "APP_DIR=%%~fI"
set "ENV_FILE=%APP_DIR%\.env.micro"
set "TMP_ENV=%TEMP%\microflyton_env_%RANDOM%_%RANDOM%.tmp"
set "LOG_FILE=%APP_DIR%\install.log"

set "MYSQL_VERSION=8.0.36"
set "MYSQL_DIR=C:\mysql_lite"
set "MYSQL_BIN=%MYSQL_DIR%\bin"
set "MYSQL_URL=https://dev.mysql.com/get/Downloads/MySQL-8.0/mysql-%MYSQL_VERSION%-winx64.zip"

echo. > "%LOG_FILE%"
call :log "=============================="
call :log "MicroFlyton Install - %DATE% %TIME%"
call :log "APP_DIR  = %APP_DIR%"
call :log "ENV_FILE = %ENV_FILE%"
call :log "MYSQL_DIR= %MYSQL_DIR%"
call :log "=============================="

rem ----------------------------------------------------------------
echo [1/5] Checking Python...
call :log "[1/5] Checking Python"
where python >nul 2>nul
if errorlevel 1 (
  call :log "FAIL: python not found in PATH"
  echo ERROR: python was not found in PATH.
  echo Install Python 3.11+ and rerun this script.
  exit /b 1
)
for /f "tokens=*" %%V in ('python --version 2^>^&1') do call :log "  python = %%V"

rem ----------------------------------------------------------------
echo [2/5] Validating environment file...
call :log "[2/5] Validating env file: %ENV_FILE%"
if not exist "%ENV_FILE%" (
  call :log "FAIL: env file not found"
  echo ERROR: %ENV_FILE% was not found.
  exit /b 1
)
call :log "  env file OK"

rem ----------------------------------------------------------------
echo [3/6] Installing Microsoft VC++ Runtime...
call :log "[3/6] Installing Microsoft VC++ Runtime"

curl -L -o "%TEMP%\vc_redist.x64.exe" "https://aka.ms/vc14/vc_redist.x64.exe" 2>&1
if errorlevel 1 (
  call :log "FAIL: VC++ runtime download failed"
  echo ERROR: Could not download Microsoft VC++ Runtime.
  exit /b 1
)

"%TEMP%\vc_redist.x64.exe" /install /quiet /norestart 2>&1
if errorlevel 1 (
  call :log "FAIL: VC++ runtime install failed"
  echo ERROR: Microsoft VC++ Runtime installation failed.
  exit /b 1
)

call :log " VC++ runtime installed OK"

rem ----------------------------------------------------------------
echo [4/6] Installing MySQL...
call :log "[4/6] MySQL install"

if exist "%MYSQL_BIN%\mysqld.exe" (
  call :log "  mysqld.exe exists - skipping download"
  echo   MySQL binaries already at %MYSQL_DIR%
  goto mysql_service
)

call :log "  mysqld.exe not found - downloading"
if not exist "%MYSQL_DIR%" mkdir "%MYSQL_DIR%"
cd /d "%MYSQL_DIR%"

echo   Downloading MySQL v%MYSQL_VERSION%...
call :log "  curl -> %MYSQL_URL%"
curl -L -o mysql.zip "%MYSQL_URL%" 2>&1
if errorlevel 1 (
  call :log "FAIL: curl download failed"
  echo ERROR: Download failed. Check internet connection.
  exit /b 1
)
call :log "  download OK"

echo   Extracting...
tar -xf mysql.zip --strip-components=1
if errorlevel 1 (
  call :log "FAIL: tar extract failed"
  echo ERROR: Extract failed.
  exit /b 1
)
del mysql.zip
call :log "  extract OK"

echo   Creating my.ini...
(
  echo [mysqld]
  echo basedir=%MYSQL_DIR:\=/%
  echo datadir=%MYSQL_DIR:\=/%/data
  echo port=3306
  echo innodb_buffer_pool_size=128M
  echo max_connections=10
) > "%MYSQL_DIR%\my.ini"
call :log "  my.ini written"

echo   Clearing old data directory for fresh initialize...
call :log "  removing old data dir"
if exist "%MYSQL_DIR%\data" rmdir /s /q "%MYSQL_DIR%\data"

echo   Initializing data directory...
call :log "  running mysqld --initialize-insecure"
"%MYSQL_BIN%\mysqld.exe" --defaults-file="%MYSQL_DIR%\my.ini" --initialize-insecure --console 2>&1
if errorlevel 1 (
  call :log "FAIL: initialize-insecure failed"
  echo ERROR: MySQL initialization failed.
  exit /b 1
)
call :log "  initialize OK"

echo   Registering Windows service...
call :log "  cleaning up any old service registration"
net stop MySQL_Lite >nul 2>nul
"%MYSQL_BIN%\mysqld.exe" --remove MySQL_Lite >nul 2>nul
sc delete MySQL_Lite >nul 2>nul
timeout /t 2 /nobreak >nul

call :log "  mysqld --install MySQL_Lite"
"%MYSQL_BIN%\mysqld.exe" --defaults-file="%MYSQL_DIR%\my.ini" --install MySQL_Lite 2>&1
if errorlevel 1 (
  call :log "FAIL: service install failed"
  echo ERROR: MySQL service registration failed.
  echo   Trying sc create as fallback...
  sc create MySQL_Lite binPath= "\"%MYSQL_BIN%\mysqld.exe\" --defaults-file=\"%MYSQL_DIR%\my.ini\" MySQL_Lite" start= auto DisplayName= "MySQL Lite" 2>&1
  if errorlevel 1 (
    call :log "FAIL: sc create also failed"
    echo ERROR: Could not register MySQL service.
    exit /b 1
  )
)
call :log "  service registered OK"
goto mysql_start

:mysql_service
echo   Checking service registration...
call :log "  sc query MySQL_Lite"
sc query MySQL_Lite >nul 2>nul
if not errorlevel 1 (
  call :log "  service already registered"
  echo   Service already registered.
  goto mysql_start
)

call :log "  service not registered - registering"
echo   Service not registered. Registering...
"%MYSQL_BIN%\mysqld.exe" --defaults-file="%MYSQL_DIR%\my.ini" --install MySQL_Lite 2>&1
if errorlevel 1 (
  call :log "FAIL: service install failed"
  echo ERROR: MySQL service registration failed.
  exit /b 1
)
call :log "  service registered OK"

:mysql_start
echo   Starting MySQL service...
call :log "  net start MySQL_Lite"
net start MySQL_Lite 2>&1
call :log "  net start errorlevel=%errorlevel%"

echo   Waiting for MySQL to be ready...
call :log "  waiting for TCP connection on 127.0.0.1:3306"
set "READY=0"
for /l %%i in (1,1,15) do (
  if "!READY!"=="0" (
    "%MYSQL_BIN%\mysql.exe" -u root --protocol=TCP --host=127.0.0.1 --connect-timeout=2 --execute="SELECT 1;" >nul 2>nul
    if not errorlevel 1 (
      set "READY=1"
      call :log "  MySQL ready on attempt %%i"
    )
    if "!READY!"=="0" (
      echo   attempt %%i/15...
      call :log "  attempt %%i/15 - not ready"
      timeout /t 2 /nobreak >nul
    )
  )
)
if "!READY!"=="0" (
  call :log "FAIL: MySQL not ready after 30s"
  echo.
  echo ERROR: MySQL did not respond after 30 seconds.
  echo.
  echo --- Service state ---
  sc query MySQL_Lite
  echo.
  echo --- MySQL error log ---
  for %%F in ("%MYSQL_DIR%\data\*.err") do (
    echo Log: %%F
    type "%%F"
  )
  echo.
  echo Full install log: %LOG_FILE%
  exit /b 1
)

rem ----------------------------------------------------------------
echo [5/6] Creating required directories...
call :log "[5/6] creating directories"
if not exist "%APP_DIR%\client\pages\im" mkdir "%APP_DIR%\client\pages\im"
call :log "  client/pages/im OK"

rem ----------------------------------------------------------------
echo [6/6] Installing mysql-connector-python...
call :log "[6/6] pip install mysql-connector-python"
python -m pip install mysql-connector-python 2>&1
if errorlevel 1 (
  call :log "FAIL: pip install mysql-connector-python failed"
  echo ERROR: Could not install mysql-connector-python.
  exit /b 1
)
call :log "  mysql-connector-python OK"

echo [6/6] Initializing database and tables...
call :log "[6/6] init_tables.sql"
"%MYSQL_BIN%\mysql.exe" -u root --protocol=TCP --host=127.0.0.1 < "%SCRIPT_DIR%init_tables.sql" 2>&1
if errorlevel 1 (
  call :log "FAIL: init_tables.sql failed"
  echo ERROR: Database initialization failed.
  exit /b 1
)
call :log "  tables OK"

rem ----------------------------------------------------------------
echo [6/6] Updating .env.micro for MySQL...
call :log "[5/5] updating .env.micro"
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
  call :log "FAIL: .env.micro update failed"
  echo WARNING: Could not update .env.micro
  exit /b 1
)
call :log "  .env.micro updated"

where git >nul 2>nul
if not errorlevel 1 (
  git -C "%APP_DIR%" rev-parse --is-inside-work-tree >nul 2>nul
  if not errorlevel 1 (
    git -C "%APP_DIR%" update-index --skip-worktree ".env.micro" >nul 2>nul
  )
)

call :log "=============================="
call :log "Installation completed OK"
call :log "=============================="
echo.
echo Installation completed.
echo Code path : %APP_DIR%
echo MySQL     : %MYSQL_DIR%
echo Database  : fly  /  user: fly  /  password: 1964
echo Log       : %LOG_FILE%
exit /b 0

rem ----------------------------------------------------------------
:log
echo [%TIME%] %~1 >> "%LOG_FILE%"
exit /b 0
