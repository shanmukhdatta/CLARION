"""Real verified evidence contracts for relay sessions, structural motifs and model serialization."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from clarion.v4.contracts import Input, Output, Tx, WireObservation
from clarion.v4.graph import build_snapshot
from clarion.v4.model_artifact import fit_json_logistic, predict_json_logistic
from clarion.v4.monitoring import population_stability_index
from clarion.v4.motifs_extended import additional_motifs
from clarion.v4.wire_sessions import build_sessions, wire_feature_rows

T = datetime(2025, 1, 1, tzinfo=UTC)
A = "a" * 64
B = "b" * 64


def test_sessions_dedupe_and_provenance():
    records = [
        WireObservation(
            observation_id="1", sensor_id="s1", host="192.0.2.21",
            event_time=T, available_at=T, txid=A, decode_provenance="observed_tx",
            clock_uncertainty_ms=20, source_id="fixture",
            source_port=8333, destination_port=41567,
        ),
        WireObservation(
            observation_id="duplicate", sensor_id="s1", host="192.0.2.21",
            event_time=T, available_at=T, txid=A, decode_provenance="observed_tx",
            clock_uncertainty_ms=20, source_id="fixture",
        ),
        WireObservation(
            observation_id="later", sensor_id="s1", host="192.0.2.21",
            event_time=T + timedelta(seconds=10), available_at=T + timedelta(seconds=10),
            txid=B, decode_provenance="observed_inv",
            clock_uncertainty_ms=20, source_id="fixture",
        ),
        WireObservation(
            observation_id="another", sensor_id="s2", host="192.0.2.21",
            event_time=T, available_at=T, txid=A, decode_provenance="observed_tx",
            clock_uncertainty_ms=20, source_id="fixture",
        ),
    ]
    sessions = build_sessions(records, cutoff=T + timedelta(minutes=3))
    assert len(sessions) == 2
    assert sessions[0].event_count == 2
    assert sessions[0].port_entropy is not None
    feature = wire_feature_rows(records, cutoff=T)
    assert feature[0]["unique_sensors"] == 2
    assert feature[0]["claim"] == "OBSERVED_RELAY_ONLY_NOT_ORIGIN_OR_WALLET"


def test_no_false_layering_in_simple_chain():
    txs = [
        Tx(txid=A, event_time=T, available_at=T, coinbase=True, source_id="x"),
        Tx(txid=B, event_time=T + timedelta(minutes=1),
           available_at=T + timedelta(minutes=1), fee_sats=0, source_id="x"),
    ]
    inp = [Input(txid=B, vin=0, prev_txid=A, prev_vout=0, source_id="x")]
    outs = [Output(txid=A, vout=0, value_sats=10000, address="alpha", source_id="x"),
            Output(txid=B, vout=0, value_sats=10000, address="beta", source_id="x")]
    snap = build_snapshot(txs, inp, outs, cutoff=T + timedelta(minutes=2))
    assert additional_motifs(snap) == []


def test_json_model_train_predict_and_tamper_guard():
    rows = []
    labels = {}
    for i in range(100):
        stamp = (T + timedelta(minutes=i)).isoformat()
        tid = f"{i:064x}"
        rows.append({
            "subject_id": tid, "available_at": stamp,
            "inputs": 1 + (i % 2), "outputs": 2 + (i % 3),
            "output_sats": 10000 + i * 700, "fee_rate": float(i % 5),
            "largest_output_share": 0.75 + 0.01 * (i % 3),
            "min_output_share": 0.1,
            "age_seconds": 60 + i, "unresolved_prevout": False,
        })
        labels[tid] = (int(i % 2), stamp)
    artifact, report = fit_json_logistic(
        rows, labels, source_hashes={"synthetic": "0" * 64},
        evaluation_time=rows[-1]["available_at"],
    )
    assert report["holdout_count"] == 20
    preds = predict_json_logistic(artifact, rows[-20:])
    assert len(preds) == 20
    assert all(0 <= p["score"] <= 1 for p in preds)
    artifact["coef"][0] += 1
    with pytest.raises(ValueError, match="digest"):
        predict_json_logistic(artifact, rows[-20:])


def test_psi_diagnostic_is_not_guilt_score():
    result = population_stability_index([i / 100 for i in range(100)],
                                        [i / 90 for i in range(100)])
    assert result["status"] == "MEASURED_NOT_CAUSAL"
    assert result["value"] >= 0
