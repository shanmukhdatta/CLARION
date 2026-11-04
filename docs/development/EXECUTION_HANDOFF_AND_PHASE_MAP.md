# CLARION v4 — Autonomous execution handoff and phase map

> **Purpose:** remove ambiguity for the next repository-aware implementation agent. This document supplements, and does not replace, the technical design or the implementation prompt.
> **Target branch:** `main`. **Status:** execution instructions; no claim that the listed work has been implemented or tested.

## 1. Which document is authoritative?

The repository contains several roadmaps written at different levels of detail. Use them in this order:

1. **Execution authority:** [`AGENT_EXECUTION_PROMPT.md`](AGENT_EXECUTION_PROMPT.md). It defines the required code-first sequence, phase acceptance, commit discipline and final report.
2. **Technical design authority:** [`CLARION_V4_MASTER_IMPLEMENTATION_PLAN.md`](CLARION_V4_MASTER_IMPLEMENTATION_PLAN.md). It defines the system architecture, algorithms, interfaces, datasets, design constraints and P0–P9 planning view.
3. **Requirement inventory:** [`docs/IMPLEMENTATION_CHECKLIST.md`](../IMPLEMENTATION_CHECKLIST.md) and the current source-to-requirement audit. These define the scope and evidence status.
4. **Environment and command reference:** [`docs/LOCAL_TESTING.md`](../LOCAL_TESTING.md), checked against the current checkout before use.
5. Older playbooks and progress notes are useful historical/contextual material. They must not override the execution prompt or silently introduce a competing phase order.

The execution prompt currently numbers work as Phase 1–11 (after the baseline audit); the master plan uses P0–P9. These are different planning granularities, not two independent implementation programmes. Use the execution prompt's sequence for actual work and the mapping below to locate its corresponding master-plan blocks.

## 2. Phase crosswalk

| Execution sequence (follow this) | Master-plan area | Required outcome / gate |
|---|---|---|
| Baseline / Phase 0 | P0 | Inspect current `main`, record exact HEAD, working tree, source audit, environment and test baseline. Do not trust historical status counts as current test results. |
| Phase 1 — mini24 fixture | P1 | Exactly 24 transaction records; associated one-to-many tables; deterministic generation; source manifest and hashes; isolated synthetic truth; validation and chain-only analysis. |
| Phase 2 — network/P2P | P2 | Source-backed observation import, decoding provenance, timestamp/coverage quality and safe CHAIN_ONLY fallback. Real capture remains externally blocked without authorized evidence. |
| Phase 3 — Bitcoin/UTXO | P2 | Exact prevout/outpoint reconstruction, satoshi accounting, completeness masks and as-of correctness. |
| Phase 4 — cross-layer graph | P3 | Six typed node classes, allowlisted relations, evidence provenance, availability-time cutoffs and no host-to-wallet ownership edge. |
| Phase 5 — features, MCER and motifs | P3–P4 | Versioned causal features, conservative candidate clusters, witness-backed motifs and explicit benign alternatives. |
| Phase 6 — classical ML and stack | P5 | 36+ synthetic-case engineering demo, valid chronological/grouped splits, leakage-safe OOF stack and honest score types. |
| Phase 7 — graph ML | P5 | Optional GraphSAGE/GAT experiments compared on the same eligible task/splits; CPU path remains available. |
| Phase 8 — fusion and propagation | P6–P7 | Frozen pass-1 seeds, bounded six-hop MLRP, no cross-customer infrastructure contagion and ≤25/100 propagation contribution. |
| Phase 9 — API/UI/cases | P8 | Existing API and React app connected to actual artifacts, bounded queries, review persistence and auditable exports. |
| Phase 10 — offline acceptance | P9 | Reproducible clean-checkout synthetic vertical slice, dependency/artifact lock, offline/no-egress checks and release evidence. |
| Phase 11 — independent research validation | P9 | Real benchmark/SIH/wire claims only where permissions, label semantics, independent evidence and valid holdouts support them; otherwise retain DATA-BLOCKED/ABSTAIN. |

