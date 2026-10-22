# CLARION — Every-folder technical README index

**Coverage:** 103 tracked folders; each should contain `README.md`.
Generated deterministically from Git-tracked file paths. This is a navigation index, **not proof of feature completion**.

## Contents

- [.github](#github)
- [artifacts](#artifacts)
- [configs](#configs)
- [data](#data)
- [deploy](#deploy)
- [docs](#docs)
- [experiments](#experiments)
- [frontend](#frontend)
- [schemas](#schemas)
- [scripts](#scripts)
- [src](#src)
- [tests](#tests)

## .github

- [`.github/README.md`](../.github/README.md) — CI and change governance.
- [`.github/ISSUE_TEMPLATE/README.md`](../.github/ISSUE_TEMPLATE/README.md) — Consistent research and implementation issue intake.
- [`.github/workflows/README.md`](../.github/workflows/README.md) — Install dependencies and check code, UI, offline security and synthetic data.

## artifacts

- [`artifacts/README.md`](../artifacts/README.md) — Organize evidence products and model outputs.
- [`artifacts/models/README.md`](../artifacts/models/README.md) — Keep versioned model manifests.
- [`artifacts/reports/README.md`](../artifacts/reports/README.md) — Store signed/evidence-linked dossiers.

## configs

- [`configs/README.md`](../configs/README.md) — Versioned experiments, ingest and runtime boundaries.
- [`configs/ingestion/README.md`](../configs/ingestion/README.md) — Explicit column mapping and quality gates.
- [`configs/models/README.md`](../configs/models/README.md) — Configurable ML, MCER and graph training settings.
- [`configs/profiles/README.md`](../configs/profiles/README.md) — Offline, synthetic and production profiles.
- [`configs/security/README.md`](../configs/security/README.md) — Local access, redaction and parsing constraints.

## data

- [`data/README.md`](../data/README.md) — Raw/normalized/split organization.
- [`data/external/README.md`](../data/external/README.md) — Keep original source immutable.
- [`data/manifests/README.md`](../data/manifests/README.md) — Track provenance and source versions.
- [`data/samples/README.md`](../data/samples/README.md) — Schema and pipeline teaching fixtures.

## deploy

- [`deploy/README.md`](../deploy/README.md) — Packaging, install and recovery strategy.
- [`deploy/containers/README.md`](../deploy/containers/README.md) — Local isolation and reproducible builds.
- [`deploy/linux/README.md`](../deploy/linux/README.md) — Single-host offline installation and upgrade.

## docs

- [`docs/README.md`](../docs/README.md) — Preserve decisions and observed implementation status.
- [`docs/adr/README.md`](../docs/adr/README.md) — Record approved architectural reasoning.
- [`docs/architecture/README.md`](../docs/architecture/README.md) — Trace features to v4 code and outstanding research.
- [`docs/data/README.md`](../docs/data/README.md) — Describe ingest, joins, provenance and legal source.
- [`docs/development/README.md`](../docs/development/README.md) — Help beginners reproduce the demo and later validate v4.
- [`docs/ml/README.md`](../docs/ml/README.md) — Define chronological splits, MCER and model-selection tests.
- [`docs/operations/README.md`](../docs/operations/README.md) — Evidence recovery, audit, review and case handling.
- [`docs/progress/README.md`](../docs/progress/README.md) — Document what is complete versus unfinished.
- [`docs/security/README.md`](../docs/security/README.md) — Document prohibited cross-layer identity assumptions.

## experiments

- [`experiments/README.md`](../experiments/README.md) — Track study design and reproducibility.
- [`experiments/ablations/README.md`](../experiments/ablations/README.md) — Compare model components at identical subject/time splits.
- [`experiments/benchmarks/README.md`](../experiments/benchmarks/README.md) — Benchmark setup and sealed holdouts.

## frontend

- [`frontend/README.md`](../frontend/README.md) — Build responsive terracotta/ivory read-only workspace.
- [`frontend/public/README.md`](../frontend/public/README.md) — Plan packaged icons/assets.
- [`frontend/src/README.md`](../frontend/src/README.md) — UI root, components, tokens and feature boundaries.
- [`frontend/src/app/README.md`](../frontend/src/app/README.md) — React navigation, tables, dossier and graph preview.
- [`frontend/src/components/README.md`](../frontend/src/components/README.md) — Reusable evidence indicators and risk scales (planned).
- [`frontend/src/features/README.md`](../frontend/src/features/README.md) — Page-level feature subdivision (planned).
- [`frontend/src/features/audit/README.md`](../frontend/src/features/audit/README.md) — Plan the evidence audits component layer.
- [`frontend/src/features/cases/README.md`](../frontend/src/features/cases/README.md) — Plan the case dossiers component layer.
- [`frontend/src/features/entities/README.md`](../frontend/src/features/entities/README.md) — Plan the candidate entity hypotheses component layer.
- [`frontend/src/features/graph/README.md`](../frontend/src/features/graph/README.md) — Plan the evidence graph component layer.
- [`frontend/src/features/leads/README.md`](../frontend/src/features/leads/README.md) — Plan the lead queue component layer.
- [`frontend/src/features/models/README.md`](../frontend/src/features/models/README.md) — Plan the model diagnostics component layer.
- [`frontend/src/features/patterns/README.md`](../frontend/src/features/patterns/README.md) — Plan the motif investigation component layer.
- [`frontend/src/features/propagation/README.md`](../frontend/src/features/propagation/README.md) — Plan the exposure paths component layer.
- [`frontend/src/features/readiness/README.md`](../frontend/src/features/readiness/README.md) — Plan the readiness gates component layer.
- [`frontend/src/features/signals/README.md`](../frontend/src/features/signals/README.md) — Plan the δ/π evidence status component layer.
- [`frontend/src/features/timeline/README.md`](../frontend/src/features/timeline/README.md) — Plan the temporal graph navigation component layer.
- [`frontend/src/lib/README.md`](../frontend/src/lib/README.md) — Typed fetch helpers and score types.
- [`frontend/src/styles/README.md`](../frontend/src/styles/README.md) — Responsive terracotta/ivory and print styles.

## schemas

- [`schemas/README.md`](../schemas/README.md) — Document machine-readable contract design.
- [`schemas/api/README.md`](../schemas/api/README.md) — Define JSON request/response fields.
- [`schemas/graph/README.md`](../schemas/graph/README.md) — Define six node categories and allowed directed relations.
- [`schemas/normalized/README.md`](../schemas/normalized/README.md) — Define unit-bearing, UTC available-at records.
- [`schemas/raw/README.md`](../schemas/raw/README.md) — Define source-specific format intake.

## scripts

- [`scripts/README.md`](../scripts/README.md) — Generate fixtures, import, train and produce reports.
- [`scripts/data/README.md`](../scripts/data/README.md) — Generate and normalize approved local data.
- [`scripts/docs/README.md`](../scripts/docs/README.md) — Generate folder maps and diagrams idempotently.
- [`scripts/release/README.md`](../scripts/release/README.md) — Plan reproducible offline release and smoke checks.
- [`scripts/train/README.md`](../scripts/train/README.md) — Train supervised OOF baselines and optional research challengers.

## src

- [`src/README.md`](../src/README.md) — Python package roots and experimental modules.
- [`src/clarion/README.md`](../src/clarion/README.md) — Route between legacy demo and separate new v4 functions.
- [`src/clarion/api/README.md`](../src/clarion/api/README.md) — Read-only FastAPI for bundled React and case examination.
- [`src/clarion/api/routers/README.md`](../src/clarion/api/routers/README.md) — Future split routers for leads/graph/cases/models.
- [`src/clarion/application/README.md`](../src/clarion/application/README.md) — Coordinate demo generation, validation, training and review.
- [`src/clarion/chain/README.md`](../src/clarion/chain/README.md) — UTXO prevout/value validation.
- [`src/clarion/cli/README.md`](../src/clarion/cli/README.md) — Dispatch explicit generate/train/investigate/serve commands.
- [`src/clarion/core/README.md`](../src/clarion/core/README.md) — Shared settings/validation foundations.
- [`src/clarion/detection/README.md`](../src/clarion/detection/README.md) — Four-family detector design and OOF stack.
- [`src/clarion/divergence/README.md`](../src/clarion/divergence/README.md) — Estimate Δ residual dependences.
- [`src/clarion/domain/README.md`](../src/clarion/domain/README.md) — Define stable domain boundaries.
- [`src/clarion/entity_resolution/README.md`](../src/clarion/entity_resolution/README.md) — Compute conservative MCER proposals and lineage.
- [`src/clarion/evaluation/README.md`](../src/clarion/evaluation/README.md) — Bootstrap, leakage, calibration and false-positive tests.
- [`src/clarion/expenditure/README.md`](../src/clarion/expenditure/README.md) — Compare unit-consistent Π components.
- [`src/clarion/explanations/README.md`](../src/clarion/explanations/README.md) — Explain contributions and hypothetical alternatives.
- [`src/clarion/features/README.md`](../src/clarion/features/README.md) — Compute nullable chain, wire, temporal features.
- [`src/clarion/fusion/README.md`](../src/clarion/fusion/README.md) — Freeze local priority then cap second-pass influence.
- [`src/clarion/graph/README.md`](../src/clarion/graph/README.md) — Build temporal typed evidence structure.
- [`src/clarion/ingestion/README.md`](../src/clarion/ingestion/README.md) — Bounded parsing and source validation.
- [`src/clarion/ingestion/adapters/README.md`](../src/clarion/ingestion/adapters/README.md) — Convert source records only with explicit mappings.
- [`src/clarion/observability/README.md`](../src/clarion/observability/README.md) — Track failures without leaking sensitive data.
- [`src/clarion/patterns/README.md`](../src/clarion/patterns/README.md) — Detect structural peel, fan-in/out, mixing-like candidates.
- [`src/clarion/propagation/README.md`](../src/clarion/propagation/README.md) — Propagate value-backed exposure ≤6 hops.
- [`src/clarion/readiness/README.md`](../src/clarion/readiness/README.md) — Route chain-only/unsupervised/conditionally cross-layer.
- [`src/clarion/reporting/README.md`](../src/clarion/reporting/README.md) — Offline JSON/CSV/PDF representations.
- [`src/clarion/representation/README.md`](../src/clarion/representation/README.md) — GraphSAGE/GAT and heterogeneous representations.
- [`src/clarion/security/README.md`](../src/clarion/security/README.md) — Reject unsafe inputs and redact optional host fields.
- [`src/clarion/storage/README.md`](../src/clarion/storage/README.md) — Offline Parquet/DuckDB/SQLite contracts.
- [`src/clarion/synthetic/README.md`](../src/clarion/synthetic/README.md) — Create fictional evidence and held-back ground truth.
- [`src/clarion/training/README.md`](../src/clarion/training/README.md) — Design folds, training, registry and drift audits.
- [`src/clarion/v4/README.md`](../src/clarion/v4/README.md) — Import → as-of UTXO graph → uncertain evidence → novelty and leads.
- [`src/clarion/wire/README.md`](../src/clarion/wire/README.md) — Time-valid observed-TXID join and context.

## tests

- [`tests/README.md`](../tests/README.md) — Test correctness, offline behavior and security expectations.
- [`tests/adversarial/README.md`](../tests/adversarial/README.md) — Reject false attribution and parser abuse.
- [`tests/contracts/README.md`](../tests/contracts/README.md) — Compatibility and validation tests.
- [`tests/e2e/README.md`](../tests/e2e/README.md) — Planned browser flows.
- [`tests/fixtures/README.md`](../tests/fixtures/README.md) — Fixture provenance and index.
- [`tests/integration/README.md`](../tests/integration/README.md) — Stage-to-stage assertions.
- [`tests/leakage/README.md`](../tests/leakage/README.md) — Guard feature/label future leakage.
- [`tests/offline/README.md`](../tests/offline/README.md) — Assert code does not unexpectedly open outbound sockets.
- [`tests/performance/README.md`](../tests/performance/README.md) — Planned CPU/memory and large-graph tests.
- [`tests/property/README.md`](../tests/property/README.md) — Property test hypotheses.
- [`tests/unit/README.md`](../tests/unit/README.md) — Base unit testing.
- [`tests/v4/README.md`](../tests/v4/README.md) — Check conservation, no ownership claims, null Π/Δ, and bounded scoring.
