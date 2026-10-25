"""Submission tests without GPU, internet, MLflow or untrusted model files."""
import json

import pytest

from clarion.v4.mlops_adapter import log_local_experiment
from clarion.v4.submission import inspect_run, model_readiness


def test_unconfigured_model_is_explicit():
    assert model_readiness()["status"] == "MODEL_NOT_CONFIGURED"


def test_pickle_placeholder_cannot_be_used(tmp_path):
    fake = tmp_path / "fake.pkl"
    fake.write_bytes(b"not a real model")
    assert model_readiness(fake)["status"] == "UNSUPPORTED_MODEL_FORMAT"


def _write_minimal(tmp_path, *, score=13.0, relation="spends_outpoint"):
    run = tmp_path / "run"
    run.mkdir()
    (run / "run_manifest.json").write_text(json.dumps({"kind": "EVIDENCE_FIRST_UNSUPERVISED_V4", "n_leads": 1}))
    (run / "graph.json").write_text(json.dumps({"nodes": [{"id": "tx:a"}], "edges": [{"relation": relation}]}))
    (run / "leads.json").write_text(json.dumps([{
        "local_seed_points": 10, "propagation_points": 3, "risk_points": score,
        "score_type": "UNSUPERVISED_RANK_NOT_PROBABILITY",
        "delta": {"status": "ABSTAIN"}, "pi": {"status": "ABSTAIN"},
    }]))
    return run


def test_inspector_validates_demo_contract(tmp_path):
    report = inspect_run(_write_minimal(tmp_path))
    assert report["result"] == "VALIDATED_DEMO_ARTIFACT_CONTRACT"
    assert report["lead_count"] == 1


def test_inspector_rejects_risk_inflation(tmp_path):
    with pytest.raises(ValueError, match="propagation"):
        inspect_run(_write_minimal(tmp_path, score=14))


def test_inspector_rejects_wallet_ip_owner_edge(tmp_path):
    with pytest.raises(ValueError, match="ownership"):
        inspect_run(_write_minimal(tmp_path, relation="wallet_owner"))


def test_invalid_metric_rejected(tmp_path):
    with pytest.raises(ValueError, match="nonfinite"):
        log_local_experiment({"future_AUROC": float("nan")}, destination=tmp_path)


def test_mlops_json_record_exists_even_without_mlflow(tmp_path):
    report = log_local_experiment({"synthetic_lead_count": 10.0}, destination=tmp_path)
    assert (tmp_path / "experiment.json").is_file()
    assert report["status"].endswith("RECORDED") or "RECORDED_JSON" in report["status"]
