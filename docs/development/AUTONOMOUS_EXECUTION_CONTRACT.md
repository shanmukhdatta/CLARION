# CLARION v4 — Autonomous Implementation Contract

Revision: 5 November 2026. Canonical implementation sequence: P0–P9. This is an execution policy, not evidence that any code or phase is complete.

## Source-of-truth order
1. `CLARION_V4_MASTER_IMPLEMENTATION_PLAN.md`: architecture, algorithms, datasets, interfaces and acceptance.
2. The 172-item requirements checklist: requirement traceability.
3. Current source and fresh test output: implementation status.
4. `../progress/PHASE_IMPLEMENTATION_LEDGER.md`: task status, evidence and blockers.
5. This contract and `AGENT_EXECUTION_PROMPT.md`: coding-agent behavior.
6. `../LOCAL_TESTING.md`: runnable setup and commands.
Older P0–P5 and 11-phase documents are historical/learning material; they do not override P0–P9.

## Canonical phase sequence
| Phase | Scope | Exit evidence |
|---|---|---|
| P0 | Repository audit, environment and scope freeze | Current SHA, source/172-REQ map, baseline logs, data-rights inventory, dependency plan |
| P1 | Contracts, ingestion and deterministic fixture | Versioned schemas; exactly 24 transaction records; CSV/JSON/XML parity; provenance and truth-isolation tests |
| P2 | Network/transport/P2P and Bitcoin transaction layers | Independently validated wire/chain evidence; exact outpoints; CHAIN_ONLY fallback |
| P3 | Temporal graph and feature registry | Six node types, typed evidence edges, as-of snapshots and causal feature tests |
| P4 | MCER candidate-entity resolution and motifs | Merge/split lineage, conflict ledger, motif witnesses and benign hard negatives |
| P5 | Classical ML, stacking and optional graph learning | Chronological/grouped splits, OOF stacking, baselines, leakage audit and resource report |
| P6 | Delta/Pi and pass-1 fusion | Eligibility gates, explicit ABSTAIN, typed scores and frozen pass-1 hash |
| P7 | Bounded MLRP and pass-2 ranking | Causal paths, six-hop maximum, 25/100 propagation cap, no contextual re-emission |
| P8 | Local API, investigator UI and case export | UI/API connected to run artifacts, evidence drill-down and redacted/hash-bound exports |
| P9 | Independent validation, security and offline release | Separate benchmark tracks, ablations, security report and clean offline Linux reproduction |

The older 11 work packages map into P1–P9: mini24→P1; network/P2P and Bitcoin/UTXO→P2; graph/features→P3; MCER/motifs→P4; ML/stacking/GNN→P5; Delta/Pi/pass-1→P6; MLRP/pass-2→P7; API/UI→P8; DevOps/security/offline validation→P9. Do not create Phase 10 or 11.

## Autonomous decision policy
- Make routine choices (functions, tests, filenames, ordinary libraries already in the plan) by inspecting neighboring code and tests. Do not ask the user to choose them.
- Reuse canonical v4/application/API modules. Do not create parallel subsystems or duplicate existing behavior.
- If external data is absent, finish schema adapters, synthetic correctness tests and safe fallback; mark only real-data validation DATA_BLOCKED.
- If labels are absent/unsuitable, use unsupervised novelty; never manufacture labels or supervised metrics.
- If Delta paired observations are absent, return ABSTAIN. If Pi objective/control assumptions are absent, return component-level ABSTAIN.
- If SIH schema/sensor semantics are undocumented, do not guess. Record the blocker and continue independent tasks.
- Diagnose failing tests; never delete/weaken tests or claim unrun tests passed.
- Pause only for legal/permission/account authorization, destructive actions, or an architecture-changing research decision not resolvable from approved evidence. Continue unrelated work.

