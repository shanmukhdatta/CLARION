# MASTER EXECUTION PROMPT — CLARION v4 end-to-end completion

> **For a repository-aware autonomous coding agent.** This document is an instruction to **inspect, implement, run, test, commit and integrate code**. It is NOT a request for a second plan or another static architecture document. Work in https://github.com/shanmukhdatta/CLARION, default branch `main`, and use existing code. Audit baseline 31 October 2026: `docs/progress/CURRENT_AUDIT_2026-10-31.md`.

## A. Mission and non-negotiable interpretation

Implement CLARION, an **offline-first, explainable Bitcoin on-chain + observed P2P/network evidence investigator**. Input: authorized CSV/JSON/XML, local Bitcoin transaction/block exports, and optional independently observed Bitcoin peer/relay metadata. Output: canonical proof-carrying evidence, exact as-of UTXO value-flow, source-tagged network observation graph, conservative cross-layer joins, candidate clusters and pattern witnesses, tabular/graph anomaly models, noncircular bounded lead prioritization, investigator UI and auditable cases/reports. A score denotes review priority or novelty unless independently validated and calibrated; **do not call it a probability of criminal behavior**.

Your job is **code execution and implementation**, not generating another roadmap. Use original `README.md` (40+ numbered sections), `docs/architecture/architecture-v4-spec.md` (blocks 0–12), `docs/IMPLEMENTATION_CHECKLIST.md` (172 items), `docs/data/data-dictionary.md`, `docs/data/join-policy.md`, `docs/ARCHITECTURE.md`, `docs/IMPLEMENTATION_DECISIONS.md`, `docs/LOCAL_TESTING.md` and the current restart audit. Treat architecture as functional targets, but treat code/test evidence as truth about what is already finished.

If a module exists in `src/clarion/v4/`, `src/clarion/application/`, or `src/clarion/api/` while an older named module is marked `FILE BLUEPRINT ONLY`, **integrate/reuse the working module** and expose a compatibility adapter if worthwhile. Do not create a second disconnected implementation; do not delete README sections or invent training results. Keep existing React investigator UI in a coherent light theme rather than rebuilding it unless necessary.

**Core safety and scientific invariants:** an observed relay IP is NOT a Bitcoin wallet owner or transaction origin; Host/ASN/Country are contextual, not financial taint conduits; exact money transfer requires validated TXID:vout; all amounts integer satoshis; every edge has provenance and as-of availability; unavailable labels => unsupervised-only; unverified independent chain/wire pairs => Δ ABSTAIN; unverified economic objective => Π ABSTAIN; case labels and synthetic truth never enter live features; no look-ahead or train/test leakage; no false crime/calibration claims; offline inference uses only bundled local assets; confidential or unauthorized evidence does not enter Git.

## B. First actions — verify, do not rewrite

1. Clone repository, inspect branch status/current SHA, list all modules/tests/workflows/docs, read the files in section A. Start from `main` and create working branch `implementation/clarion-e2e-restart`; never force-push or overwrite someone else's commits.
2. Build a traceability table with all 172 requirement IDs: owner file, status (VERIFIED_NARROW / WRITTEN_UNTESTED / PARTIAL / MISSING / EXTERNALLY_BLOCKED), exact runnable test, and evidence. Refresh statuses only with observed results. Keep both `docs/IMPLEMENTATION_CHECKLIST.md` and an updated status JSON/CSV in sync.
3. Install project/environment using documented Python 3.11/3.12 tooling, Node and optional Torch/PyG. First run `python -m pytest -q`, `python -m compileall -q src`, `python -m ruff check src/clarion/v4 tests/v4 scripts/v4_pipeline.py`, `cd frontend && npm ci && npm run typecheck && npm run build` (use `npm install` if no lockfile). Record versions and full command output. Do not claim a passing local test if unable to run it.
4. Exercise existing 36-case training and v4 analysis demo before changing algorithms. Run `python scripts/full_demo_pipeline.py --out artifacts/full_demo --cases 36 --seed 26`, `python scripts/v4_pipeline.py --help`, and `python scripts/submission_demo.py run --out artifacts/submission_demo --cases 10 --seed 26`. Check actual outputs and their score-type/status labels. Report any failures as defects, repair first.
5. Identify blueprint-only modules that are referenced by public entrypoints; align import paths and build pipeline stages around one canonical implementation per contract. Avoid a broad file-rename migration before tests exist.
6. Commit the baseline traceability and verifiable fixes as `chore(audit): establish CLARION baseline and executable gates`.

