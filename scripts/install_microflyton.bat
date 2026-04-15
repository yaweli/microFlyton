@echo off
setlocal EnableExtensions EnableDelayedExpansion

net session >nul 2>nul
if errorlevel 1 (
  echo ERROR: This script must be run as Administrator.
  echo Right-click the script and choose "Run as administrator".
  pause
  exit /b 1
)

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "APP_DIR=%%~fI"

set "ENV_FILE=%APP_DIR%\.env.micro"
set "LOG_FILE=%APP_DIR%\install.log"
set "MYSQL_VERSION=8.0.36"
set "MYSQL_DIR=C:\mysql_lite"
set "MYSQL_BIN=%MYSQL_DIR%\bin"
set "MYSQL_URL=https://dev.mysql.com/get/Downloads/MySQL-8.0/mysql-%MYSQL_VERSION%-winx64.zip"
set "VC_URL=https://aka.ms/vc14/vc_redist.x64.exe"

set "PY_CMD="
set "PIP_CMD="

> "%LOG_FILE%" (
  echo ==============================
  echo MicroFlyton Install - %DATE% %TIME%
  echo APP_DIR  = %APP_DIR%
  echo ENV_FILE = %ENV_FILE%
  echo MYSQL_DIR= %MYSQL_DIR%
  echo ==============================
)

call :step "[1/9] Validating environment file..."
if not exist "%ENV_FILE%" (
  call :fail "Environment file not found: %ENV_FILE%"
)
call :log "Environment file exists"

call :step "[2/9] Resolving Python..."
call :resolve_python
if errorlevel 1 (
  call :step "[2/9] Python not usable - installing Python 3.11..."
  call :install_python
  if errorlevel 1 (
    call :fail "Python installation failed"
  )
  call :resolve_python
  if errorlevel 1 (
    call :fail "Python still not usable after install. Disable Microsoft Store python aliases if needed."
  )
)

call :step "[3/9] Ensuring pip is ready..."
call :ensure_pip
if errorlevel 1 (
  call :fail "pip is not available"
)

call :step "[4/9] Installing Python packages..."
call :install_python_packages
if errorlevel 1 (
  call :fail "Could not install required Python packages"
)

call :step "[5/9] Installing Microsoft VC++ Runtime..."
call :install_vc_runtime
if errorlevel 1 (
  call :fail "Could not install Microsoft VC++ Runtime"
)

call :step "[6/9] Installing / starting MySQL..."
call :install_mysql
if errorlevel 1 (
  call :fail "MySQL installation/startup failed"
)

call :step "[7/9] Creating required directories and symlink..."
call :prepare_directories
if errorlevel 1 (
  call :fail "Could not prepare folders or symlink"
)

call :step "[8/9] Initializing database and tables..."
call :init_database
if errorlevel 1 (
  call :fail "Database initialization failed"
)

call :step "[9/9] Updating .env.micro for MySQL..."
call :update_env_file
if errorlevel 1 (
  call :fail "Failed to update .env.micro"
)

where git >nul 2>nul
if not errorlevel 1 (
  git -C "%APP_DIR%" rev-parse --is-inside-work-tree >nul 2>nul
  if not errorlevel 1 (
    git -C "%APP_DIR%" update-index --skip-worktree ".env.micro" >nul 2>nul
    call :log "Marked .env.micro as skip-worktree"
  )
)

call :log "=============================="
call :log "Installation completed OK"
call :log "=============================="

echo.
echo Installation completed successfully.
echo.
echo Code path : %APP_DIR%
echo MySQL     : %MYSQL_DIR%
echo Python    : %PY_CMD%
echo Database  : fly
echo User      : fly
echo Password  : 1964
echo Log       : %LOG_FILE%
echo.
exit /b 0

:resolve_python
set "PY_CMD="
set "PIP_CMD="

python --version >nul 2>nul
if not errorlevel 1 (
  set "PY_CMD=python"
  set "PIP_CMD=python -m pip"
  for /f "tokens=*" %%V in ('python --version 2^>^&1') do call :log "Using python: %%V"
  exit /b 0
)

py -3.11 --version >nul 2>nul
if not errorlevel 1 (
  set "PY_CMD=py -3.11"
  set "PIP_CMD=py -3.11 -m pip"
  for /f "tokens=*" %%V in ('py -3.11 --version 2^>^&1') do call :log "Using python: %%V"
  exit /b 0
)

