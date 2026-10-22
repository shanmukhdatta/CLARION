"""CLARION v4 deterministic local evidence pipeline. No network I/O.

Canonical CSV/JSON/XML -> validation/quarantine -> as-of graph -> features ->
unverified candidate MCER/motifs -> unsupervised rank -> freeze seed -> directed
propagation -> bounded two-pass priority -> audit/report. Optional independently
validated supervised scores can be supplied ONLY with a recorded score-type gate.
"""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from clarion.v4.analysis import (
    final_priority,
    local_priority,
    pattern_candidates,
    propagate,
)
from clarion.v4.contracts import utc
from clarion.v4.graph import build_snapshot, feature_rows, graph_export
from clarion.v4.ingest import import_canonical
from clarion.v4.mcer import conservative_partition, h1_common_inputs, h2_change_hypotheses
from clarion.v4.ml import fit_temporal_stack, novelty_ranking
from clarion.v4.monitoring import source_quality_report
from clarion.v4.motifs_extended import additional_motifs
from clarion.v4.wire_sessions import build_sessions, wire_feature_rows


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, sort_keys=True, indent=2, allow_nan=False, default=str) + "\n", encoding="utf-8")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            clean = {k: ("'" + value if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")) else value)
                     for k, value in row.items()}
            writer.writerow(clean)


def run(
    data_dir: str | Path, out_dir: str | Path, *,
    licence: str, origin: str, cutoff: datetime | None = None,
    labelled: bool = False, min_join_coverage: float | None = None,
    max_clock_uncertainty_ms: int | None = None,
    blocked_transactions: set[str] | None = None,
) -> dict[str, Any]:
    """Produce a fully local, auditable *unsupervised lead* run.

    The labeled flag means labels exist for evaluation; it never authorizes
    pretending an unvalidated model is calibrated. Runtime uses novelty ranks.
    """
    source = import_canonical(
        data_dir, licence=licence, origin=origin,
        kind="canonical", include_labels=labelled,
    )
    maximum = max((t.available_at for t in source.transactions), default=None)
    if maximum is None:
        raise ValueError("No valid transaction rows; consult quarantine")
    when = utc(cutoff or maximum)
    valid_labels = [
        x for x in source.labels if x.available_at <= when and x.subject_type == "transaction"
    ]
    snapshot = build_snapshot(
        source.transactions, source.inputs, source.outputs, source.wire, cutoff=when,
        source_hashes=source.hashes, labels_available=bool(valid_labels),
        min_join_coverage=min_join_coverage,
        max_clock_uncertainty_ms=max_clock_uncertainty_ms,
    )
    features = feature_rows(snapshot)
    patterns = pattern_candidates(snapshot) + additional_motifs(snapshot)
    # MCER H1/H2 evidence is captured, but candidates merge only with
    # independently sourced positive witnesses and no hard service conflicts.
    signed_evidence = h1_common_inputs(snapshot) + h2_change_hypotheses(snapshot)
    partition = conservative_partition(signed_evidence, cutoff=snapshot.cutoff)
    entities = [
        {"entity_id": "entity:" + partition.version_id.removeprefix("mcer:") + f":{index}",
         "members": list(group), "status": "TENTATIVE_INDEPENDENT_EVIDENCE",
         "support": [
             entry.evidence_ref for entry in signed_evidence
             if entry.left in group and entry.right in group and entry.sign == "support"
         ], "version_id": partition.version_id}
        for index, group in enumerate(partition.candidates)
    ]
    sessions = build_sessions(snapshot.wire, cutoff=snapshot.cutoff)
    wire_features = wire_feature_rows(snapshot.wire, cutoff=snapshot.cutoff)
    pattern_count: Counter[str] = Counter(str(p["subject_id"]) for p in patterns)
    if len(features) >= 10:
        novelty = {str(row["subject_id"]): float(row["novelty_rank"])
                   for row in novelty_ranking(features)}
    else:
        novelty = {}
    provisional = {
        str(row["subject_id"]): local_priority(
            str(row["subject_id"]), supervised_score=None,
            anomaly_rank=novelty.get(str(row["subject_id"])),
            motif_count=pattern_count[str(row["subject_id"])],
            delta=None, pi=None,
        ) for row in features
    }
    frozen = {tid: float(v["local_points"]) for tid, v in provisional.items()}
    propagated = propagate(snapshot, frozen, max_hops=6,
                           blocked_transactions=blocked_transactions)
    priors: dict[str, float] = propagated["propagation_prior"]  # type: ignore[assignment]
    evidence = {
        "transaction_index": {t.txid: t for t in snapshot.transactions},
        "motifs_by_subject": {tid: [p for p in patterns if p["subject_id"] == tid]
                              for tid in provisional},
    }
    leads = []
    for row in features:
        tid = str(row["subject_id"])
        local = provisional[tid]
        local_points = float(local["local_points"])
        propagation = float(priors.get(tid, 0.0))
        score = final_priority(local_points, propagation)
        priority = "P1" if score >= 85 else "P2" if score >= 65 else "P3" if score >= 35 else "P4"
        leads.append({
            "txid": tid, "subject_id": tid, "time": row["event_time"],
            "case_id": None, "priority": priority, "risk_points": score,
            "local_seed_points": local_points, "propagation_points": propagation,
            "explanation": {"novelty_rank": novelty.get(tid), "motifs": pattern_count[tid],
                            "terms": local["terms"], "local_score": local_points},
            "delta": {"status": "ABSTAIN", "reason": "independent chain-wire dependence and case-level Δ not verified"},
            "pi": {"status": "ABSTAIN", "reason": "controlled same-goal economic baseline absent"},
            "witness_path": (propagated["top_paths"]).get(tid, []),
            "source_id": evidence["transaction_index"][tid].source_id,
            "evidence_refs": [p["evidence_refs"] for p in evidence["motifs_by_subject"][tid]],
            "score_type": "UNSUPERVISED_RANK_NOT_PROBABILITY",
        })
    leads.sort(key=lambda x: (-float(x["risk_points"]), str(x["txid"])))
    graph = graph_export(snapshot)
    folder = Path(out_dir)
    folder.mkdir(parents=True, exist_ok=True)
    save_json(folder / "graph.json", graph)
    save_json(folder / "motifs.json", patterns)
    save_json(folder / "entities.json", entities)
    save_json(folder / "mcer_evidence.json", [asdict(x) for x in signed_evidence])
    save_json(folder / "mcer_partition.json", {
        "version_id": partition.version_id, "cutoff": partition.cutoff,
        "candidates": partition.candidates, "unresolved_pairs": partition.unresolved_pairs,
        "status": "TENTATIVE_NEVER_WALLET_IDENTITY",
    })
    save_json(folder / "leads.json", leads)
    save_json(folder / "features.json", features)
    save_json(folder / "wire_sessions.json", [session.as_dict() for session in sessions])
    save_json(folder / "wire_features.json", wire_features)
    save_json(folder / "quarantine.json", source.quarantine)
    save_json(folder / "propagation.json", {
        "max_hops": propagated["max_hops"], "capacity_points": 25,
        "seed_count": len(frozen), "points": priors,
        "frozen_seed_hash": propagated["frozen_seed_hash"],
        "witness_paths": propagated["top_paths"],
    })
    write_csv(folder / "leads.csv", leads, [
        "txid", "time", "priority", "risk_points", "local_seed_points", "propagation_points",
        "score_type", "source_id",
    ])
    manifest: dict[str, Any] = {
        "kind": "EVIDENCE_FIRST_UNSUPERVISED_V4",
        "schema_version": "4.0-static",
        "licence": licence, "source_origin": origin,
        "status": "CANDIDATE_LEADS_UNVALIDATED",
        "cutoff": when.isoformat(), "data_source_hashes": source.hashes,
        "readiness": {
            "analysis_mode": snapshot.readiness.mode.value,
            "reason": "; ".join(snapshot.readiness.reasons),
            "wire_observation_count": len(snapshot.wire),
            "exact_txid_joined_observations": sum(
                e.relation == "observed_relay" for e in snapshot.edges
            ),
            "cross_layer_dependence_verified": False,
        },
        "n_leads": len(leads), "n_motifs": len(patterns),
        "n_chain_edges": sum(e.relation == "spends_outpoint" for e in snapshot.edges),
        "n_wire_observations": len(snapshot.wire),
        "n_entities": len(entities), "n_quarantined_rows": len(source.quarantine),
        "n_wire_sessions": len(sessions), "n_wire_feature_rows": len(wire_features),
        "n_mcer_signed_evidence": len(signed_evidence),
        "n_mcer_tentative_entities": len(entities),
        "training_score_type": "UNSUPERVISED_RANK_NOT_PROBABILITY",
        "unvalidated_real_world_performance": True,
        "research_limitations": [
            "No legal attribution from IP observation",
            "Cross-layer Δ and Π abstain absent independently justified premises",
            "MCER addresses are uncertain hypotheses, not controller identities",
            "Synthetic performance cannot establish deployment accuracy",
        ],
    }
    save_json(folder / "monitoring.json", source_quality_report(manifest))
    save_json(folder / "run_manifest.json", manifest)
    manifest["audit_sha256"] = {
        name: hashlib.sha256((folder / name).read_bytes()).hexdigest()
        for name in ("graph.json", "motifs.json", "entities.json", "leads.json",
                     "features.json", "wire_sessions.json", "wire_features.json",
                     "propagation.json", "quarantine.json",
                     "mcer_evidence.json", "mcer_partition.json", "monitoring.json")
    }
    save_json(folder / "run_manifest.json", manifest)
    return manifest


def train_from_canonical(
    data_dir: str | Path, out_dir: str | Path, *, licence: str, origin: str,
    group_by: dict[str, str] | None = None, seed: int = 26,
) -> dict[str, Any]:
    """Separate, opt-in labeled research pipeline with chronological OOF.

    No labels enter evidence inference; labels must explicitly record availability.
    No unsafe pickle serialization.
    """
    source = import_canonical(data_dir, licence=licence, origin=origin, include_labels=True)
    if not source.labels:
        raise ValueError("labeled canonical file required; never infer labels from addresses/IPs")
    when = max(t.available_at for t in source.transactions)
    snapshot = build_snapshot(source.transactions, source.inputs, source.outputs,
                              source.wire, cutoff=when, source_hashes=source.hashes)
    rows = feature_rows(snapshot)
    labels = {label.subject_id: (label.value, label.available_at.isoformat())
              for label in source.labels if label.subject_type == "transaction"}
    result = fit_temporal_stack(rows, labels, groups=group_by, seed=seed)
    report: dict[str, Any] = {
        "status": result.status, "features": result.feature_names,
        "train_count": result.train_count, "future_count": result.future_count,
        "oof_count": result.meta_oof_count,
        "future_holdout_metrics": result.holdout,
        "source_hashes": source.hashes,
        "caveats": result.caveats,
        "note": "No claim of real-world calibration; no model pickle exported",
    }
    output = Path(out_dir)
    save_json(output / "training_manifest.json", report)
    save_json(output / "predictions.json", {
        "score_type": result.status,
        "predictions": result.predictions,
    })
    return report
