"""Research validity: honest holdouts, bootstrap intervals and cohort reviews.

No synthetic metric is presented as real-world evidence of illicit detection.
"""
from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Sequence
from typing import Any


def audited_metrics(
    truth: Sequence[int], scores: Sequence[float], *,
    group_ids: Sequence[str], source_kind: str,
    threshold: float = 0.5, bootstraps: int = 250,
    seed: int = 26,
) -> dict[str, Any]:
    import numpy as np
    from sklearn.metrics import (
        average_precision_score,
        confusion_matrix,
        f1_score,
        precision_score,
        recall_score,
        roc_auc_score,
    )
    if len(truth) != len(scores) or len(truth) != len(group_ids) or not truth:
        raise ValueError("aligned nonempty label/score/group sequences required")
    if set(truth) != {0,1}:
        raise ValueError("evaluation requires both audited classes")
    t = np.asarray(truth,dtype=int)
    p = np.asarray(scores,dtype=float)
    if not np.isfinite(p).all() or ((p<0)|(p>1)).any():
        raise ValueError("scores must be finite 0..1 comparable values")
    decisions=(p>=threshold).astype(int)
    grouped: dict[str,list[int]] = defaultdict(list)
    for index,gid in enumerate(group_ids):
        grouped[gid].append(index)
    rng=np.random.default_rng(seed)
    rates=[]
    for _ in range(bootstraps):
        selected = rng.choice(list(grouped),size=len(grouped),replace=True)
        sample=[i for gid in selected for i in grouped[gid]]
        if len(set(t[sample]))<2:
            continue
        rates.append(float(average_precision_score(t[sample],p[sample])))
    ci=(
        [round(float(np.quantile(rates,.025)),5),round(float(np.quantile(rates,.975)),5)]
        if rates else None
    )
    matrix=confusion_matrix(t,decisions,labels=[0,1])
    return {
        "source_kind":source_kind,
        "heldout_subjects":len(t),"heldout_groups":len(grouped),
        "auroc":round(float(roc_auc_score(t,p)),5),
        "auprc":round(float(average_precision_score(t,p)),5),
        "auprc_group_bootstrap_ci95":ci,
        "precision":round(float(precision_score(t,decisions,zero_division=0)),5),
        "recall":round(float(recall_score(t,decisions,zero_division=0)),5),
        "f1":round(float(f1_score(t,decisions,zero_division=0)),5),
        "confusion_matrix_0_1":matrix.tolist(),
        "threshold":threshold,
        "validated_real_world":False if source_kind.lower().startswith("synthetic") else None,
        "warning":"No attribution, guilt, independence or deployment performance implied",
    }


def ablation_comparison(
    arms: dict[str,Sequence[float]], truth:Sequence[int], *,
    same_heldout_ids:Sequence[str],
) -> dict[str, Any]:
    """Compare equal-subject heldout arms; leakage audits required upstream."""
    from sklearn.metrics import average_precision_score
    if len(same_heldout_ids)!=len(truth):
        raise ValueError("heldout subject identifiers not aligned")
    if len(set(same_heldout_ids))!=len(truth):
        raise ValueError("duplicate heldout subjects")
    scores={}
    for name,pred in arms.items():
        if len(pred)!=len(truth):
            raise ValueError(f"ablation {name} has a different heldout population")
        scores[name]=round(float(average_precision_score(truth,pred)),5)
    return {
        "auprc_by_arm":scores,
        "delta_vs_chain_only":{
            key:round(value-scores["chain_only"],5)
            for key,value in scores.items()
        } if "chain_only" in scores else {},
        "note":"Pairwise uplift needs confidence intervals and independent real-data audit",
    }


def temporal_leakage_audit(
    subjects: Sequence[dict[str,Any]], *,
    cutoff: str,
) -> dict[str, Any]:
    """Reject a feature, label or entity version not available by claimed cutoff."""
    leaked=[]
    for row in subjects:
        sid=str(row.get("subject_id","?"))
        for field in ("available_at","feature_available_at","entity_version_available_at"):
            if row.get(field) is not None and str(row[field])>cutoff:
                leaked.append({"subject_id":sid,"field":field,"timestamp":str(row[field])})
    return {"pass":not leaked,"leakage_count":len(leaked),"violations":leaked[:250]}


def false_merge_rate(proposed_pairs: Iterable[tuple[str,str]], truth_entities: dict[str,str]) -> dict[str,Any]:
    total=0
    wrong=0
    unknown=0
    for left,right in proposed_pairs:
        if left not in truth_entities or right not in truth_entities:
            unknown+=1
            continue
        total+=1
        wrong+=int(truth_entities[left]!=truth_entities[right])
    return {"evaluated_pairs":total,"false_merges":wrong,"unknown_pairs":unknown,
            "false_merge_fraction":round(wrong/total,6) if total else None}