py -3 --version >nul 2>nul
if not errorlevel 1 (
  set "PY_CMD=py -3"
  set "PIP_CMD=py -3 -m pip"
  for /f "tokens=*" %%V in ('py -3 --version 2^>^&1') do call :log "Using python: %%V"
  exit /b 0
)

call :log "No usable Python found"
exit /b 1

:install_python
call :log "Attempting Python install via winget"

where winget >nul 2>nul
if errorlevel 1 (
  call :log "winget not found"
  echo ERROR: winget was not found on this machine.
  echo Install Python 3.11 manually, then rerun this script.
  exit /b 1
)

winget install --id Python.Python.3.11 -e --source winget --accept-package-agreements --accept-source-agreements
if errorlevel 1 (
  call :log "winget install Python failed"
  exit /b 1
)

call :log "Python installed via winget"
exit /b 0

:ensure_pip
%PY_CMD% -m ensurepip --upgrade >nul 2>nul
%PY_CMD% -m pip --version >nul 2>nul
if errorlevel 1 (
  call :log "pip still unavailable after ensurepip"
  exit /b 1
)

%PY_CMD% -m pip install --upgrade pip
if errorlevel 1 (
  call :log "pip upgrade failed"
  exit /b 1
)

for /f "tokens=*" %%V in ('%PY_CMD% -m pip --version 2^>^&1') do call :log "Using pip: %%V"
exit /b 0

:install_python_packages
%PY_CMD% -m pip install mysql-connector-python requests
if errorlevel 1 (
  call :log "pip install mysql-connector-python requests failed"
  exit /b 1
)
call :log "Python packages installed: mysql-connector-python, requests"
exit /b 0

:install_vc_runtime
curl -L -o "%TEMP%\vc_redist.x64.exe" "%VC_URL%"
if errorlevel 1 (
  call :log "VC++ runtime download failed"
  exit /b 1
)

"%TEMP%\vc_redist.x64.exe" /install /quiet /norestart
if errorlevel 1 (
  call :log "VC++ runtime install returned error"
  exit /b 1
)

call :log "VC++ runtime installed"
exit /b 0

:install_mysql
if exist "%MYSQL_BIN%\mysqld.exe" (
  call :log "MySQL binaries already exist at %MYSQL_DIR%"
  goto mysql_service_check
)

if not exist "%MYSQL_DIR%" mkdir "%MYSQL_DIR%"
cd /d "%MYSQL_DIR%"

call :log "Downloading MySQL from %MYSQL_URL%"
curl -L -o mysql.zip "%MYSQL_URL%"
if errorlevel 1 (
  call :log "MySQL download failed"
  exit /b 1
)

tar -xf mysql.zip --strip-components=1
if errorlevel 1 (
  call :log "MySQL extraction failed"
  exit /b 1
)
del /f /q mysql.zip >nul 2>nul

(
  echo [mysqld]
  echo basedir=%MYSQL_DIR:\=/%
  echo datadir=%MYSQL_DIR:\=/%/data
  echo port=3306
  echo innodb_buffer_pool_size=128M
  echo max_connections=25
  echo default_authentication_plugin=mysql_native_password
) > "%MYSQL_DIR%\my.ini"

call :log "my.ini created"

if exist "%MYSQL_DIR%\data" (
  call :log "Removing old MySQL data directory"
  rmdir /s /q "%MYSQL_DIR%\data"
)

call :log "Initializing MySQL data directory"
"%MYSQL_BIN%\mysqld.exe" --defaults-file="%MYSQL_DIR%\my.ini" --initialize-insecure --console
if errorlevel 1 (
  call :log "mysqld --initialize-insecure failed"
  exit /b 1
)

:mysql_service_check
sc query MySQL_Lite >nul 2>nul
if errorlevel 1 (
  call :log "Registering MySQL_Lite service"
  net stop MySQL_Lite >nul 2>nul
  "%MYSQL_BIN%\mysqld.exe" --remove MySQL_Lite >nul 2>nul
  sc delete MySQL_Lite >nul 2>nul
  timeout /t 2 /nobreak >nul

  "%MYSQL_BIN%\mysqld.exe" --defaults-file="%MYSQL_DIR%\my.ini" --install MySQL_Lite
  if errorlevel 1 (
    call :log "mysqld --install failed, trying sc create fallback"
    sc create MySQL_Lite binPath= "\"%MYSQL_BIN%\mysqld.exe\" --defaults-file=\"%MYSQL_DIR%\my.ini\" MySQL_Lite" start= auto DisplayName= "MySQL Lite"
    if errorlevel 1 (
      call :log "MySQL service registration failed"
      exit /b 1
    )
  )
)

