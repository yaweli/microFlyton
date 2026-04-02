#
#
# kicdev
# Version 2.14 - ra - sql_sort
#
import os
import sys
import json
import re
from datetime import datetime
import importlib.util
import sqlite3

try:
    import mysql.connector as mysql_connector
except Exception:
    mysql_connector = None

sql_v = 2.14
_env_cache = None


def _server_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _project_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def _strip_quotes(v):
    if v is None:
        return v
    v = str(v).strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in ("'", '"'):
        return v[1:-1]
    return v


def _load_env_map():
    global _env_cache
    if _env_cache is not None:
        return _env_cache

    env = {}
    seen = set()
    candidates = []

    here = os.path.abspath(os.path.dirname(__file__))
    paths = [here]
    cur = here
    for _ in range(6):
        cur = os.path.dirname(cur)
        paths.append(cur)

    paths.append(os.getcwd())
    paths.append(_project_root())
    paths.append(_server_root())

    for base in paths:
        for name in (".env", ".env.micro", ".env.local"):
            p = os.path.join(base, name)
            if os.path.isfile(p) and p not in seen:
                seen.add(p)
                candidates.append(p)

    for path in candidates:
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if line.startswith("export "):
                        line = line[7:].strip()
                    if "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    env[k.strip()] = _strip_quotes(v.strip())
        except Exception:
            pass

    _env_cache = env
    return env


def _env_get(config, key, default=None):
    for k in (key, key.upper(), key.lower()):
        if hasattr(config, k):
            return getattr(config, k)

    env_map = _load_env_map()
    for k in (key, key.upper(), key.lower()):
        if k in env_map:
            return env_map[k]

    for k in (key, key.upper(), key.lower()):
        v = os.getenv(k)
        if v is not None:
            return v

    return default


def _is_mic():
    config = kic_config()
    v = _env_get(config, "is_mic", 0)
    return str(v).strip().lower() in ("1", "true", "yes", "on")


def _resolve_sqlite_path(db_path):
    db_path = _strip_quotes(db_path)
    db_path = os.path.expandvars(os.path.expanduser(str(db_path).strip()))

    if not os.path.isabs(db_path):
        db_path = os.path.abspath(os.path.join(_project_root(), db_path))

    return db_path


def _db_connect():
    config = kic_config()

    if _is_mic():
        db_path = _env_get(config, "DB_PATH")
        if not db_path:
            raise RuntimeError("DB_PATH is missing for SQLite mode")

        db_path = _resolve_sqlite_path(db_path)
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

        return sqlite3.connect(db_path)

    if mysql_connector is None:
        raise RuntimeError("mysql.connector is not installed but is_mic is not enabled")

    host = _env_get(config, "hostname")
    user = _env_get(config, "username")
    password = _env_get(config, "password")
    database = _env_get(config, "database")

    return mysql_connector.connect(
        host=host,
        user=user,
        password=password,
        database=database,
    )


