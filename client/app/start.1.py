from __future__ import annotations

import html


def main(ctx: dict) -> str:
    ses = html.escape(str(ctx.get("ses", "")))
    return f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>MicroFlyton Home</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; }}
    .row {{ display: flex; gap: 16px; flex-wrap: wrap; }}
    .card {{ border: 1px solid #ddd; padding: 16px; border-radius: 8px; min-width: 260px; max-width: 520px; }}
    pre {{ white-space: pre-wrap; background: #f7f7f7; padding: 12px; border-radius: 8px; }}
    button {{ padding: 8px 12px; }}
  </style>
</head>
<body>
  <h1>MicroFlyton</h1>
  <p>Session: <code>{ses}</code></p>
  <div class="row">
    <div class="card">
      <h3>Status</h3>
      <div id="status">Loading...</div>
      <button onclick="refreshStatus()">Refresh</button>
    </div>
    <div class="card">
      <h3>Architecture</h3>
      <ul>
        <li>client/app is canonical for dynamic pages</li>
        <li>server/cgi-bin preserves Flyton-style entry points</li>
        <li>server/apis/tools/sql.py is the DB access point</li>
        <li>Windows HTTP server is transport only</li>
      </ul>
    </div>
  </div>
  <h3>Recent logs</h3>
  <pre id="logs">Loading...</pre>
<script>
const SES = new URLSearchParams(location.search).get('ses') || '';
async function refreshStatus() {{
  const res = await fetch('/cgi-bin/api?meth=api_status', {{
    method: 'POST',
    headers: {{'Content-Type': 'application/json'}},
    body: JSON.stringify({{ info: {{ os: 'web', ses: SES, uses: '' }}, input: {{}} }})
  }});
  const data = await res.json();
  if (!data.server || data.server.allow !== 1) {{
    document.getElementById('status').innerText = (data.server && (data.server.msg || data.server.err)) || 'Invalid session';
    document.getElementById('logs').innerText = '';
    return;
  }}
  document.getElementById('status').innerText = 'Hello ' + (data.user.first_name || data.user.username || 'user');
  document.getElementById('logs').innerText = JSON.stringify(data.logs || [], null, 2);
}}
refreshStatus();
</script>
</body>
</html>
"""
