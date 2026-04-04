
## First time Install
Run from Command Prompt:

```bat
cd C:\
winget install --id Git.Git -e --source winget
git clone https://github.com/yaweli/microFlyton.git
cd C:\microflyton\scripts
.\kic.bat
```


in case you have git , this message will apear: (ignore and continue):
```bat
Found an existing package already installed. Trying to upgrade the installed package...
No available upgrade found.
No newer package versions are available from the configured sources.
```


Then use:
- `install`
- `run`

## KIC commands
- `sql`
- `install`
- `run`
- `register`
- `delete`
- `pull`

## Notes
- `install` moves runtime data to `C:\sqlite_microflyton`.
- `delete` removes the code folder and startup registration.
- `delete` preserves the external database.
- `delete` closes the KIC console so Windows can release the folder before removal.
- `pull` uses `git pull --ff-only` and then re-runs install.
- runtime data stays outside the repo to protect it during updates.

## Access
- `http://127.0.0.1:8080/pages/index.html`
- `http://127.0.0.1:8080/Client/pages/index.html`
- `http://127.0.0.1:8080/cgi-bin/p?app=start&ses=...`

## Login
- username: `admin`
- password: `fly123`
