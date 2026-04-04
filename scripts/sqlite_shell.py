import sqlite3
import sys
import os
import cmd


class SQLiteShell(cmd.Cmd):
    prompt = "sqlite> "
    intro = ""

    def __init__(self, db_path):
        super().__init__()
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        print(f"SQLite {sqlite3.sqlite_version}  --  {db_path}")
        print("Commands: .tables  .schema  .exit  or any SQL")
        print()

    def default(self, line):
        line = line.strip()
        if not line:
            return
        if line in (".exit", ".quit", "exit", "quit"):
            self.conn.close()
            return True
        if line == ".tables":
            cur = self.conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
            for row in cur:
                print(row[0])
            return
        if line.startswith(".schema"):
            parts = line.split(None, 1)
            table_filter = parts[1].strip() if len(parts) > 1 else None
            query = "SELECT sql FROM sqlite_master WHERE sql IS NOT NULL"
            if table_filter:
                query += f" AND name='{table_filter}'"
            query += " ORDER BY type, name"
            cur = self.conn.execute(query)
            for row in cur:
                if row[0]:
                    print(row[0])
            return
        try:
            cur = self.conn.execute(line)
            if cur.description:
                cols = [d[0] for d in cur.description]
                print("  ".join(cols))
                print("  ".join("-" * len(c) for c in cols))
                for row in cur:
                    print("  ".join("" if v is None else str(v) for v in row))
            else:
                self.conn.commit()
                print(f"OK  ({cur.rowcount} rows affected)")
        except Exception as e:
            print(f"Error: {e}")

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
