# MicroFlyton Architecture Map

## Core runtime
- `server/server.py` = process entry point, loads `.env.micro`, starts HTTP server, opens browser
- `server/runtime/windows_http.py` = Python HTTP server (replaces Apache), routes GET/POST to static files or CGI handlers
- `server/runtime/cgi_bridge.py` = loads CGI endpoint modules via importlib and forwards requests
- `server/runtime/pathmap.py` = maps URL paths to static folders or CGI endpoints
- `server/runtime/cgi_env.py` = request context helper for CGI-style metadata

## Flyton-compatible execution
- `server/flyton_core.py` = dynamic app loader and renderer
- `server/cgi-bin/p.py` = Flyton-style page endpoint
- `server/cgi-bin/api.py` = Flyton-style API endpoint (delegates to `apis/cgi.py`)
- `server/cgi-bin/p4web.py` = reserved compatibility endpoint

## API layer
- `server/apis/cgi.py` = method resolver, payload normalization, session enforcement, stdout capture
- `server/apis/api/api_login.py` = login method: validates credentials against `users` table, creates session
- `server/apis/api/api_status.py` = status/ping method
- `server/apis/tools/sql.py` = MySQL access layer (find, insert, count, raw query). Uses `use_pure` flag from `config.sys_fly`
- `server/apis/tools/db_ses.py` = session creation and validation

## Configuration
- `server/config.py` = MySQL credentials, `sys_fly` flag (1 = MicroFlyton, uses pure Python MySQL driver), `sys_mode`, `sys_root`
- `.env.micro` = runtime overrides: HOST, PORT, APP_NAME, AUTO_OPEN_BROWSER, START_URL

## Client side
- `client/pages/` = browser entry HTML pages
- `client/lib/` = client-side libraries (Bootstrap, kicdev.server.js, kicdev.bs5.js)
- `client/app/` = server-rendered apps loaded through `p.py`
- `client/app/admin/` = reserved admin app area

## Scripts (Windows)
- `scripts/run_microflyton.bat` = start the server
- `scripts/install_microflyton.bat` = local install validation and folder prep
- `scripts/register_startup.bat` = register as Windows startup item
- `scripts/kic.bat` = operator console
- `scripts/cleanup_uninstall.bat` = removal flow
- `scripts/sqlite_shell.py` = SQLite shell utility
- `scripts/init_tables.py` = database table initializer
