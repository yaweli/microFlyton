# MicroFlyton (Windows)

Micro Flyton is a thin version of Flyton

Where MicroFlyton is thin and run on a Windows stations The flyton project is a aserver based Software programming Methodology based on Python and an easy style of writing code.


# References

MicroFlyton : https://github.com/yaweli/microFlyton

Flyton : https://github.com/yaweli/flyton


## Prerequisites

Install Git:
winget install --id Git.Git -e --source winget

Install Python:
winget install --id Python.Python.3.11 -e --source winget

Install SQLite:
winget install SQLite.SQLite -e --source winget

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