**Do not stop after these steps. Proceed phase by phase with actual code.** If time or compute is limited, complete smaller connected vertical slices before moving on; never mark untested work complete.

## C. Required phase order and deliverables

### Phase 1 — exactly 24-transaction mini dataset (FIRST IMPLEMENTATION)

Build a deterministic, versioned synthetic **mini24** dataset to prove every data contract before complex ML.

- Reuse `src/clarion/application/engine.py`: `clarion generate-demo --out data/generated/mini24 --cases 6 --seed 26` currently emits four transactions per case, i.e. **24 transaction rows** (including six fictional funding records). This is a starting fixture, not a realistic statistical dataset. Build a dedicated generator/fixture validator if needed.
- Commit reviewed example data to `data/samples/mini24/`: `transactions.csv` (exactly 24 records), `inputs.csv`, `outputs.csv`, `observations.csv`, `truth_SYNTHETIC_ONLY.csv`, `source_manifest.json`, preferably `expected_manifest.json` and `README.md`. Do not force the auxiliary tables to have 24 rows: they represent one-to-many relations.
- Each record must be internally consistent with `src/clarion/v4/contracts.py` and source mappings: unique 64-hex TXIDs; nonnegative integer satoshis; exact unique outpoint references and no double-spend within the fixture; timezone-aware event/available timestamps; valid source identifiers; sensor-tagged relay observations with explicit decoded-TXID provenance; example/reserved documentation IPs only. Add input/output schema validation and hashes/fixture revision.
- Include benign ordinary transfers, multi-output change-like patterns, benign service/CoinJoin-like hard negatives and peel/layering-like **candidate** pattern examples, consistent with available fixture size. These are *fictional investigation scenarios*, not criminal ground truth. If richer patterns require a second fixture, add a separate `mini_patterns` fixture rather than compromising 24-row exactness.
- Make `truth_SYNTHETIC_ONLY.csv` accessible solely to supervised demo tests/training. Assert no truth-sidecar columns reach ingestion, snapshots, features, graph nodes, model inference, or UI as factual labels.
- CLI: support explicit deterministic generation, `clarion validate` and v4 analysis; save generated data separate from checked-in golden fixture. Run twice with the same seed and compare canonical file digests after excluding intentionally variable run timestamps; reject malformed rows and duplicate spends.
- **Acceptance:** 24 transaction records, valid references/amount conservation on fully known spends, valid as-of snapshots, checked source/hash manifest, functioning analyze and JSON outputs, golden verification tests, negative parser and leakage tests.
- Commit: `feat(data): add deterministic 24-transaction canonical acceptance fixture`.

### Phase 2 — network/P2P observation layer

- Extend `src/clarion/v4/wire_sessions.py` and reusable canonical adapters; use existing `WireObservation` contract instead of making a second incompatible network table.
- Accept bounded, permissioned local CSV/JSON/XML network records. Define real field-mapping configuration and distinguish TXID observed in a decoded Bitcoin INV/TX message from a TXID inferred merely by shared time/IP. Preserve sensor_id, event_time, available_at, clock_uncertainty_ms, source/destination ports, direction, host, decode_provenance, source SHA-256, source row/record reference and optional ASN/country.
- Implement dedup within the same sensor, bounded sessionization, per-host/sensor coverage, first/last-seen windows, port entropy, missingness and clock-skew uncertainty. Never dedup observations from independent sensors into the same raw evidence record.
- Validate IPv4/IPv6 and timestamps, bound input sizes, reject unsafe XML constructs, unknown provider fields and falsified source claims. Allow `CHAIN_ONLY` fallback when records lack genuine observed TXIDs.
- Build tests for duplicate relay, retransmission, NAT/host reuse, missing TXID, clock skew, false ownership, two sensors, post-cutoff evidence, J1 eligibility and chain-only fallback.
- Real wire capture/decoder may require explicit authorization and external devices: implement the **import/normalization contracts** fully; keep a real-capture acceptance item `EXTERNALLY_BLOCKED` until independent data is provided. Do not simulate real sensor validation.
- Commit: `feat(wire): validate and sessionize source-backed P2P relay evidence`.

