# MicroFlyton (Windows)

## Clean architecture mapping
- `server/server.py` = start / boot / orchestrate
- `server/runtime/windows_http.py` = Python HTTP host and Apache replacement layer
- `server/runtime/cgi_bridge.py` = CGI endpoint loader and dispatcher
- `server/runtime/pathmap.py` = static route and CGI route mapping
- `server/runtime/cgi_env.py` = CGI-style request metadata helper
- `server/flyton_core.py` = app / page dispatcher
- `server/cgi-bin/p.py` = Flyton-style page endpoint
- `server/cgi-bin/api.py` = Flyton-style API endpoint
- `server/cgi-bin/p4web.py` = Flyton compatibility page endpoint
- `server/apis/cgi.py` = API dispatcher and session gate
- `server/apis/api/*.py` = API method logic
- `server/apis/tools/sql.py` = SQLite access, sessions, and logs
- `client/pages/` = browser entry pages
- `client/lib/` = browser helper assets
- `client/app/` = dynamic apps rendered through `p.py`
- `.env.micro` = runtime configuration
- `scripts/*.bat` = Windows operator scripts

## Paths
- Code: `C:\microflyton`
- Database: `C:\sqlite_microflyton\microflyton.db`

## Install
Run from Command Prompt:

```bat
cd C:\microflyton\scripts
kic.bat
```

Run from PowerShell:

```powershell
cd C:\microflyton\scripts
.\kic.bat
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
