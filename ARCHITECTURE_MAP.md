# MicroFlyton Architecture Map

## Core runtime
- `server/server.py` = process entry point, boot, DB init, server start
- `server/runtime/windows_http.py` = Python HTTP host, the Apache replacement layer
- `server/runtime/cgi_bridge.py` = loads CGI endpoint modules and forwards requests
- `server/runtime/pathmap.py` = static and CGI route mapping
- `server/runtime/cgi_env.py` = request context helper for CGI-style metadata

## Flyton-compatible execution
- `server/flyton_core.py` = dynamic app loader and renderer
- `server/cgi-bin/p.py` = Flyton-style page endpoint
- `server/cgi-bin/api.py` = Flyton-style API endpoint
- `server/cgi-bin/p4web.py` = reserved compatibility endpoint

## API layer
- `server/apis/cgi.py` = method resolver, payload normalization, session enforcement
- `server/apis/api/*.py` = concrete API methods like login and status
- `server/apis/tools/sql.py` = SQLite access, users, sessions, logs

## Client side
- `client/pages/` = browser entry HTML pages
- `client/lib/` = client-side support libraries and styles
- `client/app/` = server-rendered apps loaded through `p.py`
- `client/app/admin/` = reserved admin app area

## Configuration and operations
- `.env.micro` = project runtime config
- `scripts/install_microflyton.bat` = local install validation and folder prep
- `scripts/run_microflyton.bat` = Windows start command
- `scripts/register_startup.bat` = startup registration
- `scripts/kic.bat` = operator console
- `scripts/cleanup_uninstall.bat` = removal flow

## Data
- `server/data/` = SQLite DB location
- `server/logs/` = runtime log location