## Phase execution details
### P0
Fetch latest main and record SHA; inspect source tree, tests, CI and docs; map all 172 REQ IDs to actual source owners/tests/status; run Python, lint, type, frontend and CI checks; record versions, commands, exit codes and logs; inventory data rights, schema, subject level, labels, event/available times, TXID/outpoint completeness and sensor provenance; reconcile Python/npm dependencies; identify canonical modules/stubs; freeze chain-only first slice and D01–D12.
### P1
Define versioned transaction/input/output/observation/session/label/source-manifest contracts. Build fictional mini24 with exactly 24 transaction rows (auxiliary tables may have different counts), deterministic seed/revision/hashes, timezone-aware event/available times, integer satoshis, unique TXIDs and exact outpoints. Export CSV/JSON/XML with equivalent normalized rows; quarantine malformed/duplicate/unsupported inputs. Keep synthetic truth in a separate sidecar and prove it never enters inference features, graph, scores or UI.
### P2
Validate endpoint/IP/port/protocol/sensor/direction/time; sessionize with deduplication, independent-sensor counts, coverage and clock uncertainty. Create relay facts only from exact TXIDs observed by a documented decoder; never infer TXID from time/IP proximity. Parse Bitcoin Core exports, resolve exact txid:vout prevouts, preserve unresolved ancestry/reorg state, and validate known-value satoshi conservation. Keep chain/wire gates independent; default CHAIN_ONLY.
### P3
Implement six canonical node types and directed typed-edge allowlist. Every derived edge carries source IDs/hashes, event/available time, cutoff, uncertainty and version. Build separate chain-only/wire-only/cross-layer views, deterministic as-of snapshots, graph hashes, Parquet/DuckDB queries and a versioned feature registry. Test future-edge removal and feature availability.
### P4
Implement H1–H5 as proposals with evidence, conflicts and alternatives; bounded merge/split/review, convergence, iteration cap and lineage. Embedding, ASN, subnet or shared-host context cannot force entity merge. Motifs require exact witness paths. Include benign batching, custody, consolidation, CoinJoin-like and privacy-use hard negatives. Report candidate entities/clusters, never people.
### P5
Freeze task, subject level, dataset, label definition and cutoff. Keep Elliptic++, BitcoinHeist and Bitcoin Core correctness as separate tracks. Use chronological/grouped splits; fit transforms inside folds. Establish rule-only, logistic regression, Random Forest and Isolation Forest novelty baselines. Train meta-learner only on chronological OOF predictions. Add GraphSAGE/GAT only when labels, graph task and compute justify them. Report hard negatives, uncertainty, abstention, runtime and memory.
### P6
Delta requires independent paired timestamped chain/wire evidence, coverage and dependence/null checks. Pi requires documented objective and same-goal feasible baseline. Preserve units/missingness; unsupported components ABSTAIN. Freeze/hash pass-1 scores and seeds before propagation.
### P7
Enforce edge allowlist, direction and time; use verified UTXO value-share allocation; separate forward exposure, backward provenance and context; maximum six scored hops; total propagation contribution at most 25/100 and applied once. Host/ASN/Country are context only and never re-emit financial exposure.
### P8
Use typed DTOs, pagination and payload limits. Serve completed run artifacts; do not train in HTTP requests. Connect UI to versioned artifacts, not hard-coded mocks. Provide evidence/timeline drill-down, uncertainty/abstention, case review and redacted/hash-bound JSON/CSV/PDF exports. Verify loopback-only defaults.
### P9
Evaluate public datasets, Bitcoin Core correctness and synthetic truth separately. Run sealed holdouts, ablations, benign hard negatives, source/time subgroup tests, missing-sensor/time-skew/label-shift tests, malicious-input/API/export security checks, license review and clean offline Linux reproduction.

## Every-task loop
Before: read owner module and folder README; record task ID, files, dependencies, expected output and tests; confirm behavior is not already implemented.
After: run targeted and integration tests; save exact commands, environment, exit codes, logs and hashes; update requirement rows only with evidence; regenerate folder README in write then check mode; update ledger; commit a small reviewable change. If a test cannot run, mark NOT RUN.

## Environment and Git
At the 5 Nov 2026 baseline, `uv.lock` does not include every v4/demo extra in `requirements-v4.txt` and `requirements-demo.txt`; frontend has no committed `package-lock.json`. Therefore `uv sync --locked` alone is not a full v4 setup, and `npm ci` is not usable until a lockfile exists. Follow `docs/LOCAL_TESTING.md` meanwhile. P0 must reconcile and validate both lockfiles. Keep Torch/PyG optional for P0/P1.
Branch from latest main, use small task commits and PRs, never force-push, bypass CI, overwrite collaborator work, commit secrets or confidential data. A merged PR is not automatically VERIFIED.
