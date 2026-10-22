"""Real FastAPI routes, auth refusal and hash check with fictional artifacts."""
from __future__ import annotations

import hashlib
import json
import secrets
from uuid import uuid4

from fastapi.testclient import TestClient

from clarion.api.main import create_app

TXID = "a" * 64
TOKEN = secrets.token_urlsafe(32)


def setup_run(folder):
    folder.mkdir(exist_ok=True)
    lead = {"txid": TXID, "priority": "P3", "risk_points": 23.0,
            "propagation_points": 1.0, "delta": {"status": "ABSTAIN"},
            "pi": {"status": "ABSTAIN"}}
    (folder / "leads.json").write_text(json.dumps([lead]), encoding="utf-8")
    (folder / "graph.json").write_text(json.dumps({"nodes": [], "edges": []}), encoding="utf-8")
    manifest = {"status": "UNVALIDATED", "readiness": {"mode": "CHAIN_ONLY"},
                "audit_sha256": {"graph.json": hashlib.sha256(
                    (folder / "graph.json").read_bytes()).hexdigest()}}
    (folder / "run_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


def test_no_unauthenticated_review_writes(tmp_path, monkeypatch):
    setup_run(tmp_path)
    monkeypatch.delenv("CLARION_REVIEW_TOKEN", raising=False)
    client = TestClient(create_app(tmp_path))
    assert client.get("/api/cases/" + TXID).status_code == 200
    assert client.post("/api/cases/" + TXID + "/review", json={
        "status": "IN_REVIEW", "note": "Independent review",
        "expected_revision": 0, "request_id": str(uuid4()),
    }).status_code == 503


def test_local_review_persists_and_rechecks_manifest(tmp_path, monkeypatch):
    setup_run(tmp_path)
    monkeypatch.setenv("CLARION_REVIEW_TOKEN", TOKEN)
    client = TestClient(create_app(tmp_path))
    body = {"status": "IN_REVIEW", "note": "Investigative candidate, not accusation",
            "expected_revision": 0, "request_id": str(uuid4())}
    assert client.post("/api/cases/" + TXID + "/review", json=body).status_code == 401
    response = client.post("/api/cases/" + TXID + "/review",
                           headers={"X-CLARION-REVIEW-TOKEN": TOKEN}, json=body)
    assert response.status_code == 200
    assert response.json()["revision"] == 1
    assert client.get("/api/cases/audit").json()["valid"] is True
    assert len(client.get("/api/cases/" + TXID + "/history").json()) == 1
    assert client.get("/api/provenance/verify").json()["valid"] is True
    assert client.get("/api/graph/neighborhood", params={"txid": TXID}).status_code == 200
    (tmp_path / "graph.json").write_text('{"nodes":[],"edges":[1]}', encoding="utf-8")
    assert client.get("/api/provenance/verify").json()["valid"] is False
    assert client.get("/api/graph/neighborhood", params={"txid": TXID}).status_code == 422
    assert TestClient(create_app(tmp_path)).get("/api/cases/" + TXID).json()["review"]["revision"] == 1


def test_case_rejects_forged_txid(tmp_path):
    setup_run(tmp_path)
    client = TestClient(create_app(tmp_path))
    assert client.get("/api/cases/" + "b" * 64).status_code == 404
    assert client.get("/api/cases/not-a-txid").status_code == 422