### Phase 3 — Bitcoin/UTXO layer

- Extend `src/clarion/v4/ingest.py`, `v4/graph.py` and canonical Bitcoin Core adapter. Version and test raw-to-canonical translations for locally exported transaction records and block context.
- Preserve exact `(prev_txid, prev_vout)` links, unspent outputs and value conservation: sum(inputs) = sum(outputs) + fee **only when all input prevouts are available**. For unresolved prevouts, produce a completeness mask/abstention instead of inventing balances.
- Handle coinbase, unconfirmed/mempool, chain reorg/orphan events, nonstandard script/address-null outputs, multi-input/multi-output, decimals-to-satoshis, fee/weight, out-of-order input rows and bounded ingestion.
- Prove temporal/availability correctness, outpoint uniqueness and deterministic graph witnesses. Do not infer direct wallet ownership or globally complete wallet balances from a sample.
- Tests: bad units, negative/overflow values, duplicate vouts, invalid prevout, duplicate spend, fee mismatch, orphan/reorg, zero-value output, missing address, post-cutoff spend.
- Commit: `feat(chain): harden as-of Bitcoin UTXO reconstruction`.

### Phase 4 — join Bitcoin and network into typed temporal graph

- Join J0 exact UTXO value flow and J1 exact **observed** TXID relay only, with J2 contextual sessions/ASN/country and J3 optional research candidate edges separately labeled as hypotheses.
- Canonical six node types: Transaction, Address, Entity, Host, ASN, Country. Enforce strict allowlisted directed relations; provenance/source confidence class, event_time and available_at on every edge. Distinguish observed facts from proposed entity edges.
- Produce stable graph JSON and optional Parquet/DuckDB partitioned storage. Small fixture may use NetworkX; large data must use bounded graph queries/sampling, not a full multi-GB browser payload. Reconcile `v4/representation.py` and `v4/graph.py` with `schemas/graph`.
- Construct snapshot(T) only from evidence available at or before T, then prove snapshot(T) is unaffected by any later records. Never add IP->owns-wallet or country->crime edges.
- Connect graph output to existing API and React visualizer with selected transaction, evidence path and legend.
- **Acceptance:** mini24 dataset produces traceable spend links and source-tagged observed-relay links; zero owner edges; provenance is clickable/readable in case details; cutoff tests pass.
- Commit: `feat(graph): join temporal chain and observed-relay evidence`.

### Phase 5 — feature engineering, MCER and motif candidates

- Establish a versioned, time-safe feature registry with value/fee/fragmentation/fan-in/out, spend age, graph degree/hops, relay timing/session/coverage and optional ASN context. Maintain masks and required-source metadata; avoid future-label features and ID memorization.
- Build **MCER H1–H5 evidence proposals** with signed supports/conflicts, source independence, constraints, confidence caveats and conservative time-versioned partitions. CoinJoin/shared services/host context must never cause unqualified identity merges. Emit false-merge/coverage statistics only where ground truth exists.
- Implement explainable peel-like, fan-in/out, mixing-like, rapid layering, circular path and burst *candidate* motif witnesses with benign alternatives and known uncertainty, not accusations.
- Preserve `Δ` global independence gate and required case-specific Δ1–Δ5 interfaces; compute only from independently validated paired views, otherwise `ABSTAIN` with missing premises. Preserve `Π` per-component cost objectives/baselines; do not manufacture objectives; emit `ABSTAIN` when absent.
- **Acceptance:** table of features with time/source masks, reproducible motif witnesses, no unsupported MCER merge, validated abstention routing, held-out test negatives and source evidence exports.
- Commit: `feat(intelligence): integrate source-safe features, entity candidates and motifs`.

