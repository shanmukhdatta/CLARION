"""Data-gated chain/wire Δ and verified economic-goal Π signal candidates.

These are research estimators with explicit abstention, never ownership or criminality
proof. Calling estimators alone does not establish scientific validity.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence

from clarion.v4.contracts import Abstention


def delta_signal(
    pairs: Sequence[dict[str, float]], *, min_independent: int = 30,
    holdout_fraction: float = 0.25, permutations: int = 500,
    alpha: float = 0.01, seed: int = 26,
) -> dict[str, object] | Abstention:
    """Permuted held-out cross-view predictability; conservative global Δ gate.

    Required: independent observation pairs with chain_*, wire_* fields.
    Pair collection MUST be externally deconfounded by capture window and sensor.
    Result is *not* a transaction-specific guilt score.
    """
    if len(pairs) < min_independent:
        return Abstention(reason="too few externally independent chain-wire pairs", missing=("independent_pairs",))
    if not (0.1 <= holdout_fraction < 0.5) or permutations < 100:
        raise ValueError("invalid scientific test controls")
    from numpy import asarray, corrcoef, random
    from sklearn.cross_decomposition import CCA
    from sklearn.preprocessing import StandardScaler
    import numpy as np

    keys = set(pairs[0])
    ck = sorted(k for k in keys if k.startswith("chain_"))
    wk = sorted(k for k in keys if k.startswith("wire_"))
    if not ck or not wk or any(set(p) != keys for p in pairs):
        return Abstention(reason="missing paired feature columns", missing=("chain_*", "wire_*"))
    X = asarray([[p[k] for k in ck] for p in pairs], dtype=float)
    Y = asarray([[p[k] for k in wk] for p in pairs], dtype=float)
    ntrain = int((1 - holdout_fraction) * len(pairs))
    if not np.isfinite(X).all() or not np.isfinite(Y).all():
        return Abstention(reason="missing or nonfinite paired observations")
    if ntrain < 4:
        return Abstention(reason="insufficient historical train window")
    scaler_x = StandardScaler().fit(X[:ntrain])
    scaler_y = StandardScaler().fit(Y[:ntrain])
    xtrain, xhold = scaler_x.transform(X[:ntrain]), scaler_x.transform(X[ntrain:])
    ytrain, yhold = scaler_y.transform(Y[:ntrain]), scaler_y.transform(Y[ntrain:])
    if np.std(xtrain) < 1e-10 or np.std(ytrain) < 1e-10:
        return Abstention(reason="degenerate paired-view variance")
    cca = CCA(n_components=1, max_iter=400)
    cca.fit(xtrain, ytrain)
    projected_x, projected_y = cca.transform(xhold, yhold)
    if len(projected_x) < 4:
        return Abstention(reason="heldout paired test too small")
    corr = float(corrcoef(projected_x[:, 0], projected_y[:, 0])[0, 1])
    if not isfinite(corr):
        return Abstention(reason="nonfinite heldout correlation")
    observed = abs(corr)
    rng = random.default_rng(seed)
    perm = [
        abs(float(corrcoef(projected_x[:, 0], rng.permutation(projected_y[:, 0]))[0, 1]))
        for _ in range(permutations)
    ]
    p_value = (1 + sum(v >= observed for v in perm)) / (permutations + 1)
    if p_value >= alpha:
        return Abstention(reason=f"paired dependence not established (heldout permutation p={p_value:.4g})")
    return {
        "status": "RESEARCH_ELIGIBLE", "metric": "heldout_CCA_abs_corr",
        "value": round(observed, 6), "permutation_p": round(p_value, 6),
        "train_pairs": ntrain, "holdout_pairs": len(pairs) - ntrain,
        "delta_components": {
            "delta_1_joint_dependence": round(observed, 6),
            "delta_2_timing": None, "delta_3_session": None,
            "delta_4_geo_context": None, "delta_5_infrastructure": None,
        }, "note": "No claimed operator identity; single global dependence gate, no casewise Δ inference.",
    }


@dataclass(frozen=True)
class VerifiedEconomicGoal:
    goal_id: str
    fee_sats: int | None
    hops: int | None
    duration_seconds: float | None
    outputs: int | None
    infra_cost_sats: int | None
    baseline_fee_sats: int | None
    baseline_hops: int | None
    baseline_duration_seconds: float | None
    baseline_outputs: int | None
    baseline_infra_cost_sats: int | None
    verified_goal_and_baseline: bool = False


def pi_signal(goal: VerifiedEconomicGoal) -> dict[str, object] | Abstention:
    """Computes dimensionless cost-over-baseline ratios for a *verified same goal*.

    No economic intent or hypothetical cheapest route is invented from public chain.
    Units: fee/infra satoshis, hops count, duration seconds, outputs count.
    """
    if not goal.verified_goal_and_baseline:
        return Abstention(reason="same-goal economic counterfactual not independently verified", missing=("controlled_goal", "baseline"))
    components: dict[str, float | None] = {}
    keys = ("fee_sats", "hops", "duration_seconds", "outputs", "infra_cost_sats")
    for key in keys:
        actual = getattr(goal, key)
        comparison = getattr(goal, "baseline_" + key)
        if actual is None or comparison is None or comparison <= 0 or actual < 0:
            components[key] = None
        else:
            components[key] = round(float(actual / comparison), 6)
    if all(v is None for v in components.values()):
        return Abstention(reason="no unit-bearing actual and baseline cost pairs")
    available = [v for v in components.values() if v is not None]
    assert available
    return {
        "status": "PARTIAL_VERIFIED_GOAL", "goal_id": goal.goal_id,
        "component_ratios": components,
        "available_components": len(available),
        "mean_cost_ratio": round(sum(available) / len(available), 6),
        "unavailable": [k for k, v in components.items() if v is None],
        "note": "Cost inefficiency is not criminal intent. No normalization across different physical units without per-component ratio.",
    }
