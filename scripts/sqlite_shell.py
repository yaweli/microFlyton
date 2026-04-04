import sqlite3
import sys
import os
import re
import cmd


def _translate(line):
    """Convert common MySQL commands to SQLite equivalents."""
    stripped = line.rstrip(";").strip()
    upper = stripped.upper()

    # SHOW TABLES
    if upper == "SHOW TABLES":
        return "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name", None

    # SHOW DATABASES
    if upper in ("SHOW DATABASES", "SHOW SCHEMAS"):
        return None, "(SQLite has no databases — single file)"

    # USE <db>
    if re.match(r"^USE\s+\S+$", upper):
        return None, "(SQLite has no USE — single file DB)"

    # DESCRIBE / DESC <table>
    m = re.match(r"^(?:DESCRIBE|DESC)\s+(\S+)$", stripped, re.IGNORECASE)
    if m:
        table = m.group(1)
        return f"PRAGMA table_info({table})", None

    # SHOW COLUMNS FROM <table>
    m = re.match(r"^SHOW COLUMNS FROM\s+(\S+)$", stripped, re.IGNORECASE)
    if m:
        table = m.group(1)
        return f"PRAGMA table_info({table})", None

    # SHOW CREATE TABLE <table>
    m = re.match(r"^SHOW CREATE TABLE\s+(\S+)$", stripped, re.IGNORECASE)
    if m:
        table = m.group(1)
        return (
            f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'",
            None,
        )

    # SHOW INDEX FROM <table>
    m = re.match(r"^SHOW (?:INDEX|INDEXES|KEYS) FROM\s+(\S+)$", stripped, re.IGNORECASE)
    if m:
        table = m.group(1)
        return f"PRAGMA index_list({table})", None

    # SHOW STATUS / SHOW VARIABLES
    if re.match(r"^SHOW (?:STATUS|VARIABLES)", upper):
        return None, "(not supported in SQLite)"

    return line, None


class SQLiteShell(cmd.Cmd):
    prompt = "mysql> "
    intro = ""

    def __init__(self, db_path):
        super().__init__()
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        print(f"SQLite {sqlite3.sqlite_version}  --  {db_path}")
        print("MySQL-compatible shell. Type 'help' for commands, 'exit' to quit.")
        print()

    def default(self, line):
        line = line.strip()
        if not line or line.startswith("--"):
            return
        if line.lower().rstrip(";") in ("exit", "quit", "\\q"):
            self.conn.close()
            return True
        if line.lower() in ("help", "\\h", "?"):
            self._print_help()
            return

        translated, message = _translate(line)
        if message:
            print(message)
            return
        if translated is None:
            return

        try:
            cur = self.conn.execute(translated)
            if cur.description:
                cols = [d[0] for d in cur.description]
                widths = [len(c) for c in cols]
                rows = cur.fetchall()
                for row in rows:
                    for i, v in enumerate(row):
                        widths[i] = max(widths[i], len("" if v is None else str(v)))
                sep = "+-" + "-+-".join("-" * w for w in widths) + "-+"
                fmt = "| " + " | ".join(f"{{:<{w}}}" for w in widths) + " |"
                print(sep)
                print(fmt.format(*cols))
                print(sep)
                for row in rows:
                    print(fmt.format(*("" if v is None else str(v) for v in row)))
                print(sep)
                print(f"{len(rows)} row(s) in set")
            else:
                self.conn.commit()
                print(f"Query OK, {cur.rowcount} row(s) affected")
        except Exception as e:
            print(f"ERROR: {e}")

    def _print_help(self):
        print("""
Commands supported:
  SHOW TABLES                  list all tables
  DESCRIBE <table>             show columns
  DESC <table>                 show columns
  SHOW COLUMNS FROM <table>    show columns
  SHOW CREATE TABLE <table>    show DDL
  SHOW INDEX FROM <table>      show indexes
  USE <db>                     (not applicable in SQLite)
  exit / quit                  close shell

Any standard SQL (SELECT, INSERT, UPDATE, DELETE, CREATE, DROP) works directly.
""")

    def do_EOF(self, _):
        print()
        self.conn.close()
        return True

    def emptyline(self):
        pass


if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else ":memory:"
    shell = SQLiteShell(db_path)
    try:
        shell.cmdloop()
    except KeyboardInterrupt:
        print()
        shell.conn.close()
