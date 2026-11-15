import json
import sqlite3
from pathlib import Path
from .models import Entry

class Storage:
    def __init__(self, db_path=None):
        base = Path.home() / ".quickdock"
        base.mkdir(parents=True, exist_ok=True)
        self.db_path = Path(db_path) if db_path else base / "quickdock.db"
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        with self.conn:
            self.conn.execute("""CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
                kind TEXT NOT NULL, executable TEXT NOT NULL,
                arguments TEXT NOT NULL DEFAULT '[]', working_dir TEXT NOT NULL DEFAULT '',
                favorite INTEGER NOT NULL DEFAULT 0)""")
            self.conn.execute("""CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT, entry_name TEXT NOT NULL,
                started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, return_code INTEGER)""")

    def list_entries(self, query=""):
        sql, params = "SELECT * FROM entries", []
        if query:
            sql += " WHERE name LIKE ? OR executable LIKE ?"
            params = [f"%{query}%", f"%{query}%"]
        sql += " ORDER BY favorite DESC, name COLLATE NOCASE"
        return [self._convert(r) for r in self.conn.execute(sql, params).fetchall()]

    def get_entry(self, entry_id):
        row = self.conn.execute("SELECT * FROM entries WHERE id=?", (entry_id,)).fetchone()
        return self._convert(row) if row else None

    @staticmethod
    def _convert(row):
        return Entry(row["name"], row["kind"], row["executable"],
                     json.loads(row["arguments"]), row["working_dir"],
                     bool(row["favorite"]), row["id"])

    def save_entry(self, entry):
        entry.validate()
        values = (entry.name.strip(), entry.kind, entry.executable,
                  json.dumps(entry.arguments), entry.working_dir, int(entry.favorite))
        with self.conn:
            if entry.id is None:
                cur = self.conn.execute(
                    "INSERT INTO entries(name,kind,executable,arguments,working_dir,favorite) VALUES(?,?,?,?,?,?)", values)
                entry.id = cur.lastrowid
            else:
                self.conn.execute(
                    "UPDATE entries SET name=?,kind=?,executable=?,arguments=?,working_dir=?,favorite=? WHERE id=?",
                    values + (entry.id,))
        return entry

    def delete_entry(self, entry_id):
        with self.conn:
            self.conn.execute("DELETE FROM entries WHERE id=?", (entry_id,))

    def add_history(self, name, return_code):
        with self.conn:
            self.conn.execute("INSERT INTO history(entry_name,return_code) VALUES(?,?)", (name, return_code))

    def list_history(self, limit=30):
        return self.conn.execute(
            "SELECT entry_name,started_at,return_code FROM history ORDER BY id DESC LIMIT ?", (limit,)).fetchall()

    def export_json(self, path):
        payload = {"version": 1, "entries": [e.to_dict() for e in self.list_entries()]}
        Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def import_json(self, path):
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        if payload.get("version") != 1 or not isinstance(payload.get("entries"), list):
            raise ValueError("Unsupported backup format")
        count = 0
        for item in payload["entries"]:
            entry = Entry(str(item["name"]), str(item["kind"]), str(item["executable"]),
                          [str(x) for x in item.get("arguments", [])],
                          str(item.get("working_dir", "")), bool(item.get("favorite", False)))
            self.save_entry(entry)
            count += 1
        return count

    def close(self):
        self.conn.close()
