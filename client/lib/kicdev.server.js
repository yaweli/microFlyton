async function call_server(meth, input) {
  const ses = sessionStorage.getItem('ses') || '';
  const uses = sessionStorage.getItem('uses') || '';
  const payload = {
    info: { os: 'web', ses, uses },
    input: input || {}
  };
  const res = await fetch('/cgi-bin/api?meth=' + encodeURIComponent(meth), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  const data = await res.json();
  if (data && data.server && data.server.sact === 'out') {
    sessionStorage.removeItem('ses');
  }
  return data;
}
