import json, random, string, urllib.request, urllib.error, zipfile, ssl, html
from pathlib      import Path as _Path
from pathlib      import Path
from tools.sql        import *
from tools.db_plugins import *
from tools.kicutil    import *

_root  = Path(__file__).resolve().parent.parent.parent.parent
_lib   = _root / "client" / "lib"
_tmp   = _root / "tmp"
_debug = 0

def _log(msg):
    if _debug:
        print(msg)


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
    middle_count = total_digits - 4
    prefix       = str(random.randint(0, 9))
    middle       = "".join(str(random.randint(0, 9)) for _ in range(middle_count))
    num          = f"{prefix}{len(pw):02d}{middle}{skip}"
    encoded_pw   = _encode_password(pw, skip)
    return f"{num}/{pcode}/{encoded_pw}"


def _nossl():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode    = ssl.CERT_NONE
    return ctx

def _safe(e):
    return html.escape(str(e))

def _call_verify(plp):
    url = f"https://x.yaw.red/cgi-bin/micro_f_plugin?PlP={plp}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "MicroFlyton/1.0"})
        with urllib.request.urlopen(req, timeout=10, context=_nossl()) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        return {"err": _safe(e)}


def _wget(url):
    _tmp.mkdir(parents=True, exist_ok=True)
    filename = str(_tmp / url.split("/")[-1])
    try:
        opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=_nossl()))
        with opener.open(url, timeout=30) as r, open(filename, "wb") as f:
            f.write(r.read())
        if not _Path(filename).exists() or _Path(filename).stat().st_size == 0:
            return filename, "file empty or missing after download"
        return filename, ""
    except urllib.error.HTTPError as e:
        return filename, f"HTTP {e.code}: {_safe(e.reason)}"
    except urllib.error.URLError as e:
        return filename, f"URL error: {_safe(e.reason)}"
    except Exception as e:
        return filename, _safe(e)


def _unzip(zip_path):
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(_root)
        return ""
    except Exception as e:
        return _safe(e)


def sys_plugins2(data):
    ses    = data["ses"]
    pcode  = data.get("plugin_code", "").strip()
    redeem = data.get("redeem", "").strip().upper()

    _log(f"[install] START plugin_code={pcode!r} ses={ses!r}")

    back_catalog = "sys_plugins1"
    back_plugins = "sys_plugins"

    catalog = _load_catalog()
    _log(f"[install] catalog loaded, {len(catalog)} entries, pcode found={pcode in catalog}")

    entry   = catalog.get(pcode)
    if not entry:
        _log(f"[install] ABORT unknown plugin {pcode!r}")
        return _result(ses, 0, "Unknown plugin.", back_catalog)

    pname = entry.get("name", pcode)
    state = entry.get("state", "public")
    _log(f"[install] plugin name={pname!r} state={state!r}")

    if state == "public":
        pw = "eli"
    else:
        if len(redeem) <= 2:
            _log(f"[install] ABORT invalid redeem code len={len(redeem)}")
            return _result(ses, 0, "Invalid redeem code. Please check your code.", back_catalog)
        pw = redeem[2:]

    plp  = _build_plp(pw, pcode)
    _log(f"[install] calling verify server ... plp = {plp}")

    resp = _call_verify(plp)
    _log(f"[install] verify response={resp}")

    check_code = " Please check your code." if state != "public" else ""

    if "err" in resp:
        _log(f"[install] ABORT verify error: {resp['err']}")
        return _result(ses, 0, f"{resp['err']}{check_code}", back_catalog)

    if resp.get("pas1") != "OK":
        _log(f"[install] ABORT pas1={resp.get('pas1')!r}")
        return _result(ses, 0, f"Verification failed.{check_code}", back_catalog)

    plugin_url = resp.get("url", "")
    _log(f"[install] verified OK, plugin_url={plugin_url!r}")

    r = plugin_add(pcode)
    _log(f"[install] plugin_add result={r}")
    if not r.get("status"):
        err = r.get("err", "Install failed")
        _log(f"[install] ABORT plugin_add failed: {err}")
        return _result(ses, 0, err, back_catalog)

    zip_file = ""
    if plugin_url:
        w = find_in_sql({'table': 'plugins', 'fld': 'plugin_code', 'val': pcode, 'what': 'id'})
        _log(f"[install] db row for plugin: {w}")
        if w:
            add_to_data("plugins", w[0], "url", plugin_url)

        _log(f"[install] downloading {plugin_url!r} ...")
        zip_file, err = _wget(plugin_url)
        _log(f"[install] download done zip_file={zip_file!r} err={err!r}")
        if err:
            return _result(ses, 0, f"Download failed: {err}", back_catalog)

        _log(f"[install] unzipping {zip_file!r} into {_root} ...")
        err = _unzip(zip_file)
        _log(f"[install] unzip done err={err!r}")
        if err:
            return _result(ses, 0, f"Unzip failed: {err}", back_catalog)
    else:
        _log(f"[install] no plugin_url, skipping download")

    singlerun = _root / "client" / "app" / "admin" / "plugins_singlerun.py"
    _log(f"[install] singlerun path={singlerun}  exists={singlerun.exists()}")
    if singlerun.exists():
        try:
            import importlib.util as _ilu
            spec = _ilu.spec_from_file_location("plugins_singlerun", singlerun)
            mod  = _ilu.module_from_spec(spec)
            spec.loader.exec_module(mod)
            _log(f"[install] singlerun loaded, calling run() ...")
            mod.run()
            _log(f"[install] singlerun run() OK")
        except Exception as e:
            _log(f"[install] ABORT singlerun ERROR: {e}")
            singlerun.unlink(missing_ok=True)
            return _result(ses, 0, f"Plugin setup failed: {_safe(e)}", back_catalog)
        singlerun.unlink(missing_ok=True)
        _log(f"[install] singlerun file deleted")

    _log(f"[install] SUCCESS {pname!r}")
    return _result(ses, 1, f"Plugin <b>{pname}</b> installed successfully.", back_plugins)


def _result(ses, ok, msg, back_page):
    icon  = "&#9989;"  if ok else "&#10060;"
    color = "success"  if ok else "danger"
    h = f"""
    <div class="col-12 px-4 pt-5 d-flex justify-content-center">
        <div class="mf-info-card" style="max-width:480px;width:100%">
            <div class="mf-info-card-title">&#129070; Plugin Install</div>
            <div class="p-4 text-center">
                <div style="font-size:3rem">{icon}</div>
                <div class="mt-3 text-{color}">{msg}</div>
                {kicbutton(back_page, ses, "&#8592; Back", "btn btn-outline-secondary btn-sm mt-4")}
            </div>
        </div>
    </div>
    """
    return h