**Important:** The crosswalk is a navigation aid. Do not mark a master-plan phase complete merely because its corresponding execution phase has started.

## 3. Autonomous execution policy

The implementation agent should make ordinary, reversible engineering decisions without repeatedly asking the user. It must first inspect existing code and reuse canonical modules in `src/clarion/v4/`, `src/clarion/application/`, `src/clarion/api/` and `frontend/`. Do not create parallel implementations because an older blueprint path is empty.

### Proceed independently when

- choosing internal function names, test organization, small refactors and deterministic fixture details consistent with existing contracts;
- adding tests, documentation, type annotations, validation and error handling;
- selecting a CPU-compatible baseline or a synthetic fallback that is explicitly labelled;
- fixing dependency metadata when the intended package/version can be established from project constraints and compatibility tests.

### Stop and report a blocker when

- SIH or third-party data permissions, credentials, private captures or licensing are required;
- an undocumented organizer field or domain meaning changes the scientific interpretation;
- real network capture or collection requires authorization not already granted;
- a major research premise, score interpretation or irreversible data migration is unresolved;
- a test failure reveals a safety, provenance, leakage or evidence-integrity defect that cannot be fixed without changing the design.

Do not fabricate data, source provenance, model metrics, test output, sensor observations, ownership, labels or research conclusions. If evidence is absent, implement the interface and report the exact missing prerequisite; return CHAIN_ONLY, NOVELTY_ONLY, DATA-BLOCKED or ABSTAIN as appropriate.

## 4. Required phase task ledger

Maintain a checked-in ledger (or update the existing requirement tracker if it can represent this information without duplicating status) with one row per independently reviewable task:

| Field | Required content |
|---|---|
| Task ID | Stable ID, e.g. `P1-FIX-001` |
| Scope | One observable behavior, not a broad feature name |
| Dependencies | Task IDs and required input/schema versions |
| Source target | Existing file/function to inspect first; proposed new path only if needed |
| Acceptance | Exact positive and negative behavior |
| Test evidence | Test ID, command actually run, result and environment |
| Artifact | Output path and SHA-256 where applicable |
| Status | DESIGN / NOT STARTED / IMPLEMENTED / TESTED / VERIFIED / PARTIAL / DATA-BLOCKED |
| Commit | Commit SHA containing the accepted change |
| Blocker | Exact missing external permission/data/decision, or `None` |

Status rules: IMPLEMENTED means code exists; TESTED means named tests passed; VERIFIED means the complete stated acceptance gate passed and evidence is retained. A passing synthetic test does not verify a real-world research claim.

## 5. Environment and reproducibility gates

The next agent must re-check these items on the live checkout before relying on historical notes:

- Compare `pyproject.toml`, `requirements-v4.txt` and `uv.lock`. The previous review observed that the lockfile did not contain every package listed by the v4 requirements file. Do not assume `uv sync --locked` installs the full v4 stack until this is resolved and tested.
- Choose one authoritative dependency declaration. Add runtime/dev/optional groups deliberately, regenerate and commit `uv.lock`, and verify a clean environment can install from the lock. Avoid maintaining conflicting unpinned dependency lists.
- The previous review found no committed frontend `package-lock.json`. Until a lockfile exists, use `npm install`; after intentionally generating and committing the lockfile, use `npm ci` for reproducible CI/clean installs.
- Reconcile stale branch names in beginner notes with the actual target branch `main`. Use the current [local testing guide](../LOCAL_TESTING.md) only after checking its commands against `--help`.
- Record Python and Node versions, OS, dependency lock hash, CPU/GPU profile, exact HEAD SHA and test commands in the run manifest.
- Run baseline tests before edits and repeat affected tests after each meaningful change. Do not silently skip failed tests or report commands as passed when they were not executed.

Suggested baseline sequence (verify availability and current flags first):

