import json
import sqlite3
from datetime import datetime, timezone
from typing import Any


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class Database:
    def __init__(self, path: str):
        self.path = path
        self._init()

    def _connect(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init(self):
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id INTEGER PRIMARY KEY,
                    username TEXT,
                    display_name TEXT,
                    memory_json TEXT NOT NULL DEFAULT '[]',
                    history_json TEXT NOT NULL DEFAULT '[]',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def get_or_create_user(
        self,
        telegram_id: int,
        username: str | None,
        display_name: str | None,
    ) -> dict[str, Any]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE telegram_id = ?",
                (telegram_id,),
            ).fetchone()

            if row is None:
                ts = now_iso()
                conn.execute(
                    """
                    INSERT INTO users
                    (telegram_id, username, display_name, memory_json,
                     history_json, created_at, updated_at)
                    VALUES (?, ?, ?, '[]', '[]', ?, ?)
                    """,
                    (telegram_id, username, display_name, ts, ts),
                )
                conn.commit()
                row = conn.execute(
                    "SELECT * FROM users WHERE telegram_id = ?",
                    (telegram_id,),
                ).fetchone()

            return self._row_to_dict(row)

    def save_user(
        self,
        telegram_id: int,
        memory: list[str],
        history: list[dict[str, str]],
        username: str | None = None,
        display_name: str | None = None,
    ):
        memory = memory[-30:]
        history = history[-24:]

        with self._connect() as conn:
            conn.execute(
                """
                UPDATE users
                SET username = COALESCE(?, username),
                    display_name = COALESCE(?, display_name),
                    memory_json = ?,
                    history_json = ?,
                    updated_at = ?
                WHERE telegram_id = ?
                """,
                (
                    username,
                    display_name,
                    json.dumps(memory, ensure_ascii=False),
                    json.dumps(history, ensure_ascii=False),
                    now_iso(),
                    telegram_id,
                ),
            )
            conn.commit()

    def clear_history(self, telegram_id: int):
        with self._connect() as conn:
            conn.execute(
                "UPDATE users SET history_json = '[]', updated_at = ? WHERE telegram_id = ?",
                (now_iso(), telegram_id),
            )
            conn.commit()

    def clear_all(self, telegram_id: int):
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE users
                SET memory_json = '[]',
                    history_json = '[]',
                    updated_at = ?
                WHERE telegram_id = ?
                """,
                (now_iso(), telegram_id),
            )
            conn.commit()

    @staticmethod
    def _row_to_dict(row) -> dict[str, Any]:
        data = dict(row)
        data["memory"] = json.loads(data.pop("memory_json") or "[]")
        data["history"] = json.loads(data.pop("history_json") or "[]")
        return data
