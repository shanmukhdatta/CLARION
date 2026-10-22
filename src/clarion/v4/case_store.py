"""SQLite-backed local investigative case reviews with tamper-evident event chain.

Lead scores are immutable evidence; annotations and decisions live in a separate
transactional database. A review is never a claim of crime or wallet ownership.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

Status = Literal["NEW", "IN_REVIEW", "DISMISSED", "ESCALATED"]
TRANSITIONS: dict[str, set[str]] = {
    "NEW": {"IN_REVIEW"},
    "IN_REVIEW": {"DISMISSED", "ESCALATED"},
    "DISMISSED": {"IN_REVIEW"},
    "ESCALATED": {"IN_REVIEW"},
}
ZERO_HASH = "0" * 64


def _stamp() -> str:
    return datetime.now(UTC).isoformat()


def _hash_event(payload: dict[str, object]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


class ReviewConflict(ValueError):
    """Requested status transition or evidence version is not valid."""


class CaseStore:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.migrate()

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA busy_timeout=10000")
        db.execute("PRAGMA foreign_keys=ON")
        return db

    def migrate(self) -> None:
        """Idempotent schema migration; avoid destructive changes to existing reviews."""
        with self._connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS reviews (
                    txid TEXT NOT NULL,
                    run_sha256 TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN
                        ('NEW','IN_REVIEW','DISMISSED','ESCALATED')),
                    note TEXT NOT NULL,
                    reviewer TEXT NOT NULL,
                    revision INTEGER NOT NULL CHECK(revision>=1),
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY(txid, run_sha256)
                );
                CREATE TABLE IF NOT EXISTS events (
                    seq INTEGER PRIMARY KEY AUTOINCREMENT,
                    txid TEXT NOT NULL,
                    run_sha256 TEXT NOT NULL,
                    request_id TEXT NOT NULL UNIQUE,
                    previous_status TEXT NOT NULL,
                    next_status TEXT NOT NULL,
                    note TEXT NOT NULL,
                    reviewer TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    revision INTEGER NOT NULL,
                    previous_hash TEXT NOT NULL,
                    event_hash TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_reviews_status ON reviews(run_sha256,status);
                CREATE INDEX IF NOT EXISTS idx_events_txid ON events(run_sha256,txid,seq);
            """)
            version = int(db.execute("PRAGMA user_version").fetchone()[0])
            if version > 1:
                raise RuntimeError("unsupported future CLARION case database version")
            db.execute("PRAGMA user_version=1")

    def get(self, txid: str, run_sha256: str) -> dict[str, object]:
        with self._connect() as db:
            row = db.execute(
                "SELECT * FROM reviews WHERE txid=? AND run_sha256=?",
                (txid, run_sha256),
            ).fetchone()
            return dict(row) if row is not None else {
                "txid": txid, "run_sha256": run_sha256, "status": "NEW",
                "note": "", "reviewer": "", "revision": 0, "updated_at": None,
            }

    def list(self, run_sha256: str, *, status: str | None = None,
             limit: int = 100, offset: int = 0) -> list[dict[str, object]]:
        if not 1 <= limit <= 500 or offset < 0:
            raise ValueError("invalid pagination")
        if status is not None and status not in TRANSITIONS:
            raise ValueError("invalid status filter")
        with self._connect() as db:
            rows = db.execute(
                "SELECT * FROM reviews WHERE run_sha256=? AND (? IS NULL OR status=?)"
                " ORDER BY updated_at DESC,txid LIMIT ? OFFSET ?",
                (run_sha256, status, status, limit, offset),
            ).fetchall()
            return [dict(row) for row in rows]

    def history(self, txid: str, run_sha256: str, *, limit: int = 100) -> list[dict[str, object]]:
        if not 1 <= limit <= 500:
            raise ValueError("invalid history limit")
        with self._connect() as db:
            rows = db.execute(
                "SELECT * FROM events WHERE txid=? AND run_sha256=? ORDER BY seq DESC LIMIT ?",
                (txid, run_sha256, limit),
            ).fetchall()
            return [dict(row) for row in rows]

    def update(self, *, txid: str, run_sha256: str, status: Status, note: str,
               reviewer: str, expected_revision: int, request_id: str) -> dict[str, object]:
        """Atomic optimistic concurrency + idempotency + append-only hash chain."""
        if status not in TRANSITIONS or not 0 <= expected_revision < 1_000_000:
            raise ValueError("invalid status or revision")
        if not 1 <= len(note.strip()) <= 4000 or not 1 <= len(reviewer) <= 128:
            raise ValueError("explanation and authenticated reviewer required")
        if not 8 <= len(request_id) <= 128:
            raise ValueError("client request ID must be 8..128 characters")
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            duplicate = db.execute(
                "SELECT txid,run_sha256,next_status,note FROM events WHERE request_id=?",
                (request_id,),
            ).fetchone()
            if duplicate:
                if (duplicate["txid"], duplicate["run_sha256"],
                    duplicate["next_status"], duplicate["note"]) != (
                        txid, run_sha256, status, note.strip()):
                    raise ReviewConflict("idempotency key reused for a different review")
                return self.get(txid, run_sha256)
            prev = db.execute(
                "SELECT status,revision FROM reviews WHERE txid=? AND run_sha256=?",
                (txid, run_sha256),
            ).fetchone()
            previous_status = prev["status"] if prev else "NEW"
            current_revision = int(prev["revision"]) if prev else 0
            if expected_revision != current_revision:
                raise ReviewConflict("outdated review version; reload before updating")
            if status not in TRANSITIONS[previous_status]:
                raise ReviewConflict(f"transition {previous_status} -> {status} not permitted")
            timestamp = _stamp()
            revision = current_revision + 1
            last = db.execute("SELECT event_hash FROM events ORDER BY seq DESC LIMIT 1").fetchone()
            before_hash = str(last["event_hash"]) if last else ZERO_HASH
            payload = {
                "txid": txid, "run_sha256": run_sha256, "request_id": request_id,
                "previous_status": previous_status, "next_status": status,
                "note": note.strip(), "reviewer": reviewer, "timestamp": timestamp,
                "revision": revision, "previous_hash": before_hash,
            }
            digest = _hash_event(payload)
            db.execute(
                "INSERT INTO events(txid,run_sha256,request_id,previous_status,"
                "next_status,note,reviewer,timestamp,revision,previous_hash,event_hash)"
                " VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (txid, run_sha256, request_id, previous_status, status, note.strip(),
                 reviewer, timestamp, revision, before_hash, digest),
            )
            db.execute(
                "INSERT INTO reviews(txid,run_sha256,status,note,reviewer,revision,updated_at)"
                " VALUES(?,?,?,?,?,?,?) ON CONFLICT(txid,run_sha256) DO UPDATE SET "
                "status=excluded.status,note=excluded.note,reviewer=excluded.reviewer,"
                "revision=excluded.revision,updated_at=excluded.updated_at",
                (txid, run_sha256, status, note.strip(), reviewer, revision, timestamp),
            )
        return self.get(txid, run_sha256)

    def verify_chain(self) -> dict[str, object]:
        """Check every append-only event's linkage and digest (not an external signature)."""
        with self._connect() as db:
            rows = db.execute("SELECT * FROM events ORDER BY seq").fetchall()
            before = ZERO_HASH
            for row in rows:
                payload = {key: row[key] for key in (
                    "txid", "run_sha256", "request_id", "previous_status",
                    "next_status", "note", "reviewer", "timestamp", "revision",
                    "previous_hash",
                )}
                if row["previous_hash"] != before or _hash_event(payload) != row["event_hash"]:
                    return {"valid": False, "events_checked": row["seq"] - 1,
                            "failure_seq": row["seq"]}
                before = str(row["event_hash"])
            return {"valid": True, "events_checked": len(rows), "last_hash": before}