### Phase 6 — classical ML and training pipeline

- **Do not train/test on only 24 transactions.** Use 36+ generated cases to exercise machinery, then separately add genuine appropriately licensed labeled datasets after inspecting source/label meaning. Record input hashes and feature schema.
- Keep separate `UNSUPERVISED_ONLY` and `SUPERVISED_ELIGIBLE` gates. Build/verify LR, RF, Isolation Forest and optional LightGBM/OCSVM baselines, plus consistent source/feature availability masks. Treat novelty scores as novelty, not probabilities.
- Time-ordered grouped splits with as-of recomputation; training/validation/chronological final holdout separated by case and linked entities; no data preprocessing/normalization fitted on future holdouts; label availability must precede model cutoff. Use out-of-fold base predictions for the meta learner. Use calibration only with suitable independent validation.
- Implement deterministic experiment configs, seed, dependency versions, feature names, split IDs, source manifests, metrics (PR-AUC, ROC-AUC where meaningful, precision/recall/F1/confusion matrix, ranking metrics and confidence intervals), false-positive service cohort and training log artifacts.
- Persist safe versioned JSON baseline or safe model artifacts, hashes and explicit score types; reject untrusted pickles. Keep GPU optional, CPU baseline always runnable.
- **Acceptance:** 36-case pipeline trains and predicts with honest heldout report; mini24 runs inference/novelty without pretending the tiny fixture is a fair benchmark; repeated seed reproducibility and deliberately leaked feature rejection.
- Commit: `feat(ml): complete leakage-safe classical baseline and OOF stacking`.

### Phase 7 — graph ML

- Expand `src/clarion/v4/gnn_training.py` and `representation.py`; retain existing GraphSAGE edge-reconstruction **proxy** as proxy, not illicit-transaction detector.
- Create trainable GraphSAGE and GAT baselines, and an independently evaluated time-aware heterogeneous representation/model with six typed nodes and only admissible relations. If needed, use temporal neighbor sampling and self-supervised pretraining; never allow future-edge message passing or test labels in embeddings.
- On a sufficiently large independent, task-appropriate dataset, compare same exact train/validation/test split against classical baselines and simple structural features; evaluate by graph task with appropriate metrics. Report CPU/GPU/memory/time constraints and negative results. Do not claim improvement without measurements.
- Version model artifacts, feature/edge schemas, source hashes, cutoff, prediction API and uncertainty; no unsafely loaded serialized objects.
- **Acceptance:** opt-in CPU smoke, optional full GPU experiment, held-out metrics, deletion of post-cutoff edges leaves earlier predictions unchanged, UI marks models `NOT_CONFIGURED` until real checkpoint verified.
- Commit: `feat(gnn): add evaluable time-safe graph learning experiments`.

### Phase 8 — fused priority and propagation

- Separate **pass 1** local candidate score (0–75 review points; only causally independent eligible signals) and persist a frozen seed manifest.
- Run source-typed, direction-aware spend-graph propagation with at most six hops, service barriers/attenuation, uncertainty and path witnesses. Never propagate financial taint through IP, country, ASN or speculative ownership.
- **Pass 2** adds bounded propagation points (≤25), final score 0–100; forbid circular dependence on final score. Provide signal-level contribution, status/abstention and sensitivity/negative-control tests.
- Explain why a candidate ranked high without saying that it is criminal or assigning a fake probability. Validate graph/counterfactual alternatives when premises permit.
- **Acceptance:** invariant property tests for caps, monotonicity where applicable, source isolation, no risk inflation, service barriers, disconnected graphs and repeatability.
- Commit: `feat(scoring): integrate bounded non-circular lead prioritization`.

### Phase 9 — production-facing API, UI, case review and exports

