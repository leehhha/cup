"""SQLite database layer for Gift Reminder app."""

import sqlite3
import json
import os
from datetime import datetime, date
from pathlib import Path


def get_db_path() -> Path:
    """Return the path to the SQLite database in ~/Library/Application Support."""
    app_dir = Path.home() / "Library" / "Application Support" / "GiftReminder"
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir / "gift_reminder.db"


class Database:
    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or str(get_db_path())
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS profile (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                partner_name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS setup_answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_key TEXT NOT NULL UNIQUE,
                question_text TEXT NOT NULL,
                answer TEXT NOT NULL,
                category TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS gift_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gift_name TEXT NOT NULL,
                gift_type TEXT NOT NULL CHECK (gift_type IN ('monthly', 'quarterly')),
                category TEXT,
                date_given TEXT NOT NULL,
                rating INTEGER CHECK (rating BETWEEN 1 AND 5),
                notes TEXT,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reminder_type TEXT NOT NULL CHECK (reminder_type IN ('monthly', 'quarterly', 'update')),
                next_due TEXT NOT NULL,
                last_triggered TEXT,
                is_active INTEGER NOT NULL DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS update_answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_text TEXT NOT NULL,
                answer TEXT NOT NULL,
                session_date TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS app_state (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
        """)
        self.conn.commit()

    # --- Profile ---

    def save_profile(self, partner_name: str):
        now = datetime.now().isoformat()
        self.conn.execute(
            """INSERT INTO profile (id, partner_name, created_at, updated_at)
               VALUES (1, ?, ?, ?)
               ON CONFLICT(id) DO UPDATE SET partner_name=?, updated_at=?""",
            (partner_name, now, now, partner_name, now),
        )
        self.conn.commit()

    def get_profile(self) -> dict | None:
        row = self.conn.execute("SELECT * FROM profile WHERE id = 1").fetchone()
        return dict(row) if row else None

    def is_setup_complete(self) -> bool:
        return self.get_profile() is not None

    # --- Setup Answers ---

    def save_setup_answer(self, question_key: str, question_text: str, answer: str, category: str):
        self.conn.execute(
            """INSERT INTO setup_answers (question_key, question_text, answer, category)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(question_key) DO UPDATE SET answer=?""",
            (question_key, question_text, answer, category, answer),
        )
        self.conn.commit()

    def get_setup_answers(self) -> list[dict]:
        rows = self.conn.execute("SELECT * FROM setup_answers ORDER BY id").fetchall()
        return [dict(r) for r in rows]

    def get_answered_question_keys(self) -> set[str]:
        rows = self.conn.execute("SELECT question_key FROM setup_answers").fetchall()
        return {r["question_key"] for r in rows}

    def get_answers_by_category(self, category: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM setup_answers WHERE category = ?", (category,)
        ).fetchall()
        return [dict(r) for r in rows]

    # --- Gift History ---

    def add_gift(self, gift_name: str, gift_type: str, category: str, date_given: str, notes: str = ""):
        now = datetime.now().isoformat()
        self.conn.execute(
            """INSERT INTO gift_history (gift_name, gift_type, category, date_given, notes, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (gift_name, gift_type, category, date_given, notes, now),
        )
        self.conn.commit()

    def get_all_gifts(self) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM gift_history ORDER BY date_given DESC"
        ).fetchall()
        return [dict(r) for r in rows]

    def get_recent_gifts(self, limit: int = 10) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM gift_history ORDER BY date_given DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

    def rate_gift(self, gift_id: int, rating: int, notes: str = ""):
        self.conn.execute(
            "UPDATE gift_history SET rating = ?, notes = ? WHERE id = ?",
            (rating, notes, gift_id),
        )
        self.conn.commit()

    def get_gifts_by_type(self, gift_type: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM gift_history WHERE gift_type = ? ORDER BY date_given DESC",
            (gift_type,),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_gift_categories_given(self) -> list[str]:
        rows = self.conn.execute(
            "SELECT DISTINCT category FROM gift_history WHERE category IS NOT NULL"
        ).fetchall()
        return [r["category"] for r in rows]

    # --- Reminders ---

    def init_reminders(self):
        """Initialize default reminders if none exist."""
        existing = self.conn.execute("SELECT COUNT(*) as c FROM reminders").fetchone()["c"]
        if existing > 0:
            return

        today = date.today()
        # Monthly reminder: first of next month
        if today.month == 12:
            next_monthly = date(today.year + 1, 1, 1)
        else:
            next_monthly = date(today.year, today.month + 1, 1)

        # Quarterly reminder: next quarter start
        quarter_month = ((today.month - 1) // 3 + 1) * 3 + 1
        if quarter_month > 12:
            next_quarterly = date(today.year + 1, quarter_month - 12, 1)
        else:
            next_quarterly = date(today.year, quarter_month, 1)

        # 6-month update: 6 months from now
        update_month = today.month + 6
        update_year = today.year
        if update_month > 12:
            update_month -= 12
            update_year += 1
        next_update = date(update_year, update_month, 1)

        for rtype, rdate in [
            ("monthly", next_monthly),
            ("quarterly", next_quarterly),
            ("update", next_update),
        ]:
            self.conn.execute(
                "INSERT INTO reminders (reminder_type, next_due) VALUES (?, ?)",
                (rtype, rdate.isoformat()),
            )
        self.conn.commit()

    def get_due_reminders(self) -> list[dict]:
        today = date.today().isoformat()
        rows = self.conn.execute(
            "SELECT * FROM reminders WHERE next_due <= ? AND is_active = 1", (today,)
        ).fetchall()
        return [dict(r) for r in rows]

    def advance_reminder(self, reminder_id: int):
        """Advance a reminder to its next occurrence."""
        row = self.conn.execute(
            "SELECT * FROM reminders WHERE id = ?", (reminder_id,)
        ).fetchone()
        if not row:
            return

        current_due = date.fromisoformat(row["next_due"])
        today = date.today()
        rtype = row["reminder_type"]

        if rtype == "monthly":
            m = current_due.month + 1
            y = current_due.year
            if m > 12:
                m -= 12
                y += 1
            next_due = date(y, m, 1)
        elif rtype == "quarterly":
            m = current_due.month + 3
            y = current_due.year
            if m > 12:
                m -= 12
                y += 1
            next_due = date(y, m, 1)
        else:  # update (6-month)
            m = current_due.month + 6
            y = current_due.year
            if m > 12:
                m -= 12
                y += 1
            next_due = date(y, m, 1)

        self.conn.execute(
            "UPDATE reminders SET next_due = ?, last_triggered = ? WHERE id = ?",
            (next_due.isoformat(), today.isoformat(), reminder_id),
        )
        self.conn.commit()

    def get_all_reminders(self) -> list[dict]:
        rows = self.conn.execute("SELECT * FROM reminders ORDER BY next_due").fetchall()
        return [dict(r) for r in rows]

    # --- Update Answers ---

    def save_update_answer(self, question_text: str, answer: str):
        now = datetime.now().isoformat()
        today = date.today().isoformat()
        self.conn.execute(
            "INSERT INTO update_answers (question_text, answer, session_date, created_at) VALUES (?, ?, ?, ?)",
            (question_text, answer, today, now),
        )
        self.conn.commit()

    def get_update_sessions(self) -> list[str]:
        rows = self.conn.execute(
            "SELECT DISTINCT session_date FROM update_answers ORDER BY session_date DESC"
        ).fetchall()
        return [r["session_date"] for r in rows]

    def get_update_answers_for_session(self, session_date: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM update_answers WHERE session_date = ?", (session_date,)
        ).fetchall()
        return [dict(r) for r in rows]

    # --- Wizard Drafts ---

    def save_wizard_draft(self, partner_name: str, answers: dict, current_index: int):
        """Persist in-progress wizard answers keyed by partner name."""
        payload = json.dumps({"answers": answers, "index": current_index})
        self.set_state(f"draft:{partner_name}", payload)

    def get_wizard_drafts(self) -> list[dict]:
        """Return all saved wizard drafts as [{name, answers, index}, ...]."""
        rows = self.conn.execute(
            "SELECT key, value FROM app_state WHERE key LIKE 'draft:%'"
        ).fetchall()
        drafts = []
        for r in rows:
            name = r["key"][len("draft:"):]
            data = json.loads(r["value"])
            drafts.append({"name": name, "answers": data["answers"], "index": data["index"]})
        return drafts

    def load_wizard_draft(self, partner_name: str) -> dict | None:
        """Load a specific draft by partner name. Returns {answers, index} or None."""
        raw = self.get_state(f"draft:{partner_name}")
        if not raw:
            return None
        return json.loads(raw)

    def clear_wizard_draft(self, partner_name: str):
        """Remove a wizard draft after successful setup completion."""
        self.conn.execute("DELETE FROM app_state WHERE key = ?", (f"draft:{partner_name}",))
        self.conn.commit()

    def clear_all_wizard_drafts(self):
        """Remove all wizard drafts."""
        self.conn.execute("DELETE FROM app_state WHERE key LIKE 'draft:%'")
        self.conn.commit()

    # --- App State ---

    def set_state(self, key: str, value: str):
        self.conn.execute(
            "INSERT INTO app_state (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=?",
            (key, value, value),
        )
        self.conn.commit()

    def get_state(self, key: str, default: str = "") -> str:
        row = self.conn.execute(
            "SELECT value FROM app_state WHERE key = ?", (key,)
        ).fetchone()
        return row["value"] if row else default

    def close(self):
        self.conn.close()
