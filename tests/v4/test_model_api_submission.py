"""Local model API readiness, no arbitrary artifact or implied crime probability."""
from __future__ import annotations

from fastapi.testclient import TestClient

from clarion.api.main import create_app


def test_missing_model_readiness_is_explicit(tmp_path, monkeypatch):
    monkeypatch.delenv("CLARION_MODEL_ARTIFACT", raising=False)
    client = TestClient(create_app(tmp_path))
    reply = client.get("/api/models/readiness")
    assert reply.status_code == 200
    assert reply.json()["status"] == "MODEL_NOT_CONFIGURED"


def test_fake_pickle_never_loaded(tmp_path, monkeypatch):
    fake = tmp_path / "fake.pkl"
    fake.write_bytes(b"not executable or trusted")
    monkeypatch.setenv("CLARION_MODEL_ARTIFACT", str(fake))
    client = TestClient(create_app(tmp_path))
    assert client.get("/api/models/readiness").json()["status"] == "UNSUPPORTED_MODEL_FORMAT"
    response = client.get("/api/models/experimental/" + "a" * 64)
    assert response.status_code == 409


def test_inference_endpoint_rejects_invalid_id(tmp_path, monkeypatch):
    monkeypatch.delenv("CLARION_MODEL_ARTIFACT", raising=False)
    client = TestClient(create_app(tmp_path))
    assert client.get("/api/models/experimental/not-a-txid").status_code == 422
