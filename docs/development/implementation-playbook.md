# CLARION v4 — Beginner-to-implementation playbook

> **Status: IMPLEMENTATION PLAN, not implemented functionality.** This guide tells a new contributor what to build, in what order, which tools to choose, which datasets can and cannot answer each research question, how to train/evaluate models, and what evidence is required to finish a phase. It deliberately contains no application source code and does not claim that the planned commands or modules already work.
>
> **Start here if you are a fresher.** Read this document in order. Follow one phase at a time. Do not start with a complicated GNN or dashboard when the evidence pipeline is not working.
>
> **Architecture authority:** [full v4 specification](../architecture/architecture-v4-spec.md), [requirement audit](../architecture/REQUIREMENTS_AUDIT.md), [canonical data dictionary](../data/data-dictionary.md), [join policy](../data/join-policy.md), and [definition of done](definition-of-done.md). If this implementation suggestion conflicts with an approved contract, open an ADR before coding.

## 1. What you are building and what is real today

**Product:** a local, offline-at-inference Bitcoin investigation application. A user imports permitted Bitcoin transaction records, and optionally genuine locally observed Bitcoin P2P relay metadata. CLARION preserves evidence provenance, builds time-aware graphs, detects **candidate** suspicious behavior, prioritizes leads, shows uncertainty, and generates auditable case dossiers. These are investigative leads, not declarations that an address or person committed a crime.

**Present repository reality (October 2026):** the Python packaging/CLI skeleton and some configuration tests exist, while most source paths, frontend screens, data generators, model-training scripts and integration tests are **design placeholders**. A script name in the repository is **not proof that the script works**. No pretrained CLARION model, representative approved SIH dataset, measured benchmark or operational dashboard is included as a verified product.

**Non-negotiable interpretations:**

1. Bitcoin is a UTXO ledger. An input spends a previous `txid:vout`; an address annotation is not a uniquely identified human or wallet owner.
2. A network host observed relaying a TXID is **not** necessarily the creator, payer, controlling wallet or first broadcaster.
3. If genuine network observations or valid TXID joins do not exist, run **CHAIN_ONLY**. If credible labels do not exist, run **UNSUPERVISED_ONLY**. These gates are independent.
4. If the chain/wire dependence test fails, **Δ abstains**. If the controlled economic goal is unknown, the affected **Π components abstain**. Missing is never zero.
5. Pass 1 must freeze local model/motif/eligible-signal risk **before** MLRP. Pass 2 may add propagation **once**, at most 25 of 100 points. Country is contextual and is never assigned risk.
6. Synthetic data is valuable for correctness and integration, but synthetic criminal-looking behavior is **not** evidence of real-world illicit detection.

### The complete route a developer must eventually make work

~~~text
Approved source archives (CSV / JSON / XML / Bitcoin Core)
  -> immutable raw files + SHA-256 + legal/source manifest
  -> strict parsers -> canonical chain + optional wire tables
  -> readiness/coverage/clock/TXID/labels decisions
  -> reproducible as-of typed evidence graph
  -> causal features + optional learned embeddings
  -> MCER uncertain entities + motif witness paths
  -> separate base models -> time-safe OOF stack
  -> eligible Delta + eligible Pi -> pass-1 local score
  -> FREEZE pass-1 seeds -> bounded causal MLRP
  -> pass-2 final ranking + uncertainty + explanations
  -> local API -> offline dashboard -> hash-bound case export
  -> independent tests, ablations, Linux offline release
~~~

A contributor **must** make a small, testable vertical slice work first: import one documented fixture, construct three connected evidence objects, produce a transparent chain-only rule/novelty lead, and show its source records. Everything else grows from that slice.

## 2. Prerequisites, environment and exact learning path

**Intended development platform:** Ubuntu Linux (or a Linux environment on a Windows computer); target runtime is offline Linux. Have Git, Python 3.11 or 3.12, a code editor, enough local disk for imported data, and the `uv` Python package manager. GitHub hosts source and reviews; data/weights remain local or in an approved artifact store.

**Initial setup (these are setup/inspection commands, NOT a complete CLARION pipeline):**

~~~bash
git clone https://github.com/shanmukhdatta/CLARION.git
cd CLARION
python3 --version
uv --version
uv sync --locked
uv run clarion --help
uv run pytest
uv run ruff check .
~~~

If `uv` is not installed, use its official installation instructions at https://docs.astral.sh/uv/ . The repository has `pyproject.toml`, `uv.lock` and a registered `clarion` CLI entry point; at present the CLI exposes help/version, **not** implemented `ingest`, `train`, `score` or `report` operations. Do not report any test as passed unless you actually ran it and captured the result. Installing packages during development requires internet; deployed inference must not.

**A fresher should understand these terms before P1:** a row/schema is an input contract; SHA-256 verifies unchanged bytes; Parquet is a column-oriented file; DuckDB queries local data; a UTXO is a spendable transaction output; TXID identifies a transaction; an outpoint identifies one specific output; as-of time means only observations available by that cutoff; a label is documented ground truth at a specified subject level; an OOF prediction is made for a validation fold by a model that did not train on that fold; calibration asks whether predicted probabilities match frequencies; abstention means insufficient evidence.

**Progression for one developer:** small fixture -> schema tests -> source-to-evidence graph -> fixed rule baseline -> chronological split -> logistic regression/random forest -> GraphSAGE challenger -> stacking -> cross-layer scientific gates -> risk propagation -> UI -> full release. No GPU is required for the first several milestones.

## 3. Proposed technology stack: choose a tool for a job, not for hype

