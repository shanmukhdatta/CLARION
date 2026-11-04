# CLARION v4 — Phase Implementation Ledger

Revision: 5 November 2026. Documentation baseline: main at `f06594643b6ba3c58d4fbffb361e4ba475a85a71`. Every task is UNASSESSED until fresh source/test evidence is recorded. This ledger does not claim implementation completion.

## Status definitions
- UNASSESSED: no fresh evidence at current SHA.
- IN_PROGRESS: work started; gate not passed.
- IMPLEMENTED_UNTESTED: code exists, required tests not passed.
- TESTED: named tests passed on named fixture; phase gate may remain.
- VERIFIED: every acceptance condition passed with reproducible logs/artifacts and review.
- DATA_BLOCKED: only the dependent external-data/scientific claim is blocked.
- FAILED: required test or acceptance condition failed.

For each status change record task ID, source SHA, changed paths, fixture/dataset and rights, subject level, exact commands/environment/exit code, test counts, hashes, artifact paths, limitations and next handoff. Do not mark VERIFIED because a file exists or a mock works.

## P0 — Repository audit, environment and scope freeze
Phase status: UNASSESSED.
| ID | Work | Acceptance evidence | Status |
|---|---|---|---|
| P0.1 | Fetch latest main; record SHA/worktree; inventory source/docs/tests/workflows | Baseline manifest | UNASSESSED |
| P0.2 | Read architecture, master plan, data dictionary, join policy, feature audit and definition of done | Source-document map and stale-reference list | UNASSESSED |
| P0.3 | Map all 172 REQ IDs to canonical source owners/tests/status | Requirement-to-source/test matrix | UNASSESSED |
| P0.4 | Run Python, compile, Ruff, available type checks, frontend typecheck/build and CI | Logs, versions, exit codes; FAIL/SKIP/NOT RUN distinct | UNASSESSED |
| P0.5 | Inventory data rights, schema, labels, subject level, times, outpoints and sensor provenance | Data-readiness/rights matrix and D01–D12 | UNASSESSED |
| P0.6 | Reconcile pyproject, uv.lock, requirements-v4/demo, package.json and npm lock | Clean-install plan | UNASSESSED |
| P0.7 | Identify canonical module owners, stubs and duplicates | Module ownership map | UNASSESSED |
| P0.8 | Freeze first chain-only vertical slice | P1 acceptance specification | UNASSESSED |
Exit: current source map, 172-REQ baseline, test log, data/rights inventory, dependency plan, D01–D12 and first-slice spec.

## P1 — Contracts and mini24
Phase status: UNASSESSED.
| ID | Work | Acceptance evidence | Status |
|---|---|---|---|
| P1.1 | Versioned transaction/input/output/observation/session/label/source contracts | Valid/invalid/missing schema tests | UNASSESSED |
| P1.2 | Fictional mini24: exactly 24 transaction records | Seed, counts, fixture README and hashes | UNASSESSED |
| P1.3 | CSV/JSON/XML parity and quarantine | Equivalent normalized records; malformed/duplicate tests | UNASSESSED |
| P1.4 | Source bytes, SHA-256, rights, schema, row lineage, event/available times | Deterministic re-import/provenance tests | UNASSESSED |
| P1.5 | Integer satoshis, unique TXIDs/outpoints, prevout constraints | Conservation, duplicate spend and unresolved-prevout tests | UNASSESSED |
| P1.6 | Synthetic truth isolated from inference | Truth absent from features/graph/scores/UI | UNASSESSED |
| P1.7 | Parser fixture separate from training cohort | Distinct manifests and label scopes | UNASSESSED |
Exit: 24 transactions; format parity, hashes, satoshi/outpoint invariants and truth-isolation pass.

