import sys
import os
import subprocess

MYSQL_BIN = r"C:\mysql_lite\bin\mysql.exe"
SQL_FILE  = os.path.join(os.path.dirname(__file__), "init_tables.sql")

def run(host="127.0.0.1", user="root", password=""):
    cmd = [MYSQL_BIN, f"-h{host}", f"-u{user}"]
    if password:
        cmd.append(f"-p{password}")
    cmd += ["--execute", f"source {SQL_FILE}"]

    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"ERROR: {r.stderr}")
        sys.exit(1)
    print("Tables initialized.")

if __name__ == "__main__":
    host     = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    user     = sys.argv[2] if len(sys.argv) > 2 else "root"
    password = sys.argv[3] if len(sys.argv) > 3 else ""
    run(host, user, password)
