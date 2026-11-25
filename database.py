"""Ma'lumotlar bazasi (SQLite). Hamma jadval va so'rovlar shu yerda.

sqlite3 sinxron ishlaydi, shuning uchun har bir so'rovni asyncio.to_thread
orqali alohida oqimda bajaramiz — bot qotib qolmaydi.
"""
import asyncio
import sqlite3
import threading
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Iterable, List, Optional

Row = Dict[str, Any]

PLACEHOLDER_NAME = "Yangi admin"

SUBJECTS_SEED = [
    "Matematika", "Algebra", "Geometriya", "Ona tili", "Adabiyot",
    "Ingliz tili", "Rus tili", "Fizika", "Kimyo", "Biologiya",
    "Tarix", "Geografiya", "Informatika",
]

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id    INTEGER PRIMARY KEY,
    full_name  TEXT    NOT NULL,
    username   TEXT,
    is_admin   INTEGER NOT NULL DEFAULT 0,
    status     TEXT    NOT NULL DEFAULT 'pending',   -- pending | approved | blocked
    created_at TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS subjects (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE COLLATE NOCASE
);

CREATE TABLE IF NOT EXISTS exams (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    year       TEXT    NOT NULL,                      -- masalan 2026-2027
    subject_id INTEGER NOT NULL REFERENCES subjects(id),
    grade      INTEGER NOT NULL,
    kind       TEXT    NOT NULL,                      -- BSB | CHSB
    number     INTEGER NOT NULL DEFAULT 0,            -- BSB uchun tartib raqami
    quarter    INTEGER NOT NULL DEFAULT 0,            -- CHSB uchun chorak (1-4)
    created_by INTEGER,
    created_at TEXT    NOT NULL,
    UNIQUE (year, subject_id, grade, kind, number, quarter)
);