The repo currently pins only a minimal Python runtime (Pydantic and PyYAML) and dev tools. The following are **recommended additions by phase**, not already installed dependencies. When a phase starts, install compatible versions with `uv add` or `uv add --group dev`, update `uv.lock`, record licenses, and test on Linux. Do **not** paste unverified versions into requirements or upgrade everything blindly.

| Layer | Default first choice | Upgrade only when needed | Why / when |
|---|---|---|---|
| Project/runtime | Python 3.11/3.12, uv, Git, pytest, Ruff, mypy | Docker/Podman for reproducible packaging | reproducible installs and checks |
| Schemas/configuration | Pydantic v2, JSON Schema, PyYAML | PyArrow schema contracts | strict, versioned interfaces |
| CSV/JSON/XML import | Python standard library, Pydantic, defusedxml for untrusted XML | PyArrow CSV for large files | secure bounded validation; reject XML DTD/entities |
| Table storage | PyArrow/Parquet + DuckDB | local SQLite for run/case metadata | memory-efficient local, offline analysis |
| Small graph correctness | NetworkX on **small fixtures only** | PyTorch Geometric (PyG) sparse tensors/samplers | test graph semantics before scaling |
| Feature and statistical work | NumPy, pandas, SciPy, scikit-learn | Polars, statsmodels as justified | tabular baseline, splits, dependence and metrics |
| GNN training | PyTorch + PyTorch Geometric GraphSAGE | GAT / heterogeneous or temporal GNN | incremental measured graph contribution |
| Supervised baselines | scikit-learn logistic regression + random forest | LightGBM if reproducibly better | simple interpretable baselines first |
| Unsupervised baselines | scikit-learn Isolation Forest, GMM | One-Class SVM for modest datasets, graph novelty | ranking when labels insufficient |
| Explanations | explicit rule/path provenance and model feature tables | SHAP for supported models | evidence must remain the primary explanation |
| API + UI | FastAPI + Pydantic; React + TypeScript + Vite | Cytoscape.js or Sigma.js for bounded graph views | local, typed, explorable investigator console |
| Report/export | safe CSV/JSON writers + ReportLab or WeasyPrint with **bundled** assets | no cloud PDF service | local hashable/redactable cases |
| CI/security | GitHub Actions, pytest, Ruff, mypy, dependency audit | Playwright for end-to-end UI | reviewable regression gates |

**Compatibility rule:** pick the supported PyTorch CPU/CUDA build first, then the matching PyG wheels from https://pytorch-geometric.readthedocs.io/en/latest/install/installation.html . Confirm GPU support with an actual minimal run; PyG compiled acceleration is optional. Do not require CUDA to use CLARION on a CPU-only Linux workstation.

**Hardware tiers:** CPU (development, chain-only baselines, small fixture graphs), single compatible GPU (GraphSAGE/GAT research, sampled minibatches), larger research machine (only after profiling justifies temporal hetero GNN). Persist windows as Parquet and sample neighborhoods; never assume that a full Bitcoin graph fits into RAM or VRAM. Record rows/second, peak RSS/VRAM, training time and local inference latency.

## 4. Where to get data — and what each dataset genuinely contains

Before downloading anything, record publisher, official link, revision, license/permission, hash, time range, subject/label granularity and missing fields in `data/manifests/`. Source URLs here are acquisition references, **not credentials or automatic imports**. Verify each dataset's latest license and exact columns before use.

