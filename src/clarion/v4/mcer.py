"""MCER v4 H1-H5 evidence ledger and conservative versioned partition hypotheses.

This does not establish legal identity, controller, source-IP attribution or guilt.
H3 embedding closeness and H4 wire-context disagreement are soft hypotheses.
"""
from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from itertools import combinations
from math import sqrt
from typing import Any, Literal

from clarion.v4.contracts import Snapshot, utc


@dataclass(frozen=True)
class SignedEvidence:
    left: str
    right: str
    mechanism: Literal["H1","H2","H3","H4","H5"]
    sign: Literal["support","conflict"]
    weight: float
    available_at: datetime
    independent_source: str
    evidence_ref: str
    statement: str

    def __post_init__(self) -> None:
        if not self.left or not self.right or self.left==self.right:
            raise ValueError("pair must have two distinct addresses")
        if not 0 < self.weight <= 1:
            raise ValueError("weight outside configured range")
        utc(self.available_at)


def h1_common_inputs(
    snapshot: Snapshot, *, blocked_transactions: set[str] | None = None,
    service_addresses: set[str] | None = None,
) -> list[SignedEvidence]:
    """Co-spend proposals unless structurally suggestive of multi-party spending."""
    blocked_transactions=blocked_transactions or set()
    service_addresses=service_addresses or set()
    outs={(o.txid,o.vout):o for o in snapshot.outputs}
    txins:dict[str,list[Any]]=defaultdict(list)
    for row in snapshot.inputs:
        txins[row.txid].append(row)
    txs={t.txid:t for t in snapshot.transactions}
    result=[]
    for tid,inputs in txins.items():
        if tid in blocked_transactions or len(inputs)<2 or tid not in txs:
            continue
        known=[outs.get((i.prev_txid,i.prev_vout)) for i in inputs]
        valid=[v for v in known if v is not None and v.address not in service_addresses]
        if len(valid)<2:
            continue
        # Exclude CoinJoin-like equal-valued large participant transactions.
        if len(valid)>=3 and len({o.value_sats for o in valid})==1:
            continue
        addresses=sorted(set(v.address for v in valid if v.address))
        for left,right in combinations(addresses,2):
            result.append(SignedEvidence(
                left,right,"H1","support",0.8,txs[tid].available_at,
                "transaction:"+tid,"input:"+tid,
                "Common-input heuristic subject to service/CoinJoin exclusions",
            ))
    return result


def h2_change_hypotheses(
    snapshot: Snapshot, *, threshold: float = 0.85,
) -> list[SignedEvidence]:
    """Propose, but never automatically confirm, ambiguous change links."""
    outs:dict[str,list[Any]]=defaultdict(list)
    times={t.txid:t.available_at for t in snapshot.transactions}
    for o in snapshot.outputs:
        outs[o.txid].append(o)
    inputs:dict[str,list[Any]]=defaultdict(list)
    for i in snapshot.inputs:
        inputs[i.txid].append(i)
    outpoint={(o.txid,o.vout):o for o in snapshot.outputs}
    result=[]
    for tid,spends in inputs.items():
        values=outs.get(tid,[])
        if len(values)!=2 or not all(v.address for v in values):
            continue
        total=sum(v.value_sats for v in values)
        if total<=0:
            continue
        dominant=max(values,key=lambda o:o.value_sats)
        share=dominant.value_sats/total
        if share<threshold:
            continue
        addresses=sorted({
            parent.address for i in spends
            if (parent:=outpoint.get((i.prev_txid,i.prev_vout))) is not None
            and parent.address
        })
        for address in addresses:
            if address==dominant.address:
                continue
            result.append(SignedEvidence(
                address, dominant.address, "H2","support",0.25,
                times[tid],"change-candidate:"+tid,f"output:{tid}:{dominant.vout}",
                "Dominant output may be change; weak unverified ownership clue",
            ))
    return result


def h3_embedding_pairs(
    vectors: dict[str,Sequence[float]], *,
    available_at:datetime, threshold:float=0.96,
    max_candidates:int=2000, embedding_snapshot_id:str,
) -> list[SignedEvidence]:
    """Cosine similarity proposals. Never give similarity alone merge authority."""
    if not 0<threshold<=1 or not embedding_snapshot_id:
        raise ValueError("required similarity threshold and fold-specific snapshot version")
    keys=sorted(vectors)
    if len(keys)>5000:
        raise ValueError("large H3 proposals require approximate nearest neighbors")
    result=[]
    for left,right in combinations(keys,2):
        left_vec,right_vec=vectors[left],vectors[right]
        if len(left_vec)!=len(right_vec) or not left_vec:
            continue
        dot=sum(float(a)*float(b) for a,b in zip(left_vec,right_vec,strict=True))
        ln=sqrt(sum(float(a)**2 for a in left_vec))
        rn=sqrt(sum(float(b)**2 for b in right_vec))
        similarity=dot/(ln*rn) if ln*rn else 0.0
        if similarity>=threshold:
            result.append(SignedEvidence(
                left,right,"H3","support",0.2,available_at,
                "embedding:"+embedding_snapshot_id,
                "vector:"+embedding_snapshot_id,
                "Graph representation similarity; not common controller proof",
            ))
        if len(result)>=max_candidates:
            break
    return result


