# MicroFlyton (Windows)

## Prerequisites

Install Git:
winget install --id Git.Git -e --source winget

Install Python:
winget install --id Python.Python.3.11 -e --source winget

## 1. Setup (Clone + Install)

cd C:\
git clone https://github.com/yaweli/microFlyton.git microflyton
cd C:\microflyton
.\scripts\install_microflyton.bat

## 2. Run MicroFlyton

C:\microflyton\scripts\run_microflyton.bat

This will:
- start the local server
- open MicroFlyton automatically in the browser

## 3. Enable Startup Launch

C:\microflyton\scripts\register_startup.bat

This will:
- start MicroFlyton automatically when Windows starts
- open it automatically in the browser

## 4. Uninstall

C:\microflyton\scripts\cleanup_uninstall.bat

## 5. sql

C:\microflyton\scripts\kic.bat

## Access

http://127.0.0.1:8080/Client/pages/index.html

Login:
- username: admin
- password: fly123
