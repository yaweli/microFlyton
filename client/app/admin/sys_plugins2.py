import json, random, string, urllib.request, urllib.error
from pathlib import Path as _Path
from pathlib import Path
from tools.sql import *
from tools.db_plugins import *

_lib = Path(__file__).resolve().parent.parent.parent / "lib"


def _load_catalog():
    try:
        raw = (_lib / "flyton_plugins.json").read_text(encoding="utf-8")
        return {p["code"]: p for p in json.loads(raw).get("p", [])}
    except Exception:
        return {}


def _rand_char():
    return random.choice(string.ascii_letters)


def _encode_password(pw, skip):
    result = ""
    for ch in pw:
        result += ch
        for _ in range(skip - 1):
            result += _rand_char()
    extra = random.randint(9, 15)
    for _ in range(extra):
        result += _rand_char()
    return result


def _build_plp(pw, pcode):
    skip         = random.randint(1, 9)
    total_digits = random.randint(6, 11)
    middle_count = total_digits - 3
    middle       = "".join(str(random.randint(0, 9)) for _ in range(middle_count))
    num          = f"{len(pw):02d}{middle}{skip}"
    encoded_pw   = _encode_password(pw, skip)
    return f"{num}/{pcode}/{encoded_pw}"


def _call_verify(plp):
    url = f"https://x.yaw.red/cgi-bin/micro_f_plugin?PlP={plp}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "MicroFlyton/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        return {"err": str(e)}


def _wget(url):
    filename = "/tmp/" + url.split("/")[-1]
    try:
        urllib.request.urlretrieve(url, filename)
        if not _Path(filename).exists() or _Path(filename).stat().st_size == 0:
            return filename, "file empty or missing after download"
        return filename, ""
    except urllib.error.HTTPError as e:
        return filename, f"HTTP {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return filename, f"URL error: {e.reason}"
    except Exception as e:
        return filename, str(e)


def sys_plugins2(data):
    ses    = data["ses"]
    pcode  = data.get("plugin_code", "").strip()
    redeem = data.get("redeem", "").strip().upper()

    back_catalog = f"/cgi-bin/p?ses={ses}&rpage=sys_plugins1"
    back_plugins = f"/cgi-bin/p?ses={ses}&rpage=sys_plugins"

    catalog = _load_catalog()
    entry   = catalog.get(pcode)
    if not entry:
        return _result(ses, 0, "Unknown plugin.", back_catalog)

    pname = entry.get("name", pcode)
    state = entry.get("state", "public")

    if state == "public":
        pw = "eli"
    else:
        if len(redeem) <= 2:
            return _result(ses, 0, "Invalid redeem code.", back_catalog)
        pw = redeem[2:]

    plp  = _build_plp(pw, pcode)
    resp = _call_verify(plp)

    if "err" in resp:
        return _result(ses, 0, str(resp["err"]), back_catalog)

    if resp.get("pas1") != "OK":
        return _result(ses, 0, "Verification failed.", back_catalog)

    plugin_url = resp.get("url", "")

    r = plugin_add(pcode)
    if not r.get("status"):
        err = r.get("err", "Install failed")
        return _result(ses, 0, err, back_catalog)

    zip_file = ""
    if plugin_url:
        w = find_in_sql({'table': 'plugins', 'fld': 'plugin_code', 'val': pcode, 'what': 'id'})
        if w:
            add_to_data("plugins", w[0], "url", plugin_url)
        zip_file, err = _wget(plugin_url)
        if err:
            return _result(ses, 0, f"Plugin verified but download failed.<br><small class='text-muted'>{err}</small>", back_catalog)

    return _result(ses, 1, f"Plugin <b>{pname}</b> installed successfully.<br><small class='text-muted'>{zip_file}</small>", back_plugins)


def _result(ses, ok, msg, back_url):
    icon  = "&#9989;"  if ok else "&#10060;"
    color = "success"  if ok else "danger"
    h = f"""
    <div class="col-12 px-4 pt-5 d-flex justify-content-center">
        <div class="mf-info-card" style="max-width:480px;width:100%">
            <div class="mf-info-card-title">&#129070; Plugin Install</div>
            <div class="p-4 text-center">
                <div style="font-size:3rem">{icon}</div>
                <div class="mt-3 text-{color}">{msg}</div>
                <a href="{back_url}" class="btn btn-outline-secondary btn-sm mt-4">&#8592; Back</a>
            </div>
        </div>
    </div>
    """
    return h