def h4_uncertain_conflict(
    left:str,right:str, *, available_at:datetime,
    independent_source:str, evidence_ref:str,
    external_controller_conflict_verified:bool=False,
) -> SignedEvidence:
    """Geography/relay conflict cannot serve as hard identity veto.

    Only independently verified controller contradiction may later block a merge;
    the raw wire observational hypothesis has reduced weak sign/weight.
    """
    return SignedEvidence(
        left,right,"H4","conflict",
        1.0 if external_controller_conflict_verified else 0.15,
        available_at,independent_source,evidence_ref,
        "Independently verified conflicting controller facts" if external_controller_conflict_verified
        else "Observational wire/geography timing conflict is uncertain",
    )


def h5_continuity(
    left:str,right:str, *, available_at:datetime,
    source_id:str, evidence_ref:str,
) -> SignedEvidence:
    return SignedEvidence(
        left,right,"H5","support",0.12,
        available_at,source_id,evidence_ref,
        "Infrastructure/port continuity suggestion; not controller identity",
    )


@dataclass(frozen=True)
class Partition:
    version_id:str
    cutoff:str
    candidates:tuple[tuple[str,...],...]
    unresolved_pairs:tuple[tuple[str,str],...]
    ledger:tuple[SignedEvidence,...]
    false_identity_claims_prohibited:bool=True


def conservative_partition(
    entries:Iterable[SignedEvidence], *, cutoff:datetime,
    min_positive_sources:int=2, min_weight:float=1.15,
    hard_conflicts:set[frozenset[str]] | None = None,
    service_addresses:set[str] | None = None,
) -> Partition:
    """Merge only adequately independently supported non-service pairs.

    Long transitive chains are displayed as tentative group hypotheses.
    Hard conflicts require externally verified independent facts, not IP timing.
    """
    stamp=utc(cutoff)
    ledger=tuple(e for e in entries if e.available_at<=stamp)
    hard_conflicts=hard_conflicts or set()
    service_addresses=service_addresses or set()
    pairs:dict[tuple[str,str],list[SignedEvidence]]=defaultdict(list)
    for e in ledger:
        pairs[tuple(sorted((e.left,e.right)))].append(e)
    # No automatic hard constraints generated from H4 by itself.
    parent:dict[str,str]={}
    for left,right in pairs:
        parent.setdefault(left,left)
        parent.setdefault(right,right)
    def find(x:str)->str:
        while parent[x]!=x:
            x=parent[x]
        return x
    def members(root:str)->set[str]:
        return {k for k in parent if find(k)==root}
    unresolved=[]
    for (left,right),items in sorted(pairs.items()):
        if left in service_addresses or right in service_addresses:
            unresolved.append((left,right))
            continue
        # Independence is by source group, not repeated observations from one sensor.
        positives={e.independent_source:max(
            [v.weight for v in items if v.sign=="support" and v.independent_source==e.independent_source],
            default=0.0
        ) for e in items if e.sign=="support"}
        score=sum(positives.values())
        conflicted=sum(e.weight for e in items if e.sign=="conflict")
        if len(positives)<min_positive_sources or score-conflicted<min_weight:
            unresolved.append((left,right))
            continue
        a,b=find(left),find(right)
        if a==b:
            continue
        resulting=members(a)|members(b)
        if any(v.issubset(resulting) for v in hard_conflicts):
            unresolved.append((left,right))
            continue
        parent[b]=a
    groups:dict[str,list[str]]=defaultdict(list)
    for x in parent:
        groups[find(x)].append(x)
    candidates=tuple(sorted(tuple(sorted(v)) for v in groups.values() if len(v)>1))
    signature=sha256(repr((stamp.isoformat(),candidates,sorted(unresolved))).encode()).hexdigest()[:24]
    return Partition("mcer:"+signature,stamp.isoformat(),candidates,
                     tuple(sorted(unresolved)),ledger)


def partition_lineage(previous:Partition, current:Partition) -> dict[str,Any]:
    """Summarize as-of proposal lineage; never retroactively overwrite history."""
    old={frozenset(x) for x in previous.candidates}
    new={frozenset(x) for x in current.candidates}
    return {
        "old_version":previous.version_id,"new_version":current.version_id,
        "new_groups":[sorted(x) for x in new-old],
        "retired_groups":[sorted(x) for x in old-new],
        "still_tentative":True,
    }
