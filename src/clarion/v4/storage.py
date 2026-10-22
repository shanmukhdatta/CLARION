"""Optional local Parquet/DuckDB storage and SQLite case index.

Parquet files are rebuildable from verified canonical data; no cloud dependencies.
DuckDB reads local Parquet only. SQLite stores user-reviewed case metadata.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any, Iterable

from clarion.v4.contracts import Snapshot


def parquet_snapshot(snapshot: Snapshot, destination: str | Path) -> dict[str, str]:
    import pyarrow as pa
    import pyarrow.parquet as pq

    directory = Path(destination)
    directory.mkdir(parents=True, exist_ok=True)
    collection = {
        "transactions": snapshot.transactions,
        "inputs": snapshot.inputs,
        "outputs": snapshot.outputs,
        "wire_observations": snapshot.wire,
        "evidence_edges": snapshot.edges,
    }
    hashes = {}
    for name, records in collection.items():
        rows = [r.model_dump(mode="json") for r in records]
        # A stable empty table is represented as a manifest entry, not a malformed file.
        if not rows:
            continue
        path = directory / (name + ".parquet")
        pq.write_table(pa.Table.from_pylist(rows), path, compression="zstd")
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    (directory / "parquet_manifest.json").write_text(
        json.dumps({"source_hashes": snapshot.source_hashes,
                    "parquet_hashes": hashes, "cutoff": snapshot.cutoff.isoformat()},
                   indent=2, sort_keys=True), encoding="utf-8")
    return hashes


def query_parquet_local(path: str | Path, *, limit: int = 100) -> list[dict[str, Any]]:
    if not (1 <= limit <= 5000):
        raise ValueError("limit out of bounds")
    import duckdb
    filepath = Path(path).resolve()
    if filepath.suffix != ".parquet" or not filepath.is_file():
        raise ValueError("only existing .parquet local files permitted")
    # Parameter binding for filename, no arbitrary user SQL.
    connection = duckdb.connect(database=":memory:")
    try:
        result = connection.execute(
            "SELECT * FROM read_parquet(?) LIMIT ?", [str(filepath), limit],
        )
        columns = [d[0] for d in result.description]
        return [dict(zip(columns, row, strict=True)) for row in result.fetchall()]
    finally:
        connection.close()


def init_case_db(path: str | Path) -> None:
    filename = Path(path)
    filename.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(filename) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS case_review (
                case_id TEXT PRIMARY KEY,
                subject_id TEXT NOT NULL,
                status TEXT NOT NULL
                    CHECK(status IN ('NEW','IN_REVIEW','DISMISSED','ESCALATED')),
                reviewer TEXT NOT NULL,
                rationale TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                run_hash TEXT NOT NULL
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS review_audit (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT NOT NULL,
                prev_status TEXT,
                new_status TEXT NOT NULL,
                reviewer TEXT NOT NULL,
                changed_at TEXT NOT NULL
            )
        """)


def record_case_review(
    path: str | Path, *, case_id: str, subject_id: str,
    status: str, reviewer: str, rationale: str, updated_at: str,
    run_hash: str,
) -> None:
    if status not in ("NEW", "IN_REVIEW", "DISMISSED", "ESCALATED"):
        raise ValueError("invalid review state")
    if not case_id or not reviewer or not rationale or len(rationale) > 4000:
        raise ValueError("case review requires identity and rationale")
    with sqlite3.connect(path) as con:
        prev = con.execute(
            "SELECT status FROM case_review WHERE case_id=?", (case_id,),
        ).fetchone()
        con.execute("""
            INSERT INTO case_review VALUES (?,?,?,?,?,?,?)
            ON CONFLICT(case_id) DO UPDATE SET
                status=excluded.status, reviewer=excluded.reviewer,
                rationale=excluded.rationale, updated_at=excluded.updated_at,
                run_hash=excluded.run_hash
        """, (case_id, subject_id, status, reviewer, rationale, updated_at, run_hash))
        con.execute(
            "INSERT INTO review_audit(case_id,prev_status,new_status,reviewer,changed_at) VALUES (?,?,?,?,?)",
            (case_id, prev[0] if prev else None, status, reviewer, updated_at),
        )
