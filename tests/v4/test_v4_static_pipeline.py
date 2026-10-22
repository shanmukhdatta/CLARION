"""Focused v4 correctness contracts. Authored statically; NOT EXECUTED in this pass."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from clarion.v4.analysis import final_priority, mcer_candidates, propagate
from clarion.v4.contracts import Input, Output, Tx, WireObservation
from clarion.v4.graph import build_snapshot, feature_rows
from clarion.v4.ingest import btc_to_sats
from clarion.v4.signals import VerifiedEconomicGoal, delta_signal, pi_signal

NOW = datetime(2025, 1, 1, tzinfo=UTC)
A, B, C = "a"*64, "b"*64, "c"*64


def ledger():
    tx = [
        Tx(txid=A,event_time=NOW,available_at=NOW,source_id="fixture",coinbase=True),
        Tx(txid=B,event_time=NOW+timedelta(seconds=60),
           available_at=NOW+timedelta(seconds=60),source_id="fixture",
           fee_sats=1000,vbytes=125),
    ]
    inputs = [Input(txid=B,vin=0,prev_txid=A,prev_vout=0,source_id="fixture")]
    outputs = [
        Output(txid=A,vout=0,value_sats=100000,address="alpha",source_id="fixture"),
        Output(txid=B,vout=0,value_sats=90000,address="bravo",source_id="fixture"),
        Output(txid=B,vout=1,value_sats=9000,address="charlie",source_id="fixture"),
    ]
    return tx, inputs, outputs


def snap():
    t,i,o=ledger()
    return build_snapshot(t,i,o,cutoff=NOW+timedelta(seconds=100))


def test_precise_btc_units():
    assert btc_to_sats("0.00000001")==1
    with pytest.raises(ValueError):
        btc_to_sats("0.000000001")


def test_timezone_required():
    with pytest.raises(ValidationError):
        Tx(txid=A,event_time=datetime(2025,1,1),available_at=NOW,source_id="x")


def test_utxo_edge_and_conservation():
    snapshot=snap()
    transfers=[e for e in snapshot.edges if e.relation=="spends_outpoint"]
    assert len(transfers)==1
    assert transfers[0].amount_sats==100_000
    assert transfers[0].source=="tx:"+A
    assert transfers[0].target=="tx:"+B


def test_future_is_invisible():
    t,i,o=ledger()
    early=build_snapshot(t,i,o,cutoff=NOW+timedelta(seconds=30))
    assert len(early.transactions)==1
    assert not any(e.relation=="spends_outpoint" for e in early.edges)


def test_duplicate_txid_rejected():
    t,i,o=ledger()
    with pytest.raises(ValueError,match="duplicate TXIDs"):
        build_snapshot(t+[t[0]],i,o,cutoff=NOW+timedelta(seconds=100))


def test_value_conservation_violation():
    t,i,o=ledger()
    o[-1]=Output(txid=B,vout=1,value_sats=9999,address="charlie",source_id="fixture")
    with pytest.raises(ValueError,match="conservation"):
        build_snapshot(t,i,o,cutoff=NOW+timedelta(seconds=100))


def test_observed_wire_never_implies_wallet_ownership():
    t,i,o=ledger()
    observation=WireObservation(
        observation_id="obs1",sensor_id="s1",host="192.0.2.17",txid=B,
        event_time=NOW+timedelta(seconds=65),
        available_at=NOW+timedelta(seconds=65),
        decode_provenance="observed_inv",clock_uncertainty_ms=20,source_id="fixture"
    )
    data=build_snapshot(t,i,o,[observation],cutoff=NOW+timedelta(seconds=100))
    assert any(e.relation=="observed_relay" for e in data.edges)
    assert not any("ownership" in e.relation or e.source.startswith("host:") and e.target.startswith("addr:")
                   for e in data.edges)
    assert data.readiness.mode.value=="CHAIN_ONLY"


def test_no_coinjoin_auto_merge_and_singles():
    assert mcer_candidates(snap())==[]


def test_priority_cap():
    assert final_priority(75,25)==100
    with pytest.raises(ValueError):
        final_priority(80,21)


def test_propagation_is_chain_only():
    data=snap()
    result=propagate(data,{A:75.0},max_hops=6)
    assert 0<=result["propagation_prior"][B]<=25
    assert all(not node.startswith("host:") for node in result["propagation_prior"])


def test_delta_and_pi_abstain_without_validated_premise():
    assert delta_signal([]).status=="ABSTAIN"
    assert pi_signal(VerifiedEconomicGoal(
        goal_id="unknown",fee_sats=100,hops=None,duration_seconds=None,
        outputs=None,infra_cost_sats=None,baseline_fee_sats=None,baseline_hops=None,
        baseline_duration_seconds=None,baseline_outputs=None,
        baseline_infra_cost_sats=None,
    )).status=="ABSTAIN"


def test_features_historical_only():
    data=snap()
    rows=feature_rows(data)
    assert len(rows)==1
    assert rows[0]["subject_id"]==B
    assert rows[0]["age_seconds"]==60.0


def test_source_reference_attached():
    data=snap()
    for edge in data.edges:
        assert edge.evidence_ref and edge.source_id and edge.available_at<=data.cutoff