## P2 — Network/transport/P2P and Bitcoin transaction layers
Phase status: UNASSESSED.
| ID | Work | Acceptance evidence | Status |
|---|---|---|---|
| P2.1 | Validate endpoint, IP family, port, protocol, direction, sensor and time | Contract and malformed-input tests | UNASSESSED |
| P2.2 | Sessionize, deduplicate, count independent sensors, coverage and clock uncertainty | Replay/duplicate/skew tests | UNASSESSED |
| P2.3 | Relay facts only from exact TXID observed by documented decoder | Source provenance; time/IP-only joins rejected | UNASSESSED |
| P2.4 | Parse Bitcoin Core exports and preserve block/mempool/reorg state | Known fixture/parser tests | UNASSESSED |
| P2.5 | Resolve exact txid:vout; validate coinbase, duplicate spends, fees and known-value conservation | Outpoint/satoshi tests | UNASSESSED |
| P2.6 | Separate chain/wire readiness; CHAIN_ONLY when wire unavailable | Readiness and no-host-wallet-edge tests | UNASSESSED |
Exit: independent chain/wire gates pass; no inferred broadcaster, owner or identity.

## P3 — Temporal graph and feature registry
Phase status: UNASSESSED.
| ID | Work | Acceptance evidence | Status |
|---|---|---|---|
| P3.1 | Six node types and directed typed-edge allowlist | Schema/forbidden-edge tests | UNASSESSED |
| P3.2 | Source IDs/hashes, event/available times, cutoff, uncertainty, version | Every edge resolves to source evidence | UNASSESSED |
| P3.3 | Separate chain-only, wire-only and eligible cross-layer views | Mode-isolation tests | UNASSESSED |
| P3.4 | Deterministic as-of snapshots, graph hashes, Parquet/DuckDB | Future-edge removal and replay tests | UNASSESSED |
| P3.5 | Versioned causal feature registry, units and missingness | Fold-local transform/availability tests | UNASSESSED |
| P3.6 | Graph stats/Node2Vec only after reference graph passes | Reproducibility/resource report | UNASSESSED |
| P3.7 | Bounded neighborhood/subgraph export | Size, provenance and cutoff tests | UNASSESSED |
Exit: traceable graph/features; future data cannot alter past snapshots.

## P4 — MCER and motifs
Phase status: UNASSESSED.
| ID | Work | Acceptance evidence | Status |
|---|---|---|---|
| P4.1 | H1 co-spend proposals and CoinJoin/multi-party controls | False-merge tests | UNASSESSED |
| P4.2 | H2 change proposals with alternatives | Witness paths/hard negatives | UNASSESSED |
| P4.3 | H3 embedding similarity proposal-only | No embedding-only forced merge | UNASSESSED |
| P4.4 | H4 wire conflict/H5 behavioral continuity | NAT/VPN/shared-host and independence tests | UNASSESSED |
| P4.5 | Bounded merge/split/review, lineage, convergence and conflicts | Deterministic iteration tests | UNASSESSED |
| P4.6 | Peel/fan-in/fan-out/fragmentation/layering motif witnesses | Reproducible witness paths | UNASSESSED |
| P4.7 | Benign service/custody/consolidation/CoinJoin controls | Independent truth and candidate-entity metrics | UNASSESSED |
Exit: every merge/motif explainable; weak context cannot force identity; report clusters, not people.

## P5 — ML, chronological stacking and optional GNN
Phase status: UNASSESSED.
| ID | Work | Acceptance evidence | Status |
|---|---|---|---|
| P5.1 | Freeze task, subject, dataset, label and cutoff | Eligibility manifest | UNASSESSED |
| P5.2 | Chronological/grouped splits; fold-local transforms | Leakage/future-label tests | UNASSESSED |
| P5.3 | Rule-only, logistic regression and Random Forest | Same-split baseline report | UNASSESSED |
| P5.4 | Isolation Forest novelty, not probability | Score-type/label-ineligible tests | UNASSESSED |
| P5.5 | GraphSAGE only if justified; GAT optional challenger | Same-split/resource comparison | UNASSESSED |
| P5.6 | Chronological OOF base scores; meta-learner on OOF only | Fold/OOF key integrity | UNASSESSED |
| P5.7 | Calibration, uncertainty, hard negatives, subgroup/resource report | Metrics, N, valid intervals and model cards | UNASSESSED |
Exit: no future leakage; stack compared fairly to strongest base; novelty is not crime probability.

