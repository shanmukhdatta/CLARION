"""Local case-management routes mounted under the immutable run-file API.

Write operations require an explicitly configured secret; there is no default
password and there is no network-facing/multi-tenant identity platform here.
"""
from __future__ import annotations

import hashlib
import hmac
import os
import re
from pathlib import Path
from typing import Any, Literal
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field

from clarion.v4.case_store import CaseStore, ReviewConflict

HEX_TXID = re.compile(r"^[0-9a-f]{64}$")


class ReviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Literal["NEW", "IN_REVIEW", "DISMISSED", "ESCALATED"]
    note: str = Field(min_length=1, max_length=4000)
    expected_revision: int = Field(ge=0)
    request_id: UUID


def attach_review_routes(
    router: APIRouter, run_dir: Path,
    read_file: Any,
) -> None:
    """Register real HTTP routes with a persistent SQLite transaction backend."""
    store = CaseStore(run_dir / ".clarion_reviews.sqlite3")

    def validate_txid(txid: str) -> str:
        if not HEX_TXID.fullmatch(txid):
            raise HTTPException(422, "expected 64 lowercase-hex transaction ID")
        return txid

    def locate(txid: str) -> dict[str, Any]:
        validate_txid(txid)
        for lead in read_file("leads.json"):
            if lead.get("txid") == txid:
                return lead
        raise HTTPException(404, "transaction lead not in this run")

    def run_sha() -> str:
        name = run_dir / "run_manifest.json"
        if not name.is_file():
            raise HTTPException(404, "run manifest is absent")
        return hashlib.sha256(name.read_bytes()).hexdigest()

    def authorized(secret: str | None) -> str:
        expected = os.environ.get("CLARION_REVIEW_TOKEN", "")
        if len(expected) < 24:
            raise HTTPException(503, "review writes disabled: configure CLARION_REVIEW_TOKEN")
        if not secret or not hmac.compare_digest(expected, secret):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "reviewer token required")
        return os.environ.get("CLARION_REVIEWER_ID", "local_operator")

    @router.get("/api/cases")
    def list_cases(
        status_filter: Literal["NEW", "IN_REVIEW", "DISMISSED", "ESCALATED"] | None = None,
        limit: int = Query(100, ge=1, le=500),
        offset: int = Query(0, ge=0),
    ) -> list[dict[str, object]]:
        return store.list(run_sha(), status=status_filter, limit=limit, offset=offset)

    @router.get("/api/cases/audit")
    def audit() -> dict[str, object]:
        return store.verify_chain()

    @router.get("/api/cases/{txid}")
    def get_case(txid: str) -> dict[str, object]:
        lead = locate(txid)
        return {"lead": lead, "review": store.get(txid, run_sha())}

    @router.get("/api/cases/{txid}/history")
    def history(txid: str, limit: int = Query(100, ge=1, le=500)) -> list[dict[str, object]]:
        locate(txid)
        return store.history(txid, run_sha(), limit=limit)

    @router.post("/api/cases/{txid}/review")
    def review_case(
        txid: str, body: ReviewRequest,
        x_clarion_review_token: str | None = Header(default=None),
    ) -> dict[str, object]:
        reviewer = authorized(x_clarion_review_token)
        locate(txid)
        try:
            return store.update(
                txid=txid, run_sha256=run_sha(), status=body.status,
                note=body.note, reviewer=reviewer,
                expected_revision=body.expected_revision,
                request_id=str(body.request_id),
            )
        except ReviewConflict as exc:
            raise HTTPException(409, str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