```bash
git status --short --branch
git rev-parse HEAD
python --version
uv --version
node --version
npm --version
uv sync --locked
uv run python -m pytest -q
uv run python -m compileall -q src
cd frontend && npm install --no-audit --no-fund
npm run typecheck
npm run build
```

If a command is unavailable or fails, capture its actual output and diagnose it before proceeding. Do not treat this suggested sequence as evidence that it has already passed.

## 6. Phase 1 — exact first implementation slice

Do not start with model training, GNNs, scoring, MLRP or dashboard redesign. The first implementation milestone is the mini24 fixture and a working chain-only path.

Expected fixture directory: `data/samples/mini24/`

Expected files:

- `transactions.csv` — exactly 24 transaction records;
- `inputs.csv` and `outputs.csv` — one-to-many tables with exact outpoint references and integer satoshis;
- `observations.csv` — synthetic observations only, clearly labelled and never represented as real sensor capture;
- `truth_SYNTHETIC_ONLY.csv` — sealed synthetic labels, excluded from ingestion/features/inference/UI;
- `source_manifest.json` — schema/version, generator/fixture revision, source identity, rights/licence, record counts and file hashes;
- `README.md` — field semantics, generation/reproduction instructions, limitations and expected outputs.

Acceptance must include all of the following:

1. Exactly 24 transaction rows, excluding headers; auxiliary table row counts are determined by their one-to-many relationships.
2. Deterministic fixture contents for a fixed seed, excluding explicitly documented run-time metadata.
3. Unique well-formed TXIDs and valid referenced `txid:vout` pairs; no duplicate spend within the fixture.
4. Nonnegative integer satoshi values and conservation checks only where all input prevouts are known. Unknown inputs must not be silently treated as zero.
5. Timezone-aware event/availability timestamps, source IDs and provenance references.
6. Truth-sidecar separation tests proving synthetic truth cannot leak into canonical graph, feature, prediction or UI inputs.
7. Positive and negative parser/validation tests, including malformed values, duplicate spends, missing prevouts and post-cutoff evidence.
8. Successful chain-only analysis with a traceable graph/evidence output and an explicit reason that cross-layer inference is unavailable or synthetic-only.
9. Repeated generation/validation with matching canonical digests and retained command output.

Only after this gate passes should Phase 2 begin. The exact Phase 1 acceptance contract in `AGENT_EXECUTION_PROMPT.md` remains controlling if a detail here differs.

## 7. Commit, review and reporting discipline

- Work on `main` only when explicitly instructed and the repository workflow permits it; otherwise use a reviewable feature branch and PR. Never overwrite collaborator changes or force-push.
- Before a phase, state scope, dependencies, expected artifacts and tests. After it, report changed files, commands actually run, pass/fail counts, artifact hashes, limitations and commit SHA.
- Commit one coherent phase or vertical slice at a time. Update the relevant requirement IDs and folder README; run the folder README generator/check only when source/documentation changes require it.
- Do not merge merely to make the branch appear complete. Preserve CI and review gates.
- Final report must distinguish: code implemented, synthetic software acceptance passed, real-data validation passed, and external evidence blocked. These are four different claims.

## 8. Non-negotiable evidence semantics

- A relay observation is evidence that the named sensor observed the specified relay event under recorded conditions; it does not prove transaction origin, wallet control or person identity.
- MCER produces candidate clusters/entities, not verified people.
- Bitcoin values are integer satoshis; exact spends use outpoints.
- Event time and availability time remain separate; future-available records cannot affect earlier snapshots.
- Missing evidence is not zero. Unsupported `Δ` and `Π` components abstain.
- Synthetic labels remain synthetic and are never treated as external truth.
- Novelty/review-priority scores are not criminal probabilities.
- Financial propagation must not cross shared IP/ASN/Country infrastructure into unrelated customers. Country is context only.
- Inference and investigation UI must work offline with bundled assets and no required external API/CDN.
