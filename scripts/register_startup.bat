@echo off
set STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
copy C:\microflyton\scripts\run_microflyton.bat "%STARTUP%"
echo Startup registered.