call :log "Starting MySQL_Lite service"
net start MySQL_Lite >nul 2>nul

set "READY=0"
for /l %%i in (1,1,20) do (
  if "!READY!"=="0" (
    "%MYSQL_BIN%\mysql.exe" -u root --protocol=TCP --host=127.0.0.1 --connect-timeout=2 --execute="SELECT 1;" >nul 2>nul
    if not errorlevel 1 (
      set "READY=1"
      call :log "MySQL became ready on attempt %%i"
    ) else (
      timeout /t 2 /nobreak >nul
    )
  )
)

if "!READY!"=="0" (
  call :log "MySQL did not become ready in time"
  sc query MySQL_Lite >> "%LOG_FILE%" 2>&1
  for %%F in ("%MYSQL_DIR%\data\*.err") do (
    echo ----- %%F ----- >> "%LOG_FILE%"
    type "%%F" >> "%LOG_FILE%"
  )
  exit /b 1
)

call :log "MySQL is ready"
exit /b 0

:prepare_directories
if not exist "%APP_DIR%\client\pages\im" mkdir "%APP_DIR%\client\pages\im"
if not exist "%APP_DIR%\client\app" mkdir "%APP_DIR%\client\app"

if exist "%APP_DIR%\client\app\tools" (
  call :log "Symlink or folder already exists: client\app\tools"
  exit /b 0
)

mklink /D "%APP_DIR%\client\app\tools" "%APP_DIR%\server\apis\tools"
if errorlevel 1 (
  call :log "mklink failed"
  exit /b 1
)

call :log "Directories and symlink prepared"
exit /b 0

:init_database
if not exist "%SCRIPT_DIR%init_tables.sql" (
  call :log "init_tables.sql not found: %SCRIPT_DIR%init_tables.sql"
  exit /b 1
)

"%MYSQL_BIN%\mysql.exe" -u root --protocol=TCP --host=127.0.0.1 < "%SCRIPT_DIR%init_tables.sql"
if errorlevel 1 (
  call :log "init_tables.sql execution failed"
  exit /b 1
)

call :log "Database initialized from init_tables.sql"
exit /b 0

:update_env_file
set "TMP_PY=%TEMP%\microflyton_update_env_%RANDOM%_%RANDOM%.py"

> "%TMP_PY%" (
  echo import sys
  echo from pathlib import Path
  echo env_file = Path^(sys.argv[1]^)
  echo text = env_file.read_text^(encoding="utf-8"^) if env_file.exists^(^) else ""
  echo lines = text.splitlines^(True^)
  echo set_keys = {
  echo     "DB_BACKEND": "mysql",
  echo     "hostname": "127.0.0.1",
  echo     "username": "fly",
  echo     "password": "1964",
  echo     "database": "fly",
  echo     "is_mic": "0",
  echo }
  echo remove_keys = {"DB_PATH"}
  echo result = []
  echo seen = set^(^)
  echo for line in lines:
  echo     s = line.strip^(^)
  echo     if not s or s.startswith^("#"^) or "=" not in s:
  echo         result.append^(line^)
  echo         continue
  echo     k, v = s.split^("="^, 1^)
  echo     k = k.strip^(^)
  echo     if k in remove_keys:
  echo         continue
  echo     if k in set_keys:
  echo         result.append^(f"{k}={set_keys[k]}\n"^)
  echo         seen.add^(k^)
  echo     else:
  echo         result.append^(line^)
  echo for k, v in set_keys.items^(^):
  echo     if k not in seen:
  echo         result.append^(f"{k}={v}\n"^)
  echo env_file.write_text^("".join^(result^), encoding="utf-8"^)
  echo print^("env updated"^)
)

%PY_CMD% "%TMP_PY%" "%ENV_FILE%"
set "ENV_ERR=%errorlevel%"
del /f /q "%TMP_PY%" >nul 2>nul

if not "%ENV_ERR%"=="0" (
  call :log ".env.micro update script failed"
  exit /b 1
)

call :log ".env.micro updated for MySQL"
exit /b 0

:step
echo.
echo %~1
call :log "%~1"
exit /b 0

:fail
call :log "FAIL: %~1"
echo.
echo ERROR: %~1
echo See log: %LOG_FILE%
echo.
pause
exit /b 1

:log
>> "%LOG_FILE%" echo [%DATE% %TIME%] %~1
exit /b 0