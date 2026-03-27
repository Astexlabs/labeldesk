import json
import sqlite3
import time
from pathlib import Path

from labeldesk.core.models.result import LabelResult
from labeldesk.core.paths import cacheDbPath


class ResultCache:
    """sqlite cache keyed by phash + mode + model"""

    def __init__(self, dbPath: str | Path | None = None):
        p = dbPath or cacheDbPath()
        self._db = sqlite3.connect(str(p), check_same_thread=False)
        self._initTbl()

    def _initTbl(self):
        self._db.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                title TEXT, desc TEXT, tags TEXT,
                src TEXT, ts REAL, extra TEXT DEFAULT '{}'
            )
        """)
        try:
            self._db.execute("ALTER TABLE cache ADD COLUMN extra TEXT DEFAULT '{}'")
        except sqlite3.OperationalError:
            pass
        self._db.commit()

    def _makeKey(self, phash: str, mode: str, model: str) -> str:
        return f"{phash}:{mode}:{model}"

    def get(self, phash: str, mode: str, model: str) -> LabelResult | None:
        key = self._makeKey(phash, mode, model)
        row = self._db.execute(
            "SELECT title, desc, tags, src, extra FROM cache WHERE key = ?", (key,)
        ).fetchone()
        if row is None:
            return None
        return LabelResult(
            title=row[0], desc=row[1],
            tags=json.loads(row[2]), src=row[3],
            extra=json.loads(row[4] or "{}"), cached=True,
        )

    def put(self, phash: str, mode: str, model: str, result: LabelResult):
        key = self._makeKey(phash, mode, model)
        self._db.execute(
            "INSERT OR REPLACE INTO cache (key, title, desc, tags, src, ts, extra) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (key, result.title, result.desc, json.dumps(result.tags),
             result.src, time.time(), json.dumps(result.extra)),
        )
        self._db.commit()

    def getPartial(self, phash: str, model: str) -> dict:
        rows = self._db.execute(
            "SELECT key, title, desc, tags FROM cache WHERE key LIKE ?",
            (f"{phash}:%:{model}",),
        ).fetchall()
        parts = {}
        for row in rows:
            mode = row[0].split(":")[1]
            parts[mode] = LabelResult(
                title=row[1], desc=row[2], tags=json.loads(row[3]), cached=True
            )
        return parts

    def evictOld(self, maxAgeSec: float = 86400 * 30):
        cutoff = time.time() - maxAgeSec
        self._db.execute("DELETE FROM cache WHERE ts < ?", (cutoff,))
        self._db.commit()

    def clear(self):
        self._db.execute("DELETE FROM cache")
        self._db.commit()

    def close(self):
        self._db.close()
