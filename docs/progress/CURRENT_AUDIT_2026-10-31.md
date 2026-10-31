# CLARION repository status and restart audit — 31 October 2026

> Scope: inspected GitHub default branch `main` at commit `34739e433a60534775f014f400166ef9343464a4`. This is a source/documentation + existing GitHub Actions evidence audit, **not** a fresh local code execution or empirical real-world evaluation. Update this file after every implementation phase.

## Executive finding

CLARION has a runnable **fictional/synthetic research demonstration**, not an independently validated production Bitcoin financial-crime detector. Reuse implemented modules and add missing contracts, fixtures, functionality and test evidence incrementally. Do not rewrite a working flow based only on an older README declaring that it is a stub.

- Repository: https://github.com/shanmukhdatta/CLARION
- Current main inspected: `34739e4` (25 October 2026).
- GitHub Actions on that commit: `CLARION CI` run 40194320232, `CLARION security checks` run 40194320242, and `CLARION v4 validation` run 40194320126 report success. This verifies their configured jobs, **not** the full 172-requirement system.
- Requirements ledger (see `docs/IMPLEMENTATION_CHECKLIST.md`): **59 implemented and narrowly tested; 39 written but not fully accepted; 37 partial; 29 missing; 8 externally blocked = 172**. These numbers are documented classifications, not a measured percent-complete claim.
- A self-contained, checked-in, 20–30 transaction starter fixture is **not currently present** under `data/samples/`. The existing generator and 36-case demo are not the same artifact.

## Evidence and entrypoints

| Area | Existing runnable/meaningful code | Remaining boundary or blocker |
|---|---|---|
| Synthetic generator | `src/clarion/application/engine.py`, `clarion generate-demo` | Minimal reviewed 24-tx fixture, explicit fixture schema, more benign hard negatives |
| Ingestion and schema | `src/clarion/v4/contracts.py`, `ingest.py` | Verified SIH/provider fields, clocks, parser security and independent permissions |
| Chain / UTXO | `src/clarion/v4/graph.py`, `ingest.import_bitcoin_core_tx` | Real coinbase/reorg/script/mempool coverage and large source validation |
| Network observation | `src/clarion/v4/wire_sessions.py` and `contracts.WireObservation` | Real authorized instrumented peer observations, decoder provenance and capture bias |
| Cross-layer graph | `src/clarion/v4/graph.py`, `representation.py` | Full temporal hetero training and precise candidate edge confidence |
| Features / MCER / motifs | `graph.feature_rows`, `mcer.py`, `analysis.py`, `motifs_extended.py` | H3–H5 independent calibration; false merges; wider motifs/negative controls |
| Models / evaluation | `v4/ml.py`, `model_artifact.py`, `gnn_training.py`, `evaluation.py` | Model selection, independent temporal heldouts, real label audit, GNN superiority unproven |
| Delta / Pi | `v4/signals.py` | Case-local delta components and economic-objective verification missing; ABSTAIN is correct |
| Priority / propagation | `v4/analysis.py`, `pipeline.py` | Full source-separated MLRP, service barriers, sensitivity and false-positive evaluation |
| Console and evidence | `src/clarion/api/main.py`, `api/reviews.py`, `frontend/src/app/App.tsx` | Full large-graph visualization, public/RBAC deployment, final export/release QA |
| Release | Dockerfile, compose.yaml, CI, docs, scripts/release | Fully offline release installation, signing, supply-chain, broader E2E security validation |

**Legacy blueprint trap:** some files in `src/clarion/ingestion/adapters/`, `src/clarion/synthetic/`, `src/clarion/representation/`, `src/clarion/features/` and elsewhere are explicitly comment-only placeholders. Some similarly named implementations **do exist** in `src/clarion/v4/` or `src/clarion/application/`. Before filling a stub, choose one canonical implementation, integrate it and test the public import path.

**Doc currency trap:** `docs/development/implementation-playbook.md` describes an older scaffold-only state; `docs/architecture/FEATURE_IMPLEMENTATION_AUDIT.md` is explicitly tied to an older October 22 commit. Use this audit and the live 172-row checklist as starting points, and refresh statuses against current source/CI rather than blindly trusting historical paragraphs.

