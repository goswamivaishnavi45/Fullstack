# Helper (not part of the app) to look inside tracker.db. Run: python show_db.py
import sqlite3

conn = sqlite3.connect("tracker.db")
tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]

for table in tables:
    print(f"\n===== {table} =====")
    print(conn.execute("SELECT sql FROM sqlite_master WHERE name = ?", (table,)).fetchone()[0])
    rows = conn.execute(f"SELECT * FROM {table}").fetchall()
    print(f"-- {len(rows)} row(s):")
    for row in rows:
        print(row)

conn.close()
