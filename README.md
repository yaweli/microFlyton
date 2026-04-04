
## First time Install
Run from Command Prompt:

```bat
cd C:\
winget install --id Git.Git -e --source winget
git clone https://github.com/yaweli/microFlyton.git
cd C:\microflyton\scripts
.\kic.bat
```


In case you already have git , this message will apear: (ignore and continue):
```bat
Found an existing package already installed. Trying to upgrade the installed package...
No available upgrade found.
No newer package versions are available from the configured sources.
```




if this is not the first time , you will need to update , (or delete + install) , what for this error after thr git clone : 
```bat
fatal: destination path 'microFlyton' already exists and is not an empty directory.
```


## If all go well 


The "kic" script will show a menu : 
```bat
==================================
KIC Console
Project: C:\microFlyton
Database: C:\sqlite_microflyton\microflyton.db
Version: 2026.03.30
==================================

Commands:
s  - sql      - Open SQLite terminal
I  - install  - Prepare folders and DB path
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

## KIC commands
- `sql` - enter into our sql as cli 
- `run` - run the service on a cmd terminal 
- `register` - next reboot the service will run auto
- `install` moves runtime data to `C:\sqlite_microflyton`.
- `delete` removes the code folder and startup registration.
-          preserves the external database.
-          closes the KIC console so Windows can release the folder before removal.
- `pull` uses `git pull --ff-only` and then re-runs install.
- runtime data stays outside the repo to protect it during updates.

## Access
- `http://127.0.0.1:8080/pages/index.html`

## Login
- username: `admin`
- password: `fly123`