- Extend the working FastAPI and React UI, not a disconnected mock. All screens use versioned API responses and predictable empty/error/loading states.
- Minimum screens: data source/import and readiness; overview and lead rankings; selected transaction + chronological timeline; typed graph exploration and edge evidence; MCER candidates/motifs; chain/wire observational comparison; Δ/Π evidence status; training/model results and provenance; bounded propagation path; case review/history; audit and JSON/CSV/PDF dossier export.
- Preserve minimal polished React/TypeScript visual consistency and responsive layouts. For a network/graph view use bounded node counts, server-side pagination, filters, time windows and lazy neighborhood queries.
- Keep local single-user review mutation token-gated and audit append-only; implement proper RBAC/auth only if deploying as a multi-user network service. Verify evidence hashes, safe file access, safe exports and cross-platform print/PDF rendering.
- All shown metrics/statuses must derive from actual verified artifacts; show `INSUFFICIENT_EVIDENCE` / `ABSTAIN` / `MODEL_NOT_CONNECTED` where warranted. No hardcoded "real-time" data.
- **Acceptance:** import mini24, inspect real generated graph/lead/dossier, change case review status and reload persisted history, export verifiable evidence, test UI e2e and API limits.
- Commit: `feat(console): complete investigator workflow and evidence-backed UI`.

### Phase 10 — DevOps, security, offline delivery and acceptance

- Make one repeatable local command and a Docker Compose path for the complete miniature vertical slice; document Windows/WSL/Linux setup, environment variables, ports, migration state and troubleshooting.
- Lock/pin dependencies and artifacts, CPU-only fallback, optional GPU profile, no outbound API/CDN at local inference, loopback default, read-only evidence plane, schema migration/backups, no secret leakage, security scanning and bounded resource use.
- CI jobs: pytest + ruff + compilation + fixture contract + temporal/no-ownership property tests + 36-case training/inference + v4 synthetic analyze + API review tests + frontend typecheck/build + Playwright smoke + Docker smoke + offline/no-egress tests + README generator checks. Skip optional GPU **explicitly**, not silently.
- Test clean-run from fresh clone with no existing generated artifacts, verify deterministic run manifest and evidence/export hash, rerun after restart, collect artifact evidence. Use synthetic benchmark only for software acceptance.
- **Acceptance:** a new contributor can execute full CLARION mini24 pipeline from README and get the same source-backed UI outputs, with no concealed Internet dependency or pre-existing local artifacts.
- Commit: `ci(release): certify repeatable offline mini24 end-to-end acceptance`.

### Phase 11 — independent data and research validation

- Import only explicitly licensed Bitcoin Core/benchmark/SIH data using audited mappings; separate network relay observations from wallets and transaction labels. Compare provenance, coverage, time semantics, class/selection bias and allowed claims.
- Train/evaluate across independently separated future periods and datasets where scientifically possible; perform leakage checks, group-bootstrap uncertainty, ablation (`chain-only` vs `chain+wire`), robustness, false merges, drift, hard negatives and causal claims audit.
- Scientifically unprovable current features (real originating relay attribution, independently verified Δ1–Δ5, Π true economic goals, real-world AML classification performance) must stay **EXTERNALLY_BLOCKED** or **ABSTAIN**. Implement interface, documentation and explicit prerequisite checklist; do not invent evidence or performance.
- Update `docs/IMPLEMENTATION_CHECKLIST.md` item by item and final scientific/readiness statement reflecting what was actually tested, not simply “172/172 complete”.
- Commit: `docs(validation): publish reproducible results and evidence gates`.

## D. Phase acceptance and git discipline

Before EACH phase: state exact changed files, tests, expected artifacts, dependencies, and whether external source data is available. After EACH phase: run targeted unit + integration tests; show actual command output/results; run existing full tests when feasible; update folder README if needed (repository uses generated folder documentation—run `python scripts/docs/generate_folder_readmes.py --write` and `--check`); update 172-requirement tracker with code/test references; commit to the working branch with the phase message. Never skip a failing test by deletion; fix root cause or mark documented blocker.

Push commits after each phase, not one enormous unreviewable final commit. If possible use one PR per connected vertical slice into `main` with readable diff, explicit test summary, known limitations and no conflicts. Merge only when CI and safety gates pass. Do not force a merge or disable checks to satisfy completion appearance. Keep the branch synchronized with `main`; preserve collaborator work.

