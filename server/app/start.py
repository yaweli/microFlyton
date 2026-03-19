from __future__ import annotations
import html

from config import APP_NAME, CLIENT_ROOT, MACHINE_ID
from db import get_session, latest_logs


def main(ctx: dict) -> str:
    ses = ctx.get("ses", "")
    session = get_session(ses) if ses else None
    username = session["username"] if session else "guest"
    rows = latest_logs(10)
    table_rows = "".join(
        f"<tr><td>{html.escape(r['created_at'])}</td><td>{html.escape(r['level'])}</td><td>{html.escape(r['event_type'])}</td><td>{html.escape(r['event_source'])}</td><td>{html.escape(r['message'])}</td></tr>"
        for r in rows
    ) or "<tr><td colspan='5'>No logs yet</td></tr>"

    return f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>{html.escape(APP_NAME)}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; }}
    .card {{ border: 1px solid #ddd; padding: 16px; border-radius: 8px; margin-bottom: 16px; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; font-size: 14px; }}
    th {{ background: #f5f5f5; }}
    code {{ background: #f6f6f6; padding: 2px 6px; border-radius: 4px; }}
  </style>
</head>
<body>
  <h1>{html.escape(APP_NAME)}</h1>
  <div class="card">
    <p><strong>User:</strong> {html.escape(username)}</p>
    <p><strong>Machine ID:</strong> {html.escape(MACHINE_ID)}</p>
    <p><strong>Server folder:</strong> <code>Server/</code></p>
    <p><strong>Client folder:</strong> <code>Client/</code></p>
    <p><a href="/pages/index.html">Client pages</a> | <a href="/pages/login_index.html">Login page</a></p>
  </div>
  <div class="card">
    <h2>Recent Logs</h2>
    <table>
      <thead><tr><th>Time</th><th>Level</th><th>Type</th><th>Source</th><th>Message</th></tr></thead>
      <tbody>{table_rows}</tbody>
    </table>
  </div>
</body>
</html>
"""
