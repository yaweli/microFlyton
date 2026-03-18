# MicroFlyton (Windows)

## Prerequisite

winget install --id Git.Git -e --source winget
winget install --id Python.Python.3.11 -e --source winget

## 1. Setup (Clone + Install)

cd C:\
git clone https://github.com/yaweli/microFlyton.git microflyton
cd C:\microflyton
.\scripts\install_microflyton.bat

## 2. Run MicroFlyton

C:\microflyton\scripts\run_microflyton.bat

## 3. Enable Startup Launch

C:\microflyton\scripts\register_startup.bat

## 4. Uninstall

C:\microflyton\scripts\cleanup_uninstall.bat

## Access

http://127.0.0.1:8080/pages/index.html

Login:
- username: admin
- password: fly123
