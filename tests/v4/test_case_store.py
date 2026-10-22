"""Persistent review transitions, concurrency and audit chain checks."""
from __future__ import annotations

import sqlite3

import pytest

from clarion.v4.case_store import CaseStore, ReviewConflict

TXID = "a" * 64
RUN = "b" * 64


def update(store, status, *, rev=0, key="request-id-0001", note="Analyst reviewed evidence"):
    return store.update(
        txid=TXID, run_sha256=RUN, status=status, note=note,
        reviewer="offline_review_operator", expected_revision=rev, request_id=key,
    )


def test_transition_and_immutable_history(tmp_path):
    db = CaseStore(tmp_path / "review.sqlite3")
    assert db.get(TXID, RUN)["status"] == "NEW"
    first = update(db, "IN_REVIEW")
    assert first["revision"] == 1
    assert first["status"] == "IN_REVIEW"
    second = update(db, "DISMISSED", rev=1, key="request-id-0002",
                    note="Documented legitimate alternative")
    assert second["revision"] == 2
    assert db.list(RUN, status="DISMISSED")[0]["txid"] == TXID
    assert len(db.history(TXID, RUN)) == 2
    assert db.verify_chain()["valid"] is True
    assert CaseStore(tmp_path / "review.sqlite3").get(TXID, RUN)["status"] == "DISMISSED"


def test_idempotency_and_concurrency(tmp_path):
    db = CaseStore(tmp_path / "reviews.db")
    original = update(db, "IN_REVIEW")
    repeated = update(db, "IN_REVIEW")
    assert original == repeated
    assert db.verify_chain()["events_checked"] == 1
    with pytest.raises(ReviewConflict, match="reused"):
        update(db, "DISMISSED", rev=1)
    with pytest.raises(ReviewConflict, match="outdated"):
        update(db, "DISMISSED", rev=0, key="new-request-0002")
    with pytest.raises(ReviewConflict, match="not permitted"):
        update(db, "NEW", rev=1, key="new-request-0003")


def test_audit_tamper_detection(tmp_path):
    db = CaseStore(tmp_path / "review.sqlite3")
    update(db, "IN_REVIEW")
    with sqlite3.connect(db.path) as con:
        con.execute("UPDATE events SET note='changed' WHERE seq=1")
    assert db.verify_chain()["valid"] is False


def test_manifest_version_scopes_reviews(tmp_path):
    db = CaseStore(tmp_path / "review.sqlite3")
    update(db, "IN_REVIEW")
    assert db.get(TXID, "c" * 64)["status"] == "NEW"
    assert db.list("c" * 64) == []
