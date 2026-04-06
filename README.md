
# microFlyton

microFlyton is a lightweight, self-contained edition of the [Flyton](https://github.com/yaweli/flyton) project — built to run a full Flyton service on a single Windows machine with minimal setup. It includes the core runtime, connects to a local MySQL database, and provides a simple KIC console for managing the service. If you want the full-featured, production-grade version, see the main Flyton project.

**Full Flyton project:** https://github.com/yaweli/flyton

---

## Requirements
- Windows
- Python 3.10+
- MySQL server running locally
- `mysql-connector-python` package (`pip install mysql-connector-python`)

---

## First time Install
Run from Command Prompt:

```bat
cd C:\
winget install --id Git.Git -e --source winget
git clone https://github.com/yaweli/microFlyton.git
cd C:\microflyton\scripts
.\kic.bat
```

If you already have git this message will appear — ignore it and continue:
```bat
Found an existing package already installed. Trying to upgrade the installed package...
No available upgrade found.
No newer package versions are available from the configured sources.
```

If this is not the first time, you will need to update (or delete + re-install). Watch for this error after `git clone`:
```bat
fatal: destination path 'microFlyton' already exists and is not an empty directory.
```

---

## Configuration
Edit `server/config.py` before running:

```python
sys_fly  = 1          # 1 = MicroFlyton (enables pure Python MySQL driver)
sys_mode = "dev"      # "dev" or "prod"
hostname = "localhost"
username = "fly"
password = "your_password"
database = "fly"
```

Runtime overrides (HOST, PORT, APP_NAME, etc.) can be set in `.env.micro`.

---

## If all goes well

The `kic` script will show a menu:
```bat
==================================
KIC Console
Project: C:\microFlyton
Version: 2026.03.30
==================================

Commands:
I  - install  - Prepare folders
R  - run      - Run MicroFlyton service
U  - pull     - Pull latest code from GitHub safely
RG - register - Register MicroFlyton in Windows startup
delete - Delete and uninstall MicroFlyton code

Press Enter on empty command to exit.

Enter command:
```

Then use:
- `install`
- `run`

---

## KIC commands
- `run` — start the service in a cmd terminal
- `register` — auto-start the service on next reboot
- `install` — prepare runtime folders
- `delete` — removes the code folder and startup registration (preserves the database)
- `pull` — runs `git pull --ff-only` then re-runs install

---

## Access
- `http://127.0.0.1:8080/pages/index.html`

## Login
- username: `kic`
- password: `fly123`
