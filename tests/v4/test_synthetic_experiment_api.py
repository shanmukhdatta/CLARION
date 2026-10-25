"""Synthetic training experimental results are optional and must not be spoofed."""
from __future__ import annotations

import json

from fastapi.testclient import TestClient

from clarion.api.main import create_app


def test_no_training_report_returns_404(tmp_path):
    client = TestClient(create_app(tmp_path))
    assert client.get("/api/experiments/demo").status_code == 404


def test_training_report_is_local_only(tmp_path):
    (tmp_path / "training_experiment.json").write_text(
        json.dumps({"training_status": "SYNTHETIC_EXPERIMENT_ONLY",
                    "model_status": "NO_CALIBRATED_DEPLOYED_MODEL",
                    "metrics_synthetic_only": {"future_samples": 15}}))
    client = TestClient(create_app(tmp_path))
    result = client.get("/api/experiments/demo")
    assert result.status_code == 200
    assert result.json()["metrics_synthetic_only"]["future_samples"] == 15
