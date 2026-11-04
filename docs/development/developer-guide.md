# Development sequence and architecture controls (planned workflow)

**No application code is asserted working by this document.**

## 1. Correct first technical order

1. Review source PDF, [requirement audit](../architecture/REQUIREMENTS_AUDIT.md), [component contracts](../architecture/component-contracts.md), [schema dictionary](../data/data-dictionary.md) and [TXID join policy](../data/join-policy.md).
2. Acquire or produce **small legal synthetic** CSV/JSON/XML fixtures with known truth; document timestamp, satoshi, outpoint and event semantics.
3. Implement strict parsers/schema and test failure/abstention behavior; reserve local read-only raw evidence store and run manifest.
4. Implement J0 exact on-chain value flow, J1 observed TXID relay joins and J2 context with no owner edges.
5. Materialize six-type graph, time snapshots, source-to-edge evidence and chain-only baseline; run in Linux without Internet.
6. Only afterward add graph embeddings, MCER, patterns and actual trained ML under time-respecting folds.
7. Build Δ and Π only where their independent prerequisites pass; do not assign zeros to missing.
8. Freeze first-pass seeds, validate bounded MLRP, then implement local API/React UI and case exports.
9. Run all negative controls and L0–L3 scientific experiments; disclose limits.

## 2. Phase/PR contract

Every PR identifies block(s) and inputs/outputs affected, typed schema migration, tests actually executed, output artifact hashes, security/privacy impact, unresolved decisions and a rollback. No self-asserted high accuracy, no fake train logs and no executable code in documentation-only PRs.

## 3. Source of truth precedence

1. Uploaded CLARION v4 diagram and user-supplied SIH26146 statement: **requirements**.
2. 33-section [architecture-v4-spec.md](../architecture/architecture-v4-spec.md): source-preserving implementation expansion.
3. [REQUIREMENTS_AUDIT](../architecture/REQUIREMENTS_AUDIT.md) and approved ADRs: explicit constraints/resolutions.
4. Detailed data/ML/security/dashboard docs: design contracts.
5. README per source folder: module handoff; update if interface decisions change.

If two design docs conflict, open an ADR and fix contracts together, not a silent implementation change.

## 4. Ready for Phase 1?

Only if the chosen test fixture defines field units, real/synthetic TXID semantics, sufficient chain event data, and the exact chain-only fallback. Real network dependence and verified labels need not exist to **begin** Phase 1; they are data gates to be measured and must remain explicitly unknown until inspected.


## Canonical autonomous sequence

The sole phase numbering is P0–P9 in the master plan. Follow [Autonomous Implementation Contract](AUTONOMOUS_EXECUTION_CONTRACT.md) and maintain [Phase Implementation Ledger](../progress/PHASE_IMPLEMENTATION_LEDGER.md). Older P0–P5 playbooks and 11 work packages are mapped to this sequence; do not create parallel roadmaps.

Start P0 with latest main SHA, source/172-REQ mapping, fresh baseline logs, data-rights/semantics inventory, dependency reconciliation and canonical module map. Then implement P1 mini24: exactly 24 transaction records, equivalent CSV/JSON/XML normalization, source hashes, quarantine, integer satoshis/exact outpoints and truth isolation. Continue P2–P9 only when each prior gate has evidence.

Make routine engineering choices without asking the user. Missing real data blocks only dependent claims; complete the safe synthetic/chain-only path. Never claim unrun tests passed. At the 5 Nov 2026 baseline, uv.lock omits some v4 extras and frontend package-lock.json is absent; follow LOCAL_TESTING.md pending P0 reconciliation.