## P6 — Delta/Pi and pass-1 fusion
Phase status: UNASSESSED.
| ID | Work | Acceptance evidence | Status |
|---|---|---|---|
| P6.1 | Delta independent paired chain/wire evidence, coverage and null tests | Eligibility report | UNASSESSED |
| P6.2 | Pi documented objective and same-goal feasible baseline | Objective provenance and unit-aware cost | UNASSESSED |
| P6.3 | Component ABSTAIN, counterevidence and typed fusion | Missing-premise tests | UNASSESSED |
| P6.4 | Freeze/hash pass-1 scores and seeds | Immutable seed manifest | UNASSESSED |
Exit: unsupported Delta/Pi abstain; pass-1 immutable.

## P7 — Bounded MLRP and pass-2
Phase status: UNASSESSED.
| ID | Work | Acceptance evidence | Status |
|---|---|---|---|
| P7.1 | Typed edge allowlist, direction, time and eligibility | Forbidden-edge tests | UNASSESSED |
| P7.2 | Verified UTXO value-share; separate forward/backward/context | Conservation/no-duplication tests | UNASSESSED |
| P7.3 | Damping/time decay and maximum six scored hops | Boundary tests | UNASSESSED |
| P7.4 | Propagation applied once, capped at 25/100 | Score decomposition/cap tests | UNASSESSED |
| P7.5 | Host/ASN/Country cannot re-emit financial exposure | Context no-taint tests | UNASSESSED |
| P7.6 | Seed/path/boundary/uncertainty lineage | Reproducible path and pass-1 immutability | UNASSESSED |
Exit: six-hop and 25/100 bounds hold; no circular feedback or contextual taint.

## P8 — API, UI and case export
Phase status: UNASSESSED.
| ID | Work | Acceptance evidence | Status |
|---|---|---|---|
| P8.1 | Typed DTOs, pagination and payload limits | API schema/invalid-query tests | UNASSESSED |
| P8.2 | UI connected to actual run artifacts | Browser/API E2E; no mock-only claims | UNASSESSED |
| P8.3 | Case review, notes and immutable snapshots | Review/persistence tests | UNASSESSED |
| P8.4 | JSON/CSV/PDF exports, redaction and integrity hashes | Round-trip, formula-injection and redaction tests | UNASSESSED |
| P8.5 | Loopback defaults and no external runtime dependency | Local access/network-denial tests | UNASSESSED |
Exit: displayed claims trace to run artifacts; uncertainty visible; E2E passes.

## P9 — Validation, security and offline release
Phase status: UNASSESSED.
| ID | Work | Acceptance evidence | Status |
|---|---|---|---|
| P9.1 | Separate Elliptic++, BitcoinHeist, Core correctness and synthetic truth tracks | Dataset-specific manifests/reports | UNASSESSED |
| P9.2 | Sealed holdout, ablations and benign hard negatives | Reproducible reports | UNASSESSED |
| P9.3 | Missing sensors, time skew, label/generator shift and drift | Robustness/abstention report | UNASSESSED |
| P9.4 | Malicious inputs, model artifacts, API and export security | Security report/severity list | UNASSESSED |
| P9.5 | Python/npm locks, licensed offline wheelhouse/assets | Lock/license manifest | UNASSESSED |
| P9.6 | Clean Linux run with network disabled | Install/run/egress-denial logs | UNASSESSED |
| P9.7 | Refresh all 172 requirement statuses and publish limitations | SHA-linked audit | UNASSESSED |
Exit: reviewer reproduces case source-to-dossier on clean offline Linux.

## Current handoff
Start P0 from latest main. Refresh SHA/source map, run baseline checks, reconcile dependency state, then freeze and implement P1 mini24. Do not start GNN, Delta/Pi or dashboard expansion before data/evidence contracts pass.