| Source / track | Official starting point | Best legitimate use | Important limitation |
|---|---|---|---|
| **A1: Elliptic++** | https://github.com/git-disl/EllipticPlusPlus | labeled Bitcoin transaction/actor graph benchmarking, graph vs tabular models | benchmark graphs/features are not an authenticated P2P IP-to-wallet ownership dataset; verify splits and what graph is released |
| **A2: BitcoinHeist (UCI #526)** | https://archive.ics.uci.edu/dataset/526/bitcoinheistransomwareaddressdataset | address-level ransomware-label / novelty tabular benchmark, chronological feature experiments where eligible | derived address-level features; **not** raw UTXO transactions or verified benign-negative truth; UCI warns some “white” addresses may not be clean |
| **A3: Bitcoin Core** | https://bitcoincore.org/en/doc/ and https://developer.bitcoin.org/reference/rpc/ | raw transaction/outpoint truth and realistic chain-only fixtures, when lawfully available | running/indexing a node costs storage/time; raw chain data has no verified illicit label or original broadcast IP |
| **B: CLARION synthetic** | `src/clarion/synthetic/` and `scripts/data/generate_fixtures.py` (PLANNED) | schema integration, sealed known truth, relay hard negatives, Δ/Π/MLRP correctness and reproducible L0–L3 | cannot establish external real-world performance |
| **C: SIH organizer samples** | organizer-provided permitted files, if received | direct CSV/JSON/XML format acceptance and any **actually present** cross-layer fields | availability, license, TXID semantics, capture quality, label reliability are currently unverified |

**Which to start with?** In P1, first produce 10–50 hand-audited tiny synthetic transactions/observations with known expected outputs; then import a small, legally sourced Bitcoin Core sample for UTXO/parser correctness. In P2/P3, use Elliptic++ for graph classification tasks and BitcoinHeist for an independent *address-level* tabular exercise. Do **not** silently merge these datasets into one “fully labeled Bitcoin + IP” table; they have different coverage, units and labels.

**Bitcoin Core acquisition guidance, no application code:** a permitted already-synced local node or an approved export is preferable to forcing every new contributor to download the whole chain. Identify selected block heights/hashes, extract transactions with inputs, outputs and, where available, previous outpoints; capture node/version/network provenance, handle pruned/missing history, and use explicit blockhash or a txindex where the Core RPC requires one. Never infer mempool first-seen timestamps from block header times. Start from a small sample and document limitations. For SIH files, request a data dictionary explaining CSV list encoding, XML structure, TXID byte order, time units and sensor vantage; when unavailable, make the parser configuration explicit and label assumptions unverified.

### Source selection decision tree

~~~text
Do we have organizer CSV/JSON/XML with a documented schema?
  YES -> audit, hash, validate and import as Track C.
  NO  -> build reproducible Track B fixtures; do not invent official data.
Do we need real on-chain model evaluation?
  YES -> Elliptic++ / BitcoinHeist as separate benchmark tasks;
         use Bitcoin Core exports for actual outpoint reconstruction.
Do we have genuinely decoded, source-tagged observed TXIDs from a permitted sensor?
  YES -> run J1 exact-join and capture-bias checks; cross-layer only if gates pass.
  NO  -> CHAIN_ONLY; no Host-to-wallet ownership inference.
Are verified labels adequate for the chosen subject and time split?
  YES -> eligible supervised experiment, subject to leakage audit.
  NO  -> UNSUPERVISED_ONLY novelty ranking.
~~~

## 5. When data is unavailable: design the synthetic generator before any ML

**Ownership:** `src/clarion/synthetic/{generator,scenarios,ground_truth}.py`, `scripts/data/generate_fixtures.py`, `data/samples/`, `tests/fixtures/`. These paths are current placeholders, not a functioning generator.

**Build the generator in this precise order:**

1. **Seed and scenario manifest.** Decide a reproducible seed, generated date range, size, Bitcoin network marker, scenario tier L0–L3, parameter family, clock precision, and which fields are synthetic. Save a separate manifest for each generated run. Do not use an arbitrary current wall-clock value in expected fixture output.
2. **Ledger objects.** Generate unique Bitcoin-shaped TXIDs, valid distinct `txid:vout` outpoints, transaction inputs and outputs in nonnegative integer satoshis. Make coinbase/funding origins explicit, never let a non-coinbase outpoint be spent twice in a single accepted chain state, and enforce `sum(known inputs) = sum(outputs) + fee`. Preserve script types and null address annotations where needed.
3. **Normal activity first.** Include simple payments, self-consolidation, legitimate merchant payments, change, batching, exchange/custodial aggregates and high-degree services. These must not become automatically suspicious because of degree or frequency.
4. **Candidate behavior patterns.** Add configurable peeling-like chains, fan-out/fan-in, layering/cycles where physically possible, fragmentation and timing changes. The scenario identifier is a **synthetic behavior tag**, not real-world criminal ground truth.
5. **True actor assignments in a sealed file.** Write synthetic controlled-address groups, valid multi-party transactions, objective/payee records (only when deliberately modeled) and truth-level motif annotations to a **private evaluation-only table**. Never include truth IDs, scenario type, “illicit flag”, hidden owner name or generator seed among model features or public graph attributes.
6. **Separate relay observations.** Generate a distinct sensor stream with IDs, sensor vantage, observed TXID (or missing), source/destination host/port, event class, actual observation time and error/clock precision. Model one transaction observed by multiple relay peers. This never establishes that any relay host owns an address.
7. **Capture quality changes.** Deliberately include missing TXID payloads, partial captures, repeated events, clock skew, NAT-like shared egress, VPN/hosting context, several peers in one ASN, duplicate sensors and timestamp format issues.
8. **Truth-vs-evidence separation.** Release safe source fixtures to ingestion and an independently held truth set to the evaluator. Apply immutable hashes to both, keep truth inaccessible to inference, and record what signal is deliberately absent.
9. **Difficulty L0–L3.** L0 simple complete data; L1 realistic variability and mild missingness; L2 heavy degree/service confounds and sensor dropout; L3 distribution shift, ambiguous control, clock errors and complex hard negatives. State exactly which nuisance variables differ.
10. **Serialize all supported formats.** Export equivalent tiny CSV, JSON and XML samples through independent serializers, then parse them back into **identical normalized records**. Keep expected row/graph counts and exact expected outpoint linkage in tests. Store only small synthetic, non-sensitive fixtures in Git.
11. **Freeze challenge sets.** Reserve a different seed and different generator parameter distributions for a never-trained-on future holdout. If an ML model exploits scenario templates rather than behavior, report that failure.

**Recommended generator deliverables (planned names, not pre-existing downloads):** `data/samples/synthetic_v1/sample.csv`, `sample.json`, `sample.xml`; `data/manifests/synthetic_v1.manifest.json`; separate restricted `truth.json`; expected `normalized.parquet`, `graph_nodes.parquet`, `graph_edges.parquet`; and a short `scenario_report.md`. Generated bulk outputs and private truth remain ignored by Git.

**Generator safety checks:** satoshis conserved, deterministic seed output, valid/invalid rows separately identified, known cause of every test expectation, legitimate hard negatives, exact multi-relay TXID case, no leakage field, and no hidden metadata in model features. Do not score a generated “criminal” tag as an actual criminal label in the product.

## 6. Phase 0 — Orient the contributor and freeze the first slice (documentation gate)

**Goal:** understand architecture, record unresolved feasibility questions, avoid training against undefined data.

1. Read root README plus this playbook, `docs/architecture/REQUIREMENTS_AUDIT.md`, `docs/data/data-dictionary.md`, `docs/data/join-policy.md`, `docs/ml/experiment-plan.md`, and `SECURITY.md`.
2. Run the setup inspection commands from §2. Write down OS, Python, uv version, git commit and each actual command result.
3. Choose the **first subject**: transaction-level chain-only candidate risk on a small fixture. Document any extra address/entity tasks separately, because their labels are different.
4. Write a data availability table: SIH file? confirmed schema? genuine network TXID? independently trustworthy labels? available_at? enough transactions? Core UTXO completeness?
5. Record unresolved design decisions D01–D12 in [requirements audit](../architecture/REQUIREMENTS_AUDIT.md) or a decision log. An unknown is a blocking gate for the dependent feature, not a reason to invent a default.
6. Assign small PRs; define a one-page vertical-slice acceptance scenario with its exact expected graph and evidence links.

**Exit:** reviewed scope, one named fixture, documented source/units, explicit CHAIN_ONLY + UNSUPERVISED_ONLY fallbacks, and an owner for P1 tasks. **No model is trained in P0.**

## 7. Phase 1 — Safe ingestion, Bitcoin fidelity, typed graph and simple chain-only lead

**Relevant v4 blocks:** 0, 1A, 1B, 2. **Rule:** finish this phase before graph neural networks.

| Step (build in order) | Work and recommended library | Repository target | Observable proof |
|---|---|---|---|
| P1.1 contracts | Define versioned fields, primary keys, units, null vs unknown vs abstain, UTC/time precision, schema migrations (Pydantic/JSON Schema) | `schemas/raw/`, `schemas/normalized/`, `src/clarion/domain/` | good and bad rows pass/fail documented validation |
| P1.2 evidence ledger | SHA-256 original bytes; source/permissions/license; idempotent imports, quarantines and append-only run manifest | `src/clarion/storage/`, `core/provenance.py` | source bytes never rewritten; repeated import reproducible |
| P1.3 data adapters | secure CSV/JSON/XML (defusedxml for XML), explicit array parsing, safe size/depth ceilings; separate Elliptic++, BitcoinHeist and Core adapters | `src/clarion/ingestion/` and `adapters/` | equivalent three-format fixtures produce identical canonical results |
| P1.4 chain semantics | resolve `txid:vout`; amounts in **integer sats**; fee only when full inputs known; change candidate only as hypothesis; coinbase/script/reorg cases | `src/clarion/chain/` | conservation/outpoint tests and unresolved-previous-output flags |
| P1.5 wire observations | treat each actual observation as a sensor fact; retain endpoint direction, host/port, duplicates, precision; local ASN/GeoIP optional | `src/clarion/wire/` | repeated relay and missing TXID remain correctly uncertain |
| P1.6 join/readiness | enforce J0 exact value-flow, J1 exact decoded-TXID relay, J2 context; report overlap, independence and label availability; choose modes | `src/clarion/readiness/` | no fake Host→wallet edge, CHAIN_ONLY on missing wire |
| P1.7 storage | Parquet tables + DuckDB catalog, versioned manifests and time-window indexing | `src/clarion/storage/` | audited counts and reproducible queries |
| P1.8 graph | construct exactly six types: Transaction, Address, Entity candidate, Host, ASN, Country; typed evidence-backed edges and as-of snapshots | `src/clarion/graph/` | tiny graph expected nodes/edges/time/source IDs match |
| P1.9 first baseline | compute deterministic chain features/rules: inputs/outputs, fee availability, degree, burst, peel candidate; show **candidate/novelty rank**, not crime probability | `src/clarion/features/`, `src/clarion/detection/` | score traced back to source TXIDs and false-positive cautions |
| P1.10 orchestration | an actual local CLI command for import → readiness → graph → chain-only ranked file; idempotent run IDs and failure reports | `src/clarion/application/`, `src/clarion/cli/` | one end-to-end Linux run on small fixture and intentional bad input |

**P1 explicit output:** imported dataset manifest, canonical tables, `ReadinessDecision`, immutable evidence graph snapshot, baseline leads + evidence IDs, test logs and failures list. **Not yet:** trained multi-model stack, calibration, Δ/Π or dashboard.

**Required P1 negative cases:** coinbase; an unknown prevout; sub-satoshi rounding attempts; duplicate/invalid TXID; multiple sensors observing same TXID; VPN/ASN coincidence; unsafe XML DTD/entities; malformed JSON array; ambiguous addresses; graph cutoff earlier than an event; absent/invalid label. Every incorrect inference must fail closed or carry an uncertainty marker.

**Gate to P2:** P1 input-to-output works without internet on an approved fixture; tests actually pass; exact J0/J1 separation is demonstrated; raw artifacts have source hashes; no raw private IP dataset is accidentally committed.

## 8. Phase 2 — Causal graph features, embeddings, MCER and motif evidence

**Blocks:** 3, 4 and 5. **Prerequisite:** stable P1 schemas, snapshots and time boundaries.

1. **Feature registry.** Each feature records unit, subject (transaction/address/entity), derivation, required sources, missingness and `available_at`. Implement chain degree, in/out value, burst windows, fee/vsize where actually known, temporal recurrence and optional wire-session features, all using events at/before cutoff. Fit normalization on train only.
2. **Graph baselines before neural models.** Measure degree/centrality, simple random-walk embeddings or Node2Vec on an eligible small snapshot. Use NetworkX only for small correctness fixtures; use sparse storage for scale. Persist node ordering and snapshot hash so predictions map to the correct subjects.
3. **First learned graph model: GraphSAGE (PyTorch + PyG).** Define subject/labels and allowed edges; construct time-bounded neighborhood sampling, fixed features/masks, a small 2-layer baseline, reproducible seeds and separate chronological train/valid/test. Compare to the exact same subject-level logistic-regression/random-forest baseline.
4. **Optional challenger:** add type-aware hetero GraphSAGE/GAT, then temporal GNN **only** if a measured future holdout gain justifies compute and added complexity. Shared embeddings can help several tasks but never prove real identity. Report model size, neighborhood fanout, leakage checks and memory use.
5. **MCER H1–H5.** Propose pairs via common-input H1, change H2 and embedding similarity H3; inspect uncertain wire conflicts H4 and fingerprint continuity H5. Maintain signed independent evidence, service/CoinJoin must-not-auto-merge constraints, abstained ambiguous pairs, temporal versioned cluster lineage. Do **not** equate entity clusters with people.
6. **MCER optimization:** start with deterministic constrained pair proposals and auditable clustering. Introduce an iterative correlation-clustering-like optimizer if a stable, reproducible objective and stopping criterion are established. No uncontrolled transitive merges from one weak IP/ASN clue.
7. **Motif engine:** enumerate candidate peel, fragmentation/fan-out, mixing-like and layering/cycle motifs as **timestamped witness edge paths**. Score clear feature evidence; attach alternative innocent interpretations (batched exchange, CoinJoin, processor/custodian). Do not label motives from graph shape alone.
8. **Test graph edits and cutoffs.** Remove any future edge and confirm earlier output is unchanged. Verify entity false-merge rate on sealed truth and known hard negatives; validate motif precision/recall only against legitimate task labels and witness truth.

**Module ownership:** `src/clarion/features/`, `representation/`, `entity_resolution/`, `patterns/`; training helpers in `src/clarion/training/`; tests in `tests/leakage/`, `tests/property/` and `tests/integration/`. Consult [MCER design](../ml/mcer-plan.md) and [model selection](../ml/model-selection.md).

**P2 artifacts:** `feature_registry`, chronological snapshot manifests, pretrained candidate encoder artifact(s) with hashes, versioned MCER memberships/conflicts/lineage, auditable motif witness instances, resource-profile table, time-leakage audit.

**Gate to P3:** GraphSAGE is compared against simpler baselines on the same split (improvement is **not** assumed); time-causal embedding generation works; MCER hard negatives do not silently false-merge; every motif has concrete source links and benign controls.

## 9. Phase 3 — Train real baselines, time-safe stacking, Δ/Π gates and pass-1 fusion

**Blocks:** 6, 7, 8 and first pass of 9. This is a **training and scientific validation phase** separate from offline production inference.

### 9.1 The model choices and their actual jobs

| Family | Train when | Recommended first model/library | Input | Output and interpretation |
|---|---|---|---|---|
| Non-ML rules | immediately after P1 | deterministic feature/motif rules | verified chain facts | reviewable flags/score ingredients |
| Supervised tabular | only with adequate eligible subject labels | logistic regression, random forest; optional LightGBM | time-causal tabular features | subject label predictions; probabilities only if validated/calibrated |
| Unsupervised novelty | labels missing/too weak | Isolation Forest; compare GMM, One-Class SVM for tractable scale | train-window non-label features | relative novelty score/rank, **not probability of crime** |
| Graph learned | graph task and cutoff are valid | GraphSAGE classifier + embedding head; optional GAT | sampled graph and features as of T | embeddings and held-out task predictions |
| Meta-learner | enough diverse **out-of-fold** base predictions and valid labels | regularized logistic regression; optional LightGBM | base scores, motif evidence, eligible Δ/Π, missingness masks | stacked score; separately calibrated if feasible |

**Single place for training:** `src/clarion/training/{splits,trainer,registry,drift}.py`; model families in `src/clarion/detection/` and `representation/`; experiment entrypoints `scripts/train/` (currently placeholders). Do not train models independently in disconnected notebooks and paste their numbers into one final score.

### 9.2 Ordered training recipe — do not skip a step

1. **Freeze the task.** Choose *transaction* or *address* label, permitted dataset, class definition, label source/version, what “unknown” means and time cutoff. Track Elliptic++ and BitcoinHeist separately. Never treat unverified unknowns as trusted negatives.
2. **Audit eligibility.** Count positive/negative/unknown per chronological interval and subject; check label `available_at` and any dataset-specific time grouping. If unusable, switch to unsupervised track, not fake supervised labels.
3. **Lock split protocol first.** Example design: older events for fitting, later separate calibration/validation, newest untouched test; expanding-window folds within the training period. Exact boundaries depend on the dataset. Purge repeated entities/transactions and overlapping labels where required.
4. **Per-fold replay.** Build **fold-local** raw-to-feature transforms, imputer/scaler, graph snapshots, embeddings, MCER versions, motif-derived features and training-only parameter fits. No feature can see edges or feedback from the future prediction cutoff.
5. **Train easy baselines.** Rule baseline → LR → RF → IF; log seeds/hyperparameters, features, subject counts, fit time, score scale, imbalance handling and why any labels were dropped. For supervised labels, compute PR-AUC, precision@K and appropriate confusion/error measures; for novelty, use honest ranking evaluation only where reviewed truth exists.
6. **Train GNN challenger.** Start with GraphSAGE with type-appropriate mask/time-limited neighbors; add GAT only after comparing on the *same* held-out task. Save embeddings and logits with correct node IDs/cutoff.
7. **Create time-respecting OOF base-score table.** For each forward fold, train models only on earlier periods and predict the next one. Put all base predictions on the same key `dataset_id, subject_id, cutoff, fold_id`; include eligibility/missingness masks and provenance. If a family cannot produce a valid score for a row, mark **unavailable**, do not backfill from the future.
8. **Train meta-model on OOF only.** A simple regularized LR is the first choice. Meta-features may include eligible motif, Δ and Π output **only if recomputed without leakage in the fold**. If insufficient independent OOF data, report a non-trained ensemble/rule combination or best single baseline instead of pretending stacking exists.
9. **Calibrate separately when justified.** Use later independent calibration data after meta-model selection, then evaluate **once** on untouched future holdout. Record reliability diagram, Brier score, calibration error and uncertainties when appropriate. An IF score or unvalidated stack is never converted to “87% chance of fraud.”
10. **Δ chain–wire residual:** only for validated J1 paired observations with genuine TXIDs, time/source quality and held-out dependence better than sensor-preserving shuffled nulls. Start with train-only CCA/linear residual mapping; components Δ1–Δ5 are hypotheses with supporting evidence, not guilt. If gate fails, return ABSTAIN with reason, not a fabricated zero.
11. **Π economic cost:** only if controlled-address set, actual goal/payees and feasible fee/latency assumptions are known. Derive a clearly itemized candidate cost premium against a documented minimum-cost alternative: fee (sats), hop count, delay, fragmentation and eligible infrastructure context. Invalid baseline/unknown payee → per-component or total ABSTAIN. Π measures extra cost/complexity, not criminal intent.
12. **Pass-1 fusion only.** Combine available model/rule/motif outputs with eligible Δ/Π in a documented, train-only calibrated mapping when possible. Keep Δ and Π on separate interpretive axes; never naïvely add correlated p-values. Store the exact local score type, uncertainty, contributing facts, model version and immutable **frozen seed**. **No current-run propagation enters the meta-model.**
13. **Final training release decision.** Promote an artifact only when it improves valid holdout utility without unacceptable legitimate-service false positives, excessive inference cost or missing security/license provenance. Otherwise keep prior baseline or unsupervised route.
14. **Model registry:** persist model ID and approved safe serialization format, library versions, training and evaluation source hashes, split boundaries, feature schema, calibration status, subject level, threshold policy, seed, time and licence. Never load untrusted pickle models from users.

**Training outputs:** fold manifests, per-fold feature/graph/MCER hashes, OOF table, base-model cards, meta-model card, independent calibration report (if eligible), future-holdout report, per-cohort hard-negative errors, and frozen pass-1 seed table. See [stacking](../architecture/stacking-architecture.md) and [experiment plan](../ml/experiment-plan.md).

**Gate to P4:** one complete **honest** training track works with temporal leakage tests, end-to-end score provenance and a known fallback when supervision/Δ/Π are unidentifiable. A low or disappointing benchmark score is not grounds to fabricate labels.

## 10. Phase 4 — Causal propagation, offline product, dashboard and dossier

**Blocks:** second pass of 9, 10 and 11.

1. **MLRP input snapshot.** Load immutable pass-1 local risk seeds, as-of typed graph, edge evidence, supported input/output amounts, candidate entity version and service boundary registry. Assert seeds cannot be silently recomputed during propagation.
2. **Separate channels.** Financial flow travels only through evidence-backed value-flow paths with directed outpoint lineage. Network/host/ASN edges provide **observation context**, not a mechanism to spread accusation to other wallet holders. Never create an inferred Host→Address ownership edge. Country is context only.
3. **Propagation algorithm.** Implement the architecture's bounded, causal value-share × time-decay × edge-conductance scheme with at most **six hops**. Normalize outgoing value shares so a 1→200 fan-out does not multiply risk. Distinguish forward exposure from backward provenance; use verified timestamp ordering.
4. **Boundaries and caps.** Exchanges/custodians/coinjoin-like high-degree services and uncertain financial flows require source-backed attenuation/absorption or abstention. Do not allow host/ASN customer-to-customer spillover. The additive **pass-2 propagation contribution is capped at 25/100 and applied once**. Keep provisional/local risk distinct from propagated exposure.
5. **Explain each propagated contribution.** A reproducible ordered evidence path shows seed, edges, timestamps, amounts/fractions, decay, uncertainty and barrier handling. An optional learned GAT edge-weight comparison cannot replace deterministic evidence justification.
6. **Local API.** Implement FastAPI read/query endpoints in `src/clarion/api/routers/` for readiness, runs, ranked leads, evidence graph, entity hypotheses, motifs, signal abstentions, propagation paths, models, audit and cases. Bind localhost by default; pagination, time bounds, role-based access and safe exports are compulsory.
7. **Dashboard.** React + TypeScript + Vite, locally bundled assets, typed API DTOs, graph component with bounded node/edge count. Implement screens in `frontend/src/features/` in this order: readiness → leads → evidence graph/timeline → entity and motifs → stack/Δ/Π → propagation → cases/report → models/audit.
8. **Case report.** Export source-linked explanation, source/model/run hashes, typed confidence, benign alternatives, case-review status, uncertainty/ABSTAIN and only authorized/sanitized data. CSV export must prevent spreadsheet-formula injection; PDF output must use local assets and preserve evidence integrity.
9. **Full local demonstration.** From a source fixture: import → readiness → chain-only score → frozen-seed bounded propagation → browser lead → click evidence chain → generate a locally stored dossier. Run one cross-layer synthetic demo separately and label it synthetic.
10. **Security and offline tests.** Simulate no network egress, malformed uploads, impossible time order, role-denied dossier export, relay-to-owner misattribution, very high graph degree and missing models. Reject unsafe model artifacts and invalid schema versions.

**P4 outputs:** versioned MLRP paths and final leads, working local API/UI, redacted report files with hashes, screenshots **plus** actual E2E test logs, no-egress logs, and evaluated CPU/RAM limits. Read [MLRP architecture](../architecture/risk-propagation-architecture.md) and [dashboard design](../architecture/investigator-dashboard-architecture.md).

**Gate to P5:** a new contributor can run the entire local import-to-dossier slice on Linux, reproduce every displayed assertion from source evidence, and prove the 25-point cap, service barriers and no-wallet/IP-ownership rule.

## 11. Phase 5 — Research-grade evaluation and offline distribution

**Block:** 12 plus all crosscutting security and release acceptance.

1. Run three **separate** evaluation tracks: real benchmark graph/address prediction; real Core UTXO correctness; and synthetic L0–L3 end-to-end functional truth. Track C SIH only when officially available. Do not pool “accuracy” across these distinct problems.
2. Measure supervised PR-AUC, ROC-AUC when meaningful, precision@K, false positive rates and calibration by **subject level, time window and label provenance**. For unsupervised rankers report rank-based outcomes only with audited labels. Publish uncertainty and support counts.
3. For MCER, evaluate pairwise false merges, precision/recall and ARI/NMI where controlled truth exists. Include services, CoinJoin-like hard negatives, shared hosts, capture bias and source loss.
4. For motifs/Δ/Π, report actual witness correctness, dependence-null/coverage results, itemized cost identifiability and **abstention rates**; do not score missing components as successful zeros.
5. For MLRP, enforce mass/value conservation, six-hop limit, 25-point limit, no future backwards propagation and benign neighbor contamination controls. Inspect one-hop innocents and high fan-out.
6. Run fixed-split ablations: chain rules only; tabular only; +GNN; +MCER/motifs; +stack; chain-only vs genuinely paired wire; Δ/Π off/on only when eligible; propagation off/on. Include generator-shift tests and negative controls.
7. Perform reproducibility and threat checks: file/schema fuzzing, test seed determinism, corrupted/truncated inputs, model compatibility mismatch, hash verification, CSV formula injection, role policies, offline/no-egress and resource limits.
8. Package a Linux offline build with pinned local wheelhouse, compatible CPU model(s), optional GPU packages, bundled JS/CSS/font assets and GeoIP only if licensed. Document first-time setup vs later completely offline run; verify on a disconnected clean target.
9. Write a plain-language limitations report. Distinguish designed, implemented, verified and unverified experiments. Reproduce at least one complete case from source file hashes to displayed dossier on a second clean installation.
10. Preserve benchmark script/config/model version, environmental fingerprint, dataset rights, artifacts and logs; get review signoff. Only now consider calling an actual build a release.

**Release files:** `experiments/benchmarks/`, `experiments/ablations/`, `docs/operations/`, `deploy/linux/`, `artifacts/models/` manifests, `docs/progress/phase-05-release.md`, and integrity hashes of the distributable. Never commit confidential source captures or large weights to Git.

## 12. Planned contributor-facing commands and artifact contract (not implemented!)

The **command names below describe the CLI that contributors should implement**; **do not copy/paste expecting current `clarion` to support them**. Exact flags are to be specified, tested and documented by each owning phase.

| Planned CLI action | Phase that must implement it | Meaning and durable output |
|---|---|---|
| `clarion doctor` | P1 | verify environment, schemas, local asset readiness, no-egress configuration |
| `clarion fixtures generate` | P1 | seeded safe synthetic CSV/JSON/XML plus truth held outside inference |
| `clarion data register / ingest` | P1 | license/source manifest, SHA-256, canonical Parquet, quarantine log |
| `clarion readiness audit` | P1 | J0/J1 join stats, data/label mode and Δ/Π eligibility report |
| `clarion graph build` | P1 | time-bounded six-type graph and evidence index |
| `clarion features build` | P2 | train-safe features, registry, as-of manifest |
| `clarion train baseline / graph / stack` | P2–P3 | training jobs with chronological split cards and artifacts |
| `clarion entities resolve / patterns find` | P2 | versioned MCER and witness motifs |
| `clarion signals delta / pi` | P3 | gated residuals / bill or explicit ABSTAIN |
| `clarion score local` | P3 | immutable pass-1 seed manifest |
| `clarion score propagate / finalize` | P4 | six-hop bounded paths and capped pass-2 lead ranking |
| `clarion serve / report export` | P4 | local API/UI and redacted evidence dossier |
| `clarion evaluate / package` | P5 | split/audit reports and verified offline Linux bundle |

**Proposed reproducible run folder (an implementation contract, not a directory that currently contains output):**

~~~text
artifacts/runs/<run-id>/
  manifest.json                 # code/config/input/model hashes, schema, cutoff
  raw_sources.json              # references only; never duplicate raw private logs
  readiness.json                # route + counts + ABSTAIN reasons
  normalized/                   # derived Parquet cache, never original evidence
  graph/                        # node/edge snapshots, cutoff, evidence references
  features/                     # feature schema, availability masks
  entities/ motifs/             # candidate evidence and versioned hypotheses
  oof/ models/                  # TRAINING runs only: fold metadata, model cards
  signals/                     # Delta / Pi and eligibility
  scores/pass1.json             # frozen local scores / seed SHA-256
  scores/propagation.json       # paths and independent exposure channels
  scores/pass2.json             # single capped final fusion
  cases/                        # controlled exports, redaction and hashes
  audit/                        # actual run/status/error reports
~~~

All relative paths are examples to be formalized before implementation. Stages must be restartable by checking source/config/schema hashes and must refuse incompatible artifacts rather than silently mixing runs.

## 13. Phase order and handoffs in one view

| Phase | Primary work | What the next phase receives | Do not claim complete until |
|---|---|---|---|
| **P0 preflight** | rights, schema, feasibility, setup, decisions | documented fixture and architecture gate | source/clock/label unknowns explicitly listed |
| **P1 foundation** | import, canonical UTXO + wire, readiness, graph, simple rule lead | hash-bound chain-only graph + features | offline real/synthetic parser correctness, negative tests |
| **P2 graph/entities** | time-safe features, GraphSAGE baseline, MCER, motifs | versioned embeddings, entity proposals, witness paths | hard-negative false merges and future-edge leakage tested |
| **P3 model evidence** | base models, OOF stack, Δ/Π when valid, pass-1 | registered models + frozen local seed table | temporal holdout and abstention/calibration honesty |
| **P4 investigator product** | bounded MLRP, pass-2, local API, UI, dossier | entire runnable investigation workflow | e2e, access, service barriers, offline checks |
| **P5 science/release** | reproducibility, ablation, hard negatives, package | independently reviewed deployable release | repeatable measured results + clean Linux air-gap demo |

**Suggested PR slicing:** one feature boundary at a time (contract+fixture, then parser+tests, then ledger+UTXO tests, etc.). Never put all of P1–P5 into one unreviewable PR. For every PR state data source and subject level, changed contracts, new dependency/licenses, negative cases, actual tests/run logs, artifact hashes, and rollback plan. A reviewer should be able to run the tiny fixture and understand *why* every output is correct without reading the entire codebase.

**Phase ledger:** update the matching file in [docs/progress/](../progress/README.md) with status `NOT STARTED / IN PROGRESS / IMPLEMENTED / VERIFIED / BLOCKED`, owner, source commit, test command, log link, input and output hashes and unresolved issue. Design documents alone can never change a phase to VERIFIED.

## 14. First-week assignments for a junior contributor (no GNN training yet)

| Day / milestone | What to deliver | What reviewer checks |
|---|---|---|
| 1 — repo and concepts | environment check, terms, one handwritten UTXO example, data rights/source inventory | correct `txid:vout`, sats and time semantics |
| 2 — tiny scenarios | deterministic 10–50 transaction truth plan with hard benign cases | no double spend or leaked labels |
| 3 — canonical schema | raw CSV/JSON/XML field mapping and validation/negative fixtures | same canonical output, invalid rows fail clearly |
| 4 — chain/wire distinction | table mapping J0 vs J1 vs J2, many hosts relaying one TXID | absolutely no host-to-wallet control inference |
| 5 — graph and cutoff | expected six-type node/edge snapshot and one source-linked rule lead | timestamps and evidence IDs reproducible |
| 6–7 — integration handoff | short actual test log, errors and PR with reviewer checklist | P1 working slice or clear BLOCKED status |

This is an **illustrative learning sequence**, not a completion promise or implementation evidence. If a task requires unfamiliar Bitcoin details, review Core protocol/RPC documentation and raise the specific unresolved assumption before writing the parser.

## 15. Common beginner mistakes and the required correction

| Mistake | Correct approach |
|---|---|
| “Dataset downloaded, so full CLARION can train” | audit subjects, fields, labels, clock meaning and missing wire first |
| “BitcoinHeist has transactions/IPs” | it is an address-level derived-feature task; keep raw flow and P2P separate |
| “Every unknown or unlabeled address is legal” | treat unknown as unknown; use eligible independently justified labels only |
| “A relaying IP is the payer” | it is only an observed relay under one sensor's viewpoint |
| “One high cosine similarity means same person” | bounded uncertain entity hypothesis, conflicts and false-merge tests |
| “A graph shape proves laundering” | support a lead with witness paths and legitimate alternatives |
| “Train/test randomly; then use the final graph for features” | split time first, rebuild fold-local causal graph and preprocessing |
| “Isolation Forest gives 97% fraud probability” | unsupervised anomaly ranking is not a calibrated probability |
| “If Δ or Π is missing, put 0” | return ABSTAIN and hide unsupported score channels |
| “Propagation before stack, then feed it back” | pass-1 stack -> freeze -> pass-2 propagation once, capped |
| “Country has a risk score” | Country is geographic context only |
| “Tests folder exists so functionality is implemented” | inspect real executable tests and record actual pass/fail results |
| “It works online so it works in air-gapped Linux” | build complete local assets/wheels and test without network |
| “Synthetic high accuracy proves real detection” | evaluate synthetic mechanics and real benchmark tasks separately |

## 16. Final quality checklist for every phase

- [ ] Source, legal basis, clock, units, keys, schemas and hashes are recorded.
- [ ] Valid/invalid/missing/unknown cases have explicit output behavior.
- [ ] No future event, label, entity cluster or embedding leaks into earlier predictions.
- [ ] J0 Bitcoin flow, J1 observed relay and J2 context are not confused with ownership.
- [ ] Baselines are compared before complex models; subject level and dataset track are explicit.
- [ ] Supervised probabilities have appropriate labels/calibration; novelty remains a rank.
- [ ] Δ and Π eligibility and individual ABSTAIN reasons are visible.
- [ ] Propagation uses frozen seeds, no cross-customer host spillover, six-hop bound, and ≤25-point single application.
- [ ] Source evidence and benign explanations appear in API, graph and reports.
- [ ] On an actual Linux/offline run, tests and outputs are captured rather than assumed.
- [ ] Dependencies and dataset licenses permit planned training/distribution.
- [ ] `docs/progress/`, README references, interface documentation and ADRs are updated by the owning PR.

**Useful next references:** [Data acquisition](../data/dataset-acquisition.md) · [Join audit](../data/join-policy.md) · [MCER](../ml/mcer-plan.md) · [Stacking](../architecture/stacking-architecture.md) · [MLRP](../architecture/risk-propagation-architecture.md) · [Dashboard](../architecture/investigator-dashboard-architecture.md) · [Developer flow](developer-guide.md) · [Definition of done](definition-of-done.md).

**Bottom line:** follow the gates in order, build the smallest verifiable chain-only investigation first, and allow every unsupported ambitious signal to abstain. This preserves the full CLARION v4 research direction without fabricating data, identity or performance.