The final integration report **must include**: base and final commit SHAs; link to each PR/merge; exactly what changed and runnable CLI; confirmed 24-row transaction fixture counts and associated table sizes; 36+ case training report with explicit synthetic caveat; each core pipeline artifact path; UI/demo instructions; tested commands and pass/fail counts; 172 requirement statuses with links; genuinely missing external evidence; limitations; whether release is GO (for synthetic software demo only) or NO-GO (for real-world detection). The final README must tell a new developer the correct order:

**Baseline audit → 24-row dataset → network observations → Bitcoin/UTXO → cross-layer temporal graph → features/MCER/motifs → classical models → GNN → scoring/propagation → dashboard/cases → offline acceptance → research validation.**

## E. Authoritative commands to verify (fix if necessary)

~~~bash
python -m pytest -q
python -m compileall -q src
python -m ruff check src/clarion/v4 scripts/v4_pipeline.py tests/v4
python -m clarion.cli.main generate-demo --out data/generated/mini24 --cases 6 --seed 26
python -m clarion.cli.main validate --data data/generated/mini24
python scripts/v4_pipeline.py analyze --data data/generated/mini24 --out artifacts/mini24 --licence SYNTHETIC_LOCAL --origin CLARION_GENERATOR
python scripts/full_demo_pipeline.py --out artifacts/full_demo --cases 36 --seed 26
python scripts/submission_demo.py run --out artifacts/submission_demo --cases 10 --seed 26
python scripts/release/check_submission.py --run artifacts/submission_demo/investigation
python scripts/docs/generate_folder_readmes.py --check
cd frontend && npm install --no-audit --no-fund && npm run typecheck && npm run build
~~~

Commands are intent and starting points from the inspected repository, not claims newly executed by the author of this prompt. When the actual code supports different flags, use `--help` and correct docs/tests together.

## F. Agent's immediate first deliverable

**Do not ask the user for new architectural ideas or another generic plan.** Begin by verifying the current repo and code, and implement **Phase 1** completely: a committed, source-hashed, tested **24-transaction** fictional mini24 fixture (with all associated CSV tables and source/truth separation), running through existing validation and canonical analysis, with a real commit and precise acceptance output. Continue to Phase 2 only after Phase 1 passes. Persist working changes and meaningful commits for subsequent phases until the synthetic end-to-end system is integrated. Where real data/evidence is unavailable, finish executable evidence-gated interfaces and report those specific blocks honestly rather than fabricating validation.


---

## Autonomous P0–P9 handoff (5 November 2026)

The authoritative phase sequence is P0–P9 in `CLARION_V4_MASTER_IMPLEMENTATION_PLAN.md`. Read `AUTONOMOUS_EXECUTION_CONTRACT.md` and maintain `../progress/PHASE_IMPLEMENTATION_LEDGER.md` as the single phase-level status ledger. The older 11 work packages map into P0–P9; do not create Phase 10/11 or treat legacy P0–P5 playbooks as competing roadmaps.

**Do not ask the user to choose routine libraries, helper names, tests, files or ordinary implementation details.** Inspect existing code and tests, choose the simplest consistent implementation, record the decision and proceed. Pause only for legal/permission/account authorization, destructive actions or an architecture-changing research decision not resolved by the approved plan. If real data is missing, complete the synthetic/chain-only fallback and mark only dependent claims DATA_BLOCKED.

Execute P0 through P9 in order. P0 must refresh the main SHA, map all 172 REQ IDs to actual source owners/tests, run and log baseline checks, inventory data rights/semantics, reconcile Python/npm dependencies and freeze the first slice. P1 must deliver deterministic fictional mini24 with exactly 24 transaction records, CSV/JSON/XML parity, provenance, integer satoshi/outpoint invariants and synthetic-truth isolation. The subsequent phase gates, autonomous rules, environment caveats and evidence requirements are defined in the contract and ledger.

**Environment caveat at 5 Nov 2026:** `uv.lock` does not include all v4/demo extras from `requirements-v4.txt` and `requirements-demo.txt`; frontend `package-lock.json` is absent. Follow `docs/LOCAL_TESTING.md` meanwhile. Do not treat `uv sync --locked` alone as a complete v4 setup or run `npm ci` before a lockfile exists. Never claim a test passed unless executed.
