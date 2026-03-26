import json
import sqlite3
import time
import uuid
from dataclasses import dataclass, field, asdict
from pathlib import Path

from labeldesk.core.paths import jobDbPath


@dataclass
class Job:
    id: str = ""
    createdAt: float = 0.0
    status: str = "queued"
    inputPaths: list[str] = field(default_factory=list)
    adapter: str = ""
    mode: str = "title"
    outputFmt: str = "preview"
    totalFiles: int = 0
    doneFiles: int = 0
    tokensUsed: int = 0
    costUsd: float = 0.0
    error: str = ""
    resultPath: str = ""
    results: dict = field(default_factory=dict)


class JobStore:
    def __init__(self, dbPath: str | Path | None = None):
        p = dbPath or jobDbPath()
        self._db = sqlite3.connect(str(p), check_same_thread=False)
        self._init()

    def _init(self):
        self._db.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                created_at REAL, status TEXT,
                input_paths TEXT, adapter TEXT, mode TEXT, output_fmt TEXT,
                total_files INTEGER, done_files INTEGER,
                tokens_used INTEGER, cost_usd REAL,
                error TEXT, result_path TEXT, results TEXT
            )
        """)
        self._db.commit()

    def create(self, **kw) -> Job:
        j = Job(id=str(uuid.uuid4())[:8], createdAt=time.time(), **kw)
        self._save(j)
        return j

    def _save(self, j: Job):
        self._db.execute("""
            INSERT OR REPLACE INTO jobs VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (j.id, j.createdAt, j.status, json.dumps(j.inputPaths),
              j.adapter, j.mode, j.outputFmt, j.totalFiles, j.doneFiles,
              j.tokensUsed, j.costUsd, j.error, j.resultPath, json.dumps(j.results)))
        self._db.commit()

    def update(self, j: Job):
        self._save(j)

    def get(self, jobId: str) -> Job | None:
        row = self._db.execute("SELECT * FROM jobs WHERE id = ?", (jobId,)).fetchone()
        return self._fromRow(row) if row else None

    def list(self, limit: int = 50) -> list[Job]:
        rows = self._db.execute(
            "SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [self._fromRow(r) for r in rows]

    def delete(self, jobId: str):
        self._db.execute("DELETE FROM jobs WHERE id = ?", (jobId,))
        self._db.commit()

    def _fromRow(self, r) -> Job:
        return Job(
            id=r[0], createdAt=r[1], status=r[2],
            inputPaths=json.loads(r[3]), adapter=r[4], mode=r[5], outputFmt=r[6],
            totalFiles=r[7], doneFiles=r[8], tokensUsed=r[9], costUsd=r[10],
            error=r[11] or "", resultPath=r[12] or "",
            results=json.loads(r[13]) if r[13] else {},
        )

    def close(self):
        self._db.close()
