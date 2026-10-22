from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

pytest.importorskip("sklearn")
pytest.importorskip("fastapi")
pytest.importorskip("httpx")
from fastapi.testclient import TestClient

from clarion.application.engine import generate, investigate, load, motifs, risk_propagation
from clarion.application.training_demo import train
from clarion.api.main import create_app
from clarion.cli.main import main


@pytest.fixture
def demo(tmp_path: Path) -> Path:
    source = tmp_path / "demo"
    generate(source, cases=36, seed=26)
    return source


def _rewrite_csv(path: Path, transform) -> None:
    with path.open(encoding="utf-8", newline="") as file:
        records = list(csv.DictReader(file))
        fields = list(records[0])
    transform(records)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)


def test_generator_deterministic(demo: Path, tmp_path: Path) -> None:
    second = tmp_path / "second"
    generate(second, cases=36, seed=26)
    for filename in ("transactions.csv", "inputs.csv", "outputs.csv", "observations.csv"):
        assert (second / filename).read_bytes() == (demo / filename).read_bytes()
    assert len(load(demo)["features"]) == 108


def test_value_conservation_and_exact_prevout(demo: Path) -> None:
    data = load(demo)
    assert len(data["links"]) == len(data["features"])
    assert all(len(edge["outpoint"].split(":")) == 2 for edge in data["links"])
    assert all(e["type"] == "observed-relay" for e in data["wire"])


def test_corrupted_value_rejected(demo: Path) -> None:
    _rewrite_csv(demo / "outputs.csv", lambda rows: rows[1].update(value_sats="99"))
    with pytest.raises(ValueError, match="UTXO conservation failed"):
        load(demo)


def test_double_spend_rejected(demo: Path) -> None:
    def corrupt(rows):
        rows[1]["prev_txid"] = rows[0]["prev_txid"]
        rows[1]["prev_vout"] = rows[0]["prev_vout"]
    _rewrite_csv(demo / "inputs.csv", corrupt)
    with pytest.raises(ValueError, match="duplicate prevout spend"):
        load(demo)


def test_bad_timezone_rejected(demo: Path) -> None:
    _rewrite_csv(demo / "transactions.csv", lambda rows: rows[0].update(time="2025-01-01T12:00:00"))
    with pytest.raises(ValueError, match="timezone"):
        load(demo)


def test_future_cutoff_does_not_reveal_later_transactions(demo: Path) -> None:
    original = load(demo)
    cutoff = original["transactions"][30]["time"]
    earlier = load(demo, __import__("datetime").datetime.fromisoformat(cutoff))
    assert len(earlier["transactions"]) <= len(original["transactions"])
    assert len(earlier["features"]) < len(original["features"])
    assert all(row["time"] <= cutoff for row in earlier["transactions"])


def test_motifs_have_factual_evidence_and_benign_alternative(demo: Path) -> None:
    snapshot = load(demo)
    known = {t["txid"] for t in snapshot["transactions"]}
    for motif in motifs(snapshot):
        assert all(t in known for t in motif["witness_txids"])
        assert motif["benign_alternative"]


def test_propagation_never_uses_host_or_exceeds_cap(demo: Path) -> None:
    snapshot = load(demo)
    tx = snapshot["features"][0]["txid"]
    p = risk_propagation(snapshot, {tx: 95., "host:192.0.2.1": 100.})
    assert all(point <= 25. for point in p["points"].values())
    assert all(not key.startswith("host:") for key in p["points"])
    assert p["seed_count"] == 2  # one host seed is inert, cannot taint finance


def test_wire_never_proves_owner(demo: Path, tmp_path: Path) -> None:
    target = tmp_path / "run"
    investigate(demo, target)
    graph = json.loads((target / "graph.json").read_text())
    assert not any("owner" in edge["type"] for edge in graph["edges"])
    assert not any(row.get("label") is not None for row in json.loads((target / "leads.json").read_text()))


def test_train_is_chronological_grouped(demo: Path, tmp_path: Path) -> None:
    report = train(demo, tmp_path / "trained")
    assert report["metrics"]["future_cases"] > 0
    assert report["metrics"]["oof_samples"] > 0
    assert report["metrics"]["training_samples"] + report["metrics"]["future_samples"] == 108
    assert report["not_real_world_validation"] is True


def test_dossier_abstentions_and_bounds(demo: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    manifest = investigate(demo, out)
    assert manifest["status"] == "DEMO_CHAIN_ONLY"
    leads = json.loads((out / "leads.json").read_text())
    assert leads
    assert all(row["delta"]["status"] == row["pi"]["status"] == "ABSTAIN" for row in leads)
    assert all(0 <= row["propagation_points"] <= 25 and 0 <= row["risk_points"] <= 100 for row in leads)


def test_api_loopback_readonly(demo: Path, tmp_path: Path) -> None:
    out = tmp_path / "run"
    investigate(demo, out)
    client = TestClient(create_app(out))
    assert client.get("/").status_code == 200
    assert client.get("/api/manifest").json()["status"] == "DEMO_CHAIN_ONLY"
    assert len(client.get("/api/leads?limit=2").json()) == 2
    assert client.get("/api/leads?limit=1001").status_code == 422
    assert client.post("/api/leads").status_code == 405


def test_cli_entry(capsys) -> None:
    assert main([]) == 0
    assert "usage: clarion" in capsys.readouterr().out
    with pytest.raises(SystemExit) as exc:
        main(["--bad-option"])
    assert exc.value.code == 2
