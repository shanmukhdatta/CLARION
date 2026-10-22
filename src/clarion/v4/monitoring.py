"""Offline feature drift and factual batch observability, not model self-training."""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any


def population_stability_index(
    baseline: Sequence[float], current: Sequence[float], *,
    bins: int = 10,
) -> dict[str, Any]:
    """Reference-only quantile bins, with epsilon for empty bins.

    PSI is a diagnostic without a universal reliable 'drift detected' threshold;
    sign-off requires source/label and sample-shift investigation.
    """
    import numpy as np

    if not 3 <= bins <= 50:
        raise ValueError("bins must be 3..50")
    if len(baseline) < 30 or len(current) < 30:
        raise ValueError("at least 30 samples per population required")
    before = np.asarray(baseline, dtype=float)
    after = np.asarray(current, dtype=float)
    if not np.isfinite(before).all() or not np.isfinite(after).all():
        raise ValueError("drift samples cannot contain nonfinite values")
    boundaries = np.unique(np.quantile(before, np.linspace(0, 1, bins + 1)[1:-1]))
    if not len(boundaries):
        return {"status": "ABSTAIN", "reason": "baseline has no variation"}
    b = np.bincount(np.searchsorted(boundaries, before, side="right"),
                    minlength=len(boundaries) + 1).astype(float)
    c = np.bincount(np.searchsorted(boundaries, after, side="right"),
                    minlength=len(boundaries) + 1).astype(float)
    # Smooth count distribution without making missing examples into real labels.
    b = (b + 0.5) / (b.sum() + len(b) * 0.5)
    c = (c + 0.5) / (c.sum() + len(c) * 0.5)
    terms = (c - b) * np.log(c / b)
    return {
        "status": "MEASURED_NOT_CAUSAL",
        "metric": "reference_anchored_population_stability_index",
        "value": round(float(np.sum(terms)), 6),
        "bins": len(b), "baseline_count": len(before), "current_count": len(after),
        "limitations": "Does not establish misconduct, predictive drift or source quality",
    }


def source_quality_report(manifest: dict[str, Any]) -> dict[str, Any]:
    """Record exact available-source quality; no invented missingness statistics."""
    return {
        "schema_version": manifest.get("schema_version"),
        "mode": manifest.get("readiness", {}).get("analysis_mode"),
        "input_hash_count": len(manifest.get("data_source_hashes", {})),
        "quarantined_rows": manifest.get("n_quarantined_rows"),
        "chain_edges": manifest.get("n_chain_edges"),
        "wire_observations": manifest.get("n_wire_observations"),
        "wire_sessions": manifest.get("n_wire_sessions"),
        "case_count": manifest.get("n_leads"),
        "scientific_validation": "UNVERIFIED",
    }