CREATE TABLE IF NOT EXISTS exam_items (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_id  INTEGER NOT NULL REFERENCES exams(id) ON DELETE CASCADE,
    part     TEXT    NOT NULL,                        -- q = savollar, a = javoblar
    position INTEGER NOT NULL,
    ctype    TEXT    NOT NULL,                        -- text | document | photo
    content  TEXT    NOT NULL,                        -- matn yoki Telegram file_id
    caption  TEXT    NOT NULL DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_exams_lookup ON exams (year, subject_id, grade, kind);
CREATE INDEX IF NOT EXISTS idx_items_exam ON exam_items (exam_id, part, position);
"""


class DuplicateExam(Exception):
    """Bunday imtihon allaqachon bor (masalan, shu chorakning CHSB si)."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _one(conn: sqlite3.Connection, sql: str, params: Iterable[Any] = ()) -> Optional[Row]:
    row = conn.execute(sql, tuple(params)).fetchone()
    return dict(row) if row is not None else None


def _all(conn: sqlite3.Connection, sql: str, params: Iterable[Any] = ()) -> List[Row]:
    return [dict(r) for r in conn.execute(sql, tuple(params)).fetchall()]


class Database:
    def __init__(self) -> None:
        self._conn: Optional[sqlite3.Connection] = None
        self._lock = threading.Lock()
        self.owner_ids: frozenset = frozenset()

    # ---------- ulanish ----------
    async def connect(self, path: str, owner_ids: Iterable[int]) -> None:
        self.owner_ids = frozenset(owner_ids)
        await asyncio.to_thread(self._connect, path)

    def _connect(self, path: str) -> None:
        conn = sqlite3.connect(path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.executescript(SCHEMA)
        count = conn.execute("SELECT COUNT(*) FROM subjects").fetchone()[0]
        if count == 0:
            conn.executemany(
                "INSERT INTO subjects (name) VALUES (?)", [(n,) for n in SUBJECTS_SEED]
            )
        conn.commit()
        self._conn = conn

    async def close(self) -> None:
        if self._conn is not None:
            await asyncio.to_thread(self._conn.close)
            self._conn = None

    async def _run(self, func: Callable[[sqlite3.Connection], Any]) -> Any:
        def task() -> Any:
            with self._lock:
                assert self._conn is not None, "Baza ulanmagan"
                try:
                    result = func(self._conn)
                    self._conn.commit()
                    return result
                except Exception:
                    self._conn.rollback()
                    raise

        return await asyncio.to_thread(task)

    # ---------- foydalanuvchilar ----------
    def is_owner(self, user_id: int) -> bool:
        return user_id in self.owner_ids

    async def get_user(self, user_id: int) -> Optional[Row]:
        return await self._run(
            lambda c: _one(c, "SELECT * FROM users WHERE user_id = ?", (user_id,))
        )

    async def get_role(self, user_id: int) -> Optional[str]:
        """owner | admin | teacher | pending | blocked | None (hali ro'yxatdan o'tmagan)."""
        if self.is_owner(user_id):
            return "owner"
        row = await self.get_user(user_id)
        if row is None:
            return None
        if row["status"] == "blocked":
            return "blocked"
        if row["status"] == "pending":
            return "pending"
        return "admin" if row["is_admin"] else "teacher"

    async def upsert_pending(self, user_id: int, full_name: str, username: Optional[str]) -> None:
        def op(c: sqlite3.Connection) -> None:
            c.execute(
                """INSERT INTO users (user_id, full_name, username, is_admin, status, created_at)
                   VALUES (?, ?, ?, 0, 'pending', ?)
                   ON CONFLICT(user_id) DO UPDATE SET
                       full_name = excluded.full_name,
                       username  = excluded.username""",
                (user_id, full_name, username, _now()),
            )

        await self._run(op)

    async def touch_user(self, user_id: int, username: Optional[str], full_name: str) -> None:
        """Username o'zgargan bo'lsa yangilaydi; admin nomi 'Yangi admin' bo'lsa, haqiqiy ismini yozadi."""

        def op(c: sqlite3.Connection) -> None:
            c.execute(
                """UPDATE users SET username = ?,
                       full_name = CASE WHEN full_name = ? THEN ? ELSE full_name END
                   WHERE user_id = ?""",
                (username, PLACEHOLDER_NAME, full_name, user_id),
            )

        await self._run(op)

    async def set_status(self, user_id: int, status: str) -> None:
        await self._run(
            lambda c: c.execute("UPDATE users SET status = ? WHERE user_id = ?", (status, user_id))
        )

    async def delete_user(self, user_id: int) -> None:
        await self._run(lambda c: c.execute("DELETE FROM users WHERE user_id = ?", (user_id,)))

    async def make_admin(self, user_id: int) -> None:
        def op(c: sqlite3.Connection) -> None:
            c.execute(
                """INSERT INTO users (user_id, full_name, username, is_admin, status, created_at)
                   VALUES (?, ?, NULL, 1, 'approved', ?)
                   ON CONFLICT(user_id) DO UPDATE SET is_admin = 1, status = 'approved'""",
                (user_id, PLACEHOLDER_NAME, _now()),
            )

        await self._run(op)

    async def remove_admin(self, user_id: int) -> None:
        await self._run(
            lambda c: c.execute("UPDATE users SET is_admin = 0 WHERE user_id = ?", (user_id,))
        )

    async def list_users(self) -> List[Row]:
        """Oddiy ustozlar (adminlarsiz). Kutayotganlar birinchi."""
        return await self._run(
            lambda c: _all(
                c,
                """SELECT * FROM users WHERE is_admin = 0
                   ORDER BY CASE status WHEN 'pending' THEN 0 WHEN 'approved' THEN 1 ELSE 2 END,
                            full_name COLLATE NOCASE""",
            )
        )

    async def list_admins(self) -> List[Row]:
        return await self._run(
            lambda c: _all(c, "SELECT * FROM users WHERE is_admin = 1 ORDER BY full_name COLLATE NOCASE")
        )

    async def approved_ids(self) -> List[int]:
        rows = await self._run(
            lambda c: _all(c, "SELECT user_id FROM users WHERE status = 'approved'")
        )
        return [r["user_id"] for r in rows]

    async def staff_ids(self) -> List[int]:
        """Egalar + faol adminlar (so'rovlarni ko'ra oladiganlar)."""
        rows = await self._run(
            lambda c: _all(c, "SELECT user_id FROM users WHERE is_admin = 1 AND status = 'approved'")
        )
        ids = list(self.owner_ids)
        for r in rows:
            if r["user_id"] not in ids:
                ids.append(r["user_id"])
        return ids

    # ---------- fanlar ----------
    async def list_subjects(self) -> List[Row]:
        return await self._run(
            lambda c: _all(c, "SELECT id, name FROM subjects ORDER BY name COLLATE NOCASE")
        )

    async def get_subject(self, subject_id: int) -> Optional[Row]:
        return await self._run(
            lambda c: _one(c, "SELECT id, name FROM subjects WHERE id = ?", (subject_id,))
        )

    async def add_subject(self, name: str) -> Optional[int]:
        """Yangi fan qo'shadi. Agar bunday fan bor bo'lsa, None qaytaradi."""

        def op(c: sqlite3.Connection) -> Optional[int]:
            try:
                cur = c.execute("INSERT INTO subjects (name) VALUES (?)", (name,))
                return cur.lastrowid
            except sqlite3.IntegrityError:
                return None

        return await self._run(op)

    # ---------- imtihonlar ----------
    async def find_chsb(self, year: str, subject_id: int, grade: int, quarter: int) -> Optional[Row]:
        return await self._run(
            lambda c: _one(
                c,
                """SELECT * FROM exams WHERE year = ? AND subject_id = ? AND grade = ?
                   AND kind = 'CHSB' AND quarter = ?""",
                (year, subject_id, grade, quarter),
            )
        )

    async def add_exam(
        self,
        *,
        year: str,
        subject_id: int,
        grade: int,
        kind: str,
        quarter: int,
        created_by: int,
        questions: List[Row],
        answers: List[Row],
        replace: bool = False,
    ) -> int:
        """Imtihonni saqlaydi va id sini qaytaradi.

        BSB: tartib raqami avtomatik beriladi (BSB-1, BSB-2, ...).
        CHSB: bir chorakka bitta; allaqachon bo'lsa DuplicateExam (replace=True bo'lsa almashtiradi).
        """

        def op(c: sqlite3.Connection) -> int:
            number = 0
            q = 0
            if kind == "CHSB":
                q = quarter
                if replace:
                    c.execute(
                        """DELETE FROM exams WHERE year = ? AND subject_id = ? AND grade = ?
                           AND kind = 'CHSB' AND quarter = ?""",
                        (year, subject_id, grade, quarter),
                    )
            else:
                number = c.execute(
                    """SELECT COALESCE(MAX(number), 0) + 1 FROM exams
                       WHERE year = ? AND subject_id = ? AND grade = ? AND kind = 'BSB'""",
                    (year, subject_id, grade),
                ).fetchone()[0]
            try:
                cur = c.execute(
                    """INSERT INTO exams (year, subject_id, grade, kind, number, quarter, created_by, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (year, subject_id, grade, kind, number, q, created_by, _now()),
                )
            except sqlite3.IntegrityError as exc:
                raise DuplicateExam() from exc
            exam_id = cur.lastrowid
            for part, items in (("q", questions), ("a", answers)):
                for pos, item in enumerate(items):
                    c.execute(
                        """INSERT INTO exam_items (exam_id, part, position, ctype, content, caption)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (exam_id, part, pos, item["ctype"], item["content"], item.get("caption", "")),
                    )
            return exam_id

        return await self._run(op)

    _EXAM_SELECT = """SELECT e.*, s.name AS subject_name
                      FROM exams e JOIN subjects s ON s.id = e.subject_id"""

    async def get_exam(self, exam_id: int) -> Optional[Row]:
        return await self._run(
            lambda c: _one(c, self._EXAM_SELECT + " WHERE e.id = ?", (exam_id,))
        )

    async def get_items(self, exam_id: int, part: str) -> List[Row]:
        return await self._run(
            lambda c: _all(
                c,
                "SELECT * FROM exam_items WHERE exam_id = ? AND part = ? ORDER BY position",
                (exam_id, part),
            )
        )

    async def list_exams(self, year: str, subject_id: int, grade: int, kind: str) -> List[Row]:
        return await self._run(
            lambda c: _all(
                c,
                self._EXAM_SELECT
                + """ WHERE e.year = ? AND e.subject_id = ? AND e.grade = ? AND e.kind = ?
                      ORDER BY e.number, e.quarter""",
                (year, subject_id, grade, kind),
            )
        )

    async def search_exams(
        self,
        year: str,
        subject_ids: Optional[List[int]] = None,
        grade: Optional[int] = None,
        kind: Optional[str] = None,
        number: Optional[int] = None,
        limit: int = 30,
    ) -> List[Row]:
        sql = self._EXAM_SELECT + " WHERE e.year = ?"
        params: List[Any] = [year]
        if subject_ids:
            sql += " AND e.subject_id IN (%s)" % ",".join("?" * len(subject_ids))
            params.extend(subject_ids)
        if grade is not None:
            sql += " AND e.grade = ?"
            params.append(grade)
        if kind is not None:
            sql += " AND e.kind = ?"
            params.append(kind)
        if number is not None:
            if kind == "BSB":
                sql += " AND e.number = ?"
                params.append(number)
            elif kind == "CHSB":
                sql += " AND e.quarter = ?"
                params.append(number)
            else:
                sql += " AND (e.number = ? OR e.quarter = ?)"
                params.extend([number, number])
        sql += " ORDER BY s.name COLLATE NOCASE, e.grade, e.kind, e.number, e.quarter LIMIT ?"
        params.append(limit)
        return await self._run(lambda c: _all(c, sql, params))

    async def delete_exam(self, exam_id: int) -> None:
        await self._run(lambda c: c.execute("DELETE FROM exams WHERE id = ?", (exam_id,)))


db = Database()