## Correct first-run distinction

**Mini fixture:** `clarion generate-demo --out data/generated/mini24 --cases 6 --seed 26` currently generates **24 transaction records** because `application.engine.generate` creates one fictional funding transaction and three spends per case. Associated inputs, outputs and wire-observation tables have different row counts; do not represent the entire multi-table dataset as just 24 rows. Investigate deterministically with canonical v4 pipeline and verify all expected outputs; promote a reviewed and deterministic fixture to `data/samples/mini24/`.

**Training fixture:** `application.training_demo.train` requires at least **30 distinct synthetic cases and 75 labeled spend transactions**; the 24-transaction mini dataset is **not** a viable credible training benchmark. Run `scripts/full_demo_pipeline.py --cases 36` or a larger separate evidence-licensed dataset to validate machinery, and maintain independent future holdouts. Any metrics from this generator are *synthetic-only*.

## Restart priority and gates

1. P0 baseline: record current SHA and CI, run locally if permitted, map 172 requirements to actual owners/tests, check for regressions.
2. P1 frozen miniature fixture: exactly 24 canonical transaction rows plus coherent related tables, negative cases, ground-truth sidecar withheld from inference, manifest/hash/schema tests and committed sample.
3. P2 network observation slice: source-tagged sensor/TXID/time/port facts, dedupe, sessions, timezone/clock/capture completeness, exact observed-relay interpretation; no IP ownership inference.
4. P3 Bitcoin slice: exact TXID/vout spends, satoshi conservation, unspent and unresolved outpoints, scripts/coinbase/fee/reorg cases and auditable graph.
5. P4 graph join: typed temporal six-node-type graph, joined J0–J3 evidence tiers, source IDs, cutoff causality, graph serialization and visualization feed.
6. P5 feature engineering and candidate intelligence: chain/wire feature registry and masks; MCER H1–H5 evidence with constraints/abstain; motif witness paths; Δ/Π evidence-gated status.
7. P6 classical ML: 36+ synthetic cases for machinery; chrono/group-safe LR, RF, IF, OOF stack; data leak guards and honest holdout report.
8. P7 graph ML: controlled GraphSAGE/GAT, temporal hetero model, identical split comparison, CPU fallback and persisted inference artifact; no unsupported improvements asserted.
9. P8 final scoring: freeze local seeds, bounded forward/backward verified value propagation, service barriers, capped second pass, typed explanation; no host/country monetary taint.
10. P9 integration: FastAPI, React investigator graph/table/timeline, case review events, JSON/CSV/PDF provenance and honest model availability.
11. P10 operational acceptance: offline Linux/containers, safe local inference, parsing security, retention controls, docs/CI/security/e2e and clean-room replay.
12. P11 scientific readiness: real authorized independently validated data/labels, ablation, sensitivity, uncertainty and release evidence; mark `EXTERNALLY_BLOCKED` instead of fabricating unavailable information.

Each phase: **inspect → implement one vertical feature slice → test → update documentation and requirement rows → commit**. See `docs/development/AGENT_EXECUTION_PROMPT.md` for file-level tasks, commands, pass gates and commit guidance.

## Strict invariant list

- Observed relay host ≠ transaction origin ≠ wallet/address owner ≠ guilt.
- Use time-available evidence only; historical snapshots cannot read later events or labels.
- Amounts are integer satoshis; link spending through exact prior outpoints, not invented direct owner transfers.
- Distinguish unsupervised novelty/priority from independently calibrated real-world crime probability.
- Always abstain from Δ/Π when independent pairing/economic goals do not exist.
- Never allow Country/ASN/Host evidence to create direct financial ownership or taint edges.
- Pass-one local score freezes before bounded propagation, which contributes at most 25 final points.
- No real secrets, private IP captures, confidential evidence, or unauthorized datasets in Git.
- No network requirement for a packaged local inference session.
- All acceptance claims are limited to tests actually executed or recorded GitHub Actions results.

## Known successful CI references

- https://github.com/shanmukhdatta/CLARION/actions/runs/40194320232
- https://github.com/shanmukhdatta/CLARION/actions/runs/40194320242
- https://github.com/shanmukhdatta/CLARION/actions/runs/40194320126