def _ensure_micro_log_table(connection):
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS server_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT,
                event_type TEXT,
                message TEXT,
                details TEXT,
                source TEXT,
                created_at TEXT
            )
            """
        )
        connection.commit()
    finally:
        if cursor:
            cursor.close()


def init_db():
    connection = None
    try:
        connection = _db_connect()
        if _is_mic():
            _ensure_micro_log_table(connection)
        return True
    finally:
        if connection:
            connection.close()


def log_event(level, event_type, message, details=None, source="system"):
    import logging as _logging

    if details is None:
        details = {}

    try:
        log_level = getattr(_logging, str(level).upper(), _logging.INFO)
        _logging.log(
            log_level,
            json.dumps(
                {
                    "event_type": event_type,
                    "message": message,
                    "details": details,
                    "source": source,
                },
                ensure_ascii=False,
                default=str,
            ),
        )
    except Exception:
        pass

    if not _is_mic():
        return {"status": True}

    connection = None
    cursor = None
    try:
        connection = _db_connect()
        _ensure_micro_log_table(connection)
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO server_events
            (level, event_type, message, details, source, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                str(level),
                str(event_type),
                str(message),
                json.dumps(details, ensure_ascii=False, default=str),
                str(source),
                datetime.now().isoformat(timespec="seconds"),
            ),
        )
        connection.commit()
        return {"status": True, "id": cursor.lastrowid}
    except Exception as err:
        return {"status": False, "err": str(err)}
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def _table_name_only(table):
    return table.split()[0].replace("`", "")


def _desc_sqlite(table):
    table_name = _table_name_only(table)
    connection = None
    cursor = None
    try:
        connection = _db_connect()
        cursor = connection.cursor()
        cursor.execute(f"PRAGMA table_info(`{table_name}`)")
        rows = cursor.fetchall()
        ans = []
        for row in rows:
            fld = row[1]
            typ = row[2]
            nulls = "NO" if row[3] else "YES"
            key = "PRI" if row[5] else ""
            default = row[4]
            extra = ""
            ans.append((fld, typ, nulls, key, default, extra))
        return ans
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def _split_set_clause(set_clause):
    parts = []
    cur = []
    in_single = False
    in_double = False
    escape = False

    for ch in set_clause:
        if escape:
            cur.append(ch)
            escape = False
            continue

        if ch == "\\":
            cur.append(ch)
            escape = True
            continue

        if ch == "'" and not in_double:
            in_single = not in_single
            cur.append(ch)
            continue

        if ch == '"' and not in_single:
            in_double = not in_double
            cur.append(ch)
            continue

        if ch == "," and not in_single and not in_double:
            part = "".join(cur).strip()
            if part:
                parts.append(part)
            cur = []
            continue

        cur.append(ch)

    part = "".join(cur).strip()
    if part:
        parts.append(part)

    return parts


def _insert_set_to_sqlite(table, set_clause):
    cols = []
    vals = []

    for part in _split_set_clause(set_clause):
        if "=" not in part:
            continue
        k, v = part.split("=", 1)
        cols.append(f"`{k.strip().strip('`')}`")
        vals.append(v.strip())

    return f"INSERT INTO {table} ({','.join(cols)}) VALUES ({','.join(vals)})"


def _json_field_expr(base, key):
    if _is_mic():
        return f"json_extract({base}, '$.{key}')"
    return f"{base}->>'$.{key}'"


def find_in_sql(r):
    connection = None
    cursor = None

    try:
        connection = _db_connect()
        cursor = connection.cursor()
        c = 0
        table = r["table"]
        tableas = table if " " not in table else table.split(" ")[1]
        q = f"SELECT {sql_what(r['what'])} FROM {table} {sql_join(tableas, r)}"

        where_parts = []

        if "fld" in r:
            fld = r["fld"]
            g = "`"
            if "." in fld or "(" in fld or " " in fld:
                g = ""
            where_parts.append(f"{g}{fld}{g}={kic_geresh(r['val'])}")
            c = c + 1

        if "where" in r:
            q1, c1 = sql_where(r["where"])
            if q1:
                where_parts.append(q1)
                c = c + c1

        if "is_active" in r:
            where_parts.append(f"""is_active={r["is_active"]} """)
            c = c + 1

        if c:
            q += " WHERE " + " AND ".join(where_parts)

        if "grp" in r:
            q += f' GROUP BY {r["grp"]}'
        if "sortj" in r and r["sortj"] != "":
            q += f' ORDER BY {sql_sortj(r["sortj"])}'
        elif "sort" in r:
            q += f' ORDER BY `{r["sort"]}`'
        if "desc" in r:
            q += " DESC"
        if "limit" in r:
            q += f' LIMIT {r["limit"]}'

        if "debug" in r:
            print(f"<br> sql={q} <br>")

        cursor.execute(q)
        results = cursor.fetchall()

        if results == []:
            return False
        if "all" in r:
            return results
        return results[0]

    except Exception as err:
        return {"status": err}
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def insert_to_sql(r):
    connection = None
    cursor = None
    tera_id = -1
    query = ""

    try:
        connection = _db_connect()
        cursor = connection.cursor()
        setdata = ""
        set1 = sql_set(r["set"])

        if "data" in r:
            x = r["data"]
            y = json.dumps(x, ensure_ascii=False)
            z = y.replace("'", "''")
            z = z.replace('ש\\"ח', "שח")
            z = z.replace('\\"', "")
            z = z.replace("\\\\", "/")
            setdata = f",data='{z}'"

        if "id" in r:
            if type(r["id"]) is dict:
                where1, _ = sql_where(r["id"])
                query = f"""UPDATE {r['table']} SET {set1}{setdata} WHERE {where1} """
            else:
                query = f"""UPDATE {r['table']} SET {set1}{setdata} WHERE {sql_var('id', r['id'])} """
            if setdata != "":
                err = "r['data'] support only new records!!! "
                print(err)
                return {"err": err, "status": False}
        else:
            if _is_mic():
                query = _insert_set_to_sqlite(r["table"], f"{set1}{setdata}")
            else:
                query = f"INSERT INTO {r['table']} SET {set1}{setdata}"

        if "debug" in r:
            print(f"<br>sql={query}<br>")

        cursor.execute(query)
        tera_id = cursor.lastrowid
        connection.commit()

    except Exception as err:
        return {"err": err, "status": False, "query": query}
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return {"results": [], "status": True, "ver": sql_v, "id": tera_id}


def count_in_sql(r):
    connection = None
    cursor = None

    try:
        connection = _db_connect()
        cursor = connection.cursor()
        query = f"SELECT COUNT(id) FROM {r['table']} where {r['fld']}={kic_geresh(r['val'])}"
        cursor.execute(query)
        results = cursor.fetchall()

        if results == []:
            return False
        return results[0]

    except Exception as err:
        return {"status": err}
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def gen_data():
    z = find_in_sql({"table": "gen", "fld": "is_active", "val": 1, "what": "*", "all": 1})
    gen = {}
    if not z:
        return gen

    for x in z:
        id = x[0]
        name = x[1]
        gd = x[6] if len(x) > 6 else None
        gen[name] = {"id": id, "val": x[2]}
        if gd is not None and gd:
            gen[name]["data"] = json.loads(gd)

    return gen


def get_data(table, id, fld="id"):
    z = find_in_sql({"table": table, "fld": fld, "val": id, "what": "data"})
    obj = {}
    if type(z) is tuple and z[0] is not None:
        obj = json.loads(z[0])
    return obj


def add_to_data(table, id, fld1, val1=""):
    obj = get_data(table, id)

    if type(fld1) is str:
        if val1 == "!del":
            if fld1 in obj:
                del obj[fld1]
        else:
            obj[fld1] = val1

    if type(fld1) is dict:
        for k in fld1:
            obj[k] = fld1[k]

    sobj = json.dumps(obj, ensure_ascii=False)
    setdata = sql_var("data", sobj)

    res = insert_to_sql({"table": table, "set": setdata, "id": id})
    return res


def get_next_counter(field, type1, data={}):
    gen = gen_data()
    x = gen[f"{type1}_{field}"]
    c = int(x["val"])
    c = c + 1
    t = insert_to_sql({"table": "gen", "set": f"val1={c}", "id": x["id"]})

    if not t["status"]:
        print("problem with sql write")
        return -1

    for k in data:
        r = add_to_data("gen", x["id"], k, data[k])
    return c


def kic_sql(q, elr=0):
    connection = None
    cursor = None

    try:
        qq = q.strip()
        if _is_mic() and qq.lower().startswith("desc "):
            table = qq[5:].strip()
            results = _desc_sqlite(table)
            if elr:
                return {"status": 1, "row_count": len(results), "results": results}
            return results

        connection = _db_connect()
        cursor = connection.cursor()

        cursor.execute(q)
        rc = cursor.rowcount

        try:
            results = cursor.fetchall()
        except Exception:
            results = []

        connection.commit()

        if elr:
            return {"status": 1, "row_count": rc, "results": results}
        return results

    except Exception as err:
        return {"status": err}
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def kic_sql_delete(r):
    if _is_mic():
        q = f'delete from {r["table"]} where id={kic_geresh(r["id"])}'
    else:
        q = f'delete from {r["table"]} where id={kic_geresh(r["id"])} limit 1'
    w = kic_sql(q, 1)
    if w["row_count"] > 0:
        return {"status": 1}
    return {"status": 0, "err": "not deleted"}


def import_state(type1):
    q = f"select count(id),type,count from import where type={kic_geresh(type1)} AND is_active=1 group by count order by count desc limit 1"
    ans = kic_sql(q)
    if len(ans) == 0:
        return {"count": 0, "lines": 0, "updated_at": ""}

    count = ans[0][2]
    lines = ans[0][0]

    z = find_in_sql({"table": "gen", "fld": "key1", "val": type1 + "_import", "what": "updated_at"})

    if z is False:
        return {"count": 0, "lines": 0, "updated_at": ""}

    updated_at = z[0]
    return {"count": count, "lines": lines, "updated_at": updated_at}


def sql_next(r):
    table = r["table"]
    id = 0
    if r["id"]:
        id = r["id"]

    if "is_active" not in r:
        r["is_active"] = 1

    q = f"select * from `{table}` where id>{id}"
    if r["is_active"]:
        q += f""" AND is_active={r["is_active"]} """

    q += " order by id limit 1"

    dict = kic_sql(f"desc `{table}`")

    ans = kic_sql(q)
    if len(ans) == 0:
        return {"id": ""}
    obj = array2obj(ans[0], dict)
    return obj


def sql_order(r):
    table = r["table"]
    id = 0
    if r["id"]:
        id = r["id"]

    if "is_active" not in r:
        r["is_active"] = 1

    q = f"select * from `{table}` where id>{id}"
    q += f""" AND is_active={r["is_active"]} """
    if "where" in r:
        q += f""" AND {r["where"]}"""

    q += " order by id"

    dict = kic_sql(f"desc `{table}`")

    ans = kic_sql(q)

    for x in ans:
        obj = array2obj(x, dict)
        yield obj


def array2obj(ary, dict):
    ans = {}
    for i in range(len(dict)):
        fld = dict[i][0]
        val = ary[i]
        ans[fld] = val
    return ans


cache1 = {}


def dic_of_table(tab):
    global cache1
    if "dict" in cache1:
        if tab in cache1["dict"]:
            return cache1["dict"][tab]
    dict = kic_sql(f"desc `{tab}`")
    if "dict" not in cache1:
        cache1["dict"] = {}
    cache1["dict"][tab] = dict
    return dict


def is_gen_table(tab):
    g = gen_data()
    gtab = f"{tab}_tab"
    if gtab in g:
        gen_id = g[gtab]["id"]
        d = get_data("gen", gen_id)
        if "tab_type" in d:
            if d["tab_type"] == "gen":
                return 1
    return 0


def kic_refine(x, v, cond):
    if "cln" in cond:
        for cln in cond["cln"]:
            v = v.replace(cln, "")
    if "toLower" in cond:
        v = v.lower()
    if "strip" in cond:
        v = v.strip()
    if "fill_zeros" in cond:
        v = str(v).zfill(cond["fill_zeros"])
    if v != "":
        if "min" in cond:
            if len(v) < cond["min"]:
                return {"status": 0, "err": f"length of {x} too small /{v}/"}
        if "max" in cond:
            if len(v) > cond["max"]:
                return {"status": 0, "err": f"length of {x} too long"}
        if "exactly" in cond:
            if len(v) != cond["exactly"]:
                return {"status": 0, "err": f'length of {x} must be {cond["exactly"]} == {cond} '}
        if "list" in cond:
            if v not in cond["list"]:
                return {"status": 0, "err": f'{x} = ({v}) not in a list {cond["list"]}'}
        if "regex" in cond:
            if not re.search(cond["regex"], v):
                return {"status": 0, "err": f"content of {x} must comply to regex"}
        if "is" in cond:
            for ii in cond["is"]:
                if ii == "email":
                    if not validate_email(v):
                        return {"status": 0, "err": "content not a valid email address"}
                if ii == "sum":
                    if v == 0:
                        continue
                    if not v:
                        return {"status": 0, "err": "content not a valid sum"}
                if ii == "yesno":
                    if v.strip() == "כן":
                        v = 1
                    else:
                        return {"status": 0, "err": f"must be yes or no /{v}/"}
                if ii == "date/mdy":
                    v = validate_datemdy(v)
                if ii == "bool01":
                    if v == "0" or v == "1" or v == 1 or v == 0:
                        v = int(v)
                    else:
                        return {"status": 0, "err": f"must be 0 or 1 /{v}/"}
                if ii == "phone":
                    v1 = v.replace("-", "")
                    if not re.fullmatch(r"\d{10}", v1):
                        return {"status": 0, "err": f"phone fromat wrong /{v}/", "errcode": 101}
    return v


def validate_email(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None


def validate_datemdy(v):
    d = v.split("/")
    day = int(d[1])
    mon = int(d[0])
    yir = int(d[2])
    y0 = int(datetime.today().strftime("%Y"))
    e = 0
    if day > 31 or day < 1:
        e = 1
    if mon > 12 or mon < 1:
        e = 2
    if yir > (y0 + 10) or yir < (y0 - 180):
        e = 3
    if e:
        return {"status": 0, "err": f"date wrong format ({e} / {y0})"}
    if day < 10:
        day = f"0{day}"
    if mon < 10:
        mon = f"0{mon}"
    v = f"{yir}-{mon}-{day}"
    return v


def kic_config():
    file_path = os.path.join(_server_root(), "config.py")
    spec = importlib.util.spec_from_file_location("config", file_path)
    if spec is None or spec.loader is None:
        raise FileNotFoundError(f"Could not load config.py from {file_path}")
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    return config


def kic_geresh(v):
    if type(v) is int or type(v) is float:
        return f"{v}"
    if v is None:
        return "NULL"
    s = str(v).replace("'", "''")
    return f"'{s}'"


def get_record(table, id, fld="id"):
    dict = kic_sql(f"desc `{table}`")
    z = find_in_sql({"table": table, "fld": fld, "val": id, "what": "*"})
    if type(z) is bool:
        return {}
    obj = array2obj(z, dict)
    jdata = get_data(table, id, fld)
    obj = {**obj, **jdata}
    if "data" in obj:
        del obj["data"]
    return obj


def sql_var(k, v, c="="):
    r = ""

    if type(v) is dict:
        v = json.dumps(v, ensure_ascii=False)

    if c.strip().lower() == "in":
        vals = []
        if type(v) in (list, tuple):
            for one in v:
                vals.append(kic_geresh(one))
            v = "(" + ",".join(vals) + ")"
        elif type(v) is str:
            v = v.strip()
            if not v.startswith("("):
                v = f"({v})"
        return f"""{k}{c}{v}"""

    if k in ["order", "key", "group", "order", "limit", "from", "to"]:
        r = "`"
    return f"""{r}{k}{r}{c}{kic_geresh(v)}"""


def sql_set(obj):
    if type(obj) is str:
        return obj
    set1 = ""
    for k in obj:
        v = obj[k]
        set1 += f",{sql_var(k, v)}"
    return set1[1:]


def sql_where(obj):
    if type(obj) is str or type(obj) is int:
        return str(obj), 1
    set1 = ""
    c = 0
    for k in obj:
        vv = obj[k]
        v = vv
        con = "="
        key = k.split("/")[0]
        if type(vv) is tuple:
            con0 = vv[0]
            v = vv[1]
            con = f" {con0} "
            if str(con0).lower() == "in":
                v = list(v)
            if str(con0).lower() == "like":
                v = f"%{v}%"
            if len(vv) > 2:
                key = _json_field_expr(vv[2], key)
        set1 += f" AND {sql_var(key, v, con)}"
        c = c + 1
    return set1[5:], c


def sql_join(tableas, r):
    j = ""
    for typ in ("join/INNER", "ljoin/LEFT", "rjoin/RIGHT"):
        ty = typ.split("/")
        key = ty[0]
        side = ty[1]
        if key in r:
            for join in r[key]:
                jtab = join["jtab"]
                onj = join.get("jon", "id")
                on1 = join["on"]
                jtabas = jtab if " " not in jtab else jtab.split(" ")[1]
                j += f"{side} JOIN {jtab} ON {tableas}.{on1}={jtabas}.{onj} "
                if "And" in join:
                    j += f' AND {join["And"]}'
    return j


def sqd(key):
    return _json_field_expr("data", key)


def sql_what(s):
    if ":" not in s:
        return s
    news = ""
    p = ""
    for one in str(s).split(","):
        if ":" in one:
            two = one.split(":")
            one = _json_field_expr(two[0], two[1])
        news += p + one
        p = ","
    return news


def sql_sortj(s):
    if ":" not in s:
        return s

    sall = s.split(":")
    l = len(sall)

    s1 = sall[0]
    s2 = sall[1] if l > 1 else ""
    s3 = sall[2] if l > 2 else ""
    s4 = sall[3] if l > 3 else ""

    out = s1

    if s2:
        out = _json_field_expr(s1, s2)

    opts = f"{s3}:{s4}".lower()

    if "int" in opts:
        if _is_mic():
            out = f"CAST({out} as INTEGER)"
        else:
            out = f"CAST({out} as SIGNED INTEGER)"

    if "desc" in opts:
        out = f"{out} DESC"

    return out
