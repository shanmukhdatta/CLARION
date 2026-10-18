# CLARION v4
> **CLARION — Offline, Explainable Bitcoin Transaction and Network-Traffic Intelligence.** An evidence-first investigator platform for SIH26146; uses graph ML and classical learning to prioritize reviewable leads **without claiming that a relay IP owns a wallet**.

**Project:** Smart India Hackathon 2026 · SIH26146 · NTRO · Blockchain & Cybersecurity  
**Target:** Linux, fully offline at inference time · **Repository status: architecture and documentation scaffold ONLY**  
**Current stage:** Architecture gap audit and cross-component contract review. **No executable application, trained model, security test or completed benchmark is represented as working. Critical dataset and calibration decisions remain open.**

### Start implementing CLARION — follow this first

**[Beginner-friendly phase-by-phase implementation playbook](docs/development/implementation-playbook.md)** — the practical starting point for a new contributor. It explains the recommended **technology stack and libraries**, where to obtain **real Bitcoin datasets**, how to **generate synthetic CSV/JSON/XML when official data is missing**, how to structure and train baseline/GNN/stacked models without data leakage, what each existing repository module should implement, what deliverables to produce, and the **P0–P5 acceptance gates**. It also lists planned CLI interfaces clearly marked **not yet implemented**.

**Read order:** [Implementation playbook](docs/development/implementation-playbook.md) → [data acquisition](docs/data/dataset-acquisition.md) → [canonical data dictionary](docs/data/data-dictionary.md) → [development workflow](docs/development/developer-guide.md) → your assigned module README. **Do not begin by training a model or implementing the dashboard before the P1 data/readiness/chain-only slice is verified.**

---

## 1. Product vision

CLARION ingests authorized local Bitcoin chain and P2P observations (CSV, JSON and XML), validates evidence, reconstructs temporal value flow, learns graph and tabular behavior, proposes explainable entity clusters, detects pattern candidates, scores discrepancies, and produces ranked investigator leads with verifiable context. The SIH task calls for a **working offline AI/ML prototype**, not only rules or a diagram; implementation follows the phase roadmap after review.

**What investigators should eventually receive:** risk-band-filtered leads; time-bounded interactive graph; candidate entity membership and uncertainty; peel/mixing/layering paths; separately itemized **Δ** divergence and **Π** cost; forward/backward bounded exposure paths; exportable case dossier; clear explanation and source trail.

## 2. Evidence, ethics and product boundaries

- A peer observing or relaying a TXID **does not** prove ownership, origination, identity or guilt.
- Heuristic entity clusters are hypotheses. CoinJoin and multi-party spending invalidate careless common-input linking.
- Exchanges, custodians, processors, VPNs and privacy users require explicit false-positive controls.
- Unknown timestamps, outpoints, network observations, trusted labels and economic objectives trigger **abstention** or chain-only/unsupervised fallback, not invented data.
- Calibrated suspiciousness probabilities require valid labeled independent holdouts; novelty scores are reported as **novelty**.
- No Internet API, telemetry, CDN or live explorer can be required in deployed Linux inference.
- Do not upload confidential captures, real IP data or externally licensed datasets to Git.

## 3. Complete investigator workflow

~~~mermaid
flowchart TD
  A["Locally supplied chain/wire CSV JSON XML"] --> B["0. Validate schema, units, source/time + go/no-go"]
  B --> C["1A. Bitcoin UTXO and value-flow layer"]
  B --> D["1B. Source-tagged P2P observation layer"]
  C --> E["2. Temporal six-type heterogeneous evidence graph"]
  D --> E
  E --> F["3. Chain/wire features + shared graph encoder"]
  F --> G["4. Temporal MCER clustering"]
  G --> E
  F --> H["5. Transaction motifs"]
  F --> I["6. Leakage-safe anomaly stack"]
  F --> J["7. Cross-layer divergence Δ"]
  F --> K["8. Obfuscation expenditure Π"]
  H --> L["9. Calibrated local first-pass fusion"]
  I --> L
  J --> L
  K --> L
  L --> M["Freeze seed risk"]
  M --> N["10. Bounded causal MLRP"]
  N --> O["9. Capped final fusion"]
  L --> O
  O --> P["11. Offline dashboard + evidence dossiers"]
  P --> Q["12. Synthetic/temporal validation + ablations"]
~~~

**Gates:** missing observed TXID or weak dependence → chain-only; unusable incident labels → unsupervised ranking; unknown economic objective → Π abstains; no reliable paired chain/wire views → Δ abstains.

## 4. High-level engineering architecture

~~~mermaid
flowchart LR
  subgraph Ingest["Data and evidence plane"]
    RAW["Immutable raw + hashes"] --> PARSE["Source adapters"]
    PARSE --> DUCK["Parquet + DuckDB"]
    PARSE --> GATE["Quality and label gates"]
  end
  subgraph Intelligence["Analytics and ML plane"]
    GATE --> GRAPH["Temporal typed graph"]
    GRAPH --> FEAT["Causal features + learned embeddings"]
    FEAT --> MCER["MCER"]
    FEAT --> PAT["Motifs"]
    FEAT --> MODEL["Base learners + OOF meta"]
    FEAT --> DELTA["Δ engine"]
    FEAT --> PI["Π engine"]
    MODEL --> FUS["Frozen seeds / fusion"]
    PAT --> FUS
    DELTA --> FUS
    PI --> FUS
    FUS --> PROP["MLRP"]
  end
  subgraph Serving["Local investigation plane"]
    PROP --> API["FastAPI"]
    API --> WEB["Bundled React dashboard"]
    API --> CASE["Case export + audit"]
  end
~~~

For the complete research design and numbered block contracts, see [Architecture specification](docs/architecture/architecture-v4-spec.md). Each implemented module must preserve the specified evidence semantics.

## 5. Recommended technology stack

| Area | Preferred stack / rationale |
|---|---|
| Backend | Python 3.11/3.12 · typed schemas (Pydantic) · FastAPI |
| Parsing and batch analytics | strict CSV/JSON/XML · PyArrow/Parquet · DuckDB |
| Bitcoin chain | locally imported Bitcoin Core RPC/export data; precise UTXO outpoints |
| Wire observations | source-tagged TXID relays, offline local sessionization, optional GeoLite2 ASN/country |
| Graph | canonical typed Parquet nodes/edges; NetworkX for small fixtures; PyTorch Geometric for learning |
| Graph/ML | PyTorch · PyG GraphSAGE/GAT; scikit-learn · optional LightGBM |
| Model registry | local signed/hashed manifests; immutable train/validation cutoffs |
| API | FastAPI + versioned contracts; loopback-only initially |
| Web | React · TypeScript · Cytoscape.js · bundled local static assets |
| Reproducibility | pytest · Ruff · mypy · Linux offline wheel/model bundle |
| Case export | locally generated PDF/CSV/JSON with evidence hashes |

All technology choices are **planned**, pending compatibility, license, security and benchmark review.

## 6. Dataset and feature strategy

**Track A — real graph benchmarks:** Elliptic++ for transaction/address graph research; BitcoinHeist for additional address-level behavior; local Bitcoin Core block/UTXO samples for authentic value-flow and scripts. None supplies trustworthy historic originating relay IP for each Bitcoin wallet.

**Track B — controlled synthetic scenarios:** deterministic SIH-format chain/wire records, separate ground-truth ledger, 0–3 operational-complexity tiers and benign exchanges/custodians/CoinJoin/hosted relays.

**Track C — actual SIH input:** import organizer-provided files after auditing field semantics, source coverage and labels. No authentic cross-layer benchmark is claimed before such data is audited.

**Canonical tables:** evidence_sources, blocks, transactions, inputs, outputs, network_observations, sessions, ip_enrichment, graph_nodes, graph_edges, entity_hypotheses, motif_instances, labels, economic_objectives, scores_and_leads, case_audit. Internal amounts are integer satoshis. Time types/precision remain distinct. Full schema planning: [Schemas](schemas/README.md) and [Data dictionary](docs/data/README.md).

## 7. Blockchain and wire correlation

**Chain:** exact prevout/outpoint links, address spends/funds, input-output amount/fee balance, script/weight, temporal snapshots. **Wire:** capture sensor, source/destination host and port, observed TXID, first-seen time accuracy, session/ASN/GeoIP data.

**Join tiers:** J0 exact on-chain outpoint flow; J1 observed TXID relay; J2 context co-session/ASN/behavior; J3 hypothetical embedding links (not owner evidence). Only J1 directly associates a host observation with a transaction; none directly establishes an owning entity.

## 8. Graph representation and entity inference

Six node types: **Transaction · Address · Entity · Host · ASN · Country**. Edges must carry source evidence, confidence, direction and time. Graph learning progresses from hand-built features and random walks to GraphSAGE/GAT and tested heterogeneous temporal encoding.

**MCER H1–H5:** co-spend proposals, change candidates, learned behavioral similarity, uncertain wire conflicts, stable-fingerprint re-link hypotheses → signed constraints → conservative iterative partition → time-versioned clusters with lineage, confidence and abstentions.

## 9. Bitcoin pattern intelligence

Track peel-chain candidate, mixing-like fan-in/out, CoinJoin-like structure, circular paths, rapid multi-hop layering, changing output fragmentation, bursts, fee/weight anomalies and interactions with locally documented service categories. Require supporting subgraphs **and legitimate alternative interpretations**; nothing is proof of laundering.

## 10. Stacked anomaly detector, meta-model and lifecycle (§6)

**What enters the stack:** as-of chain features, eligible wire features, temporal graph embeddings, MCER candidate context, §5 motif scores, valid Δ components, valid Π bills and source-coverage masks. **What exits:** named base-model scores, a leakage-safe meta-model anomaly/novelty result, calibration status, uncertainty and feature-level explanation.

~~~mermaid
flowchart LR
  A["Chain + wire (if valid) + graph features"] --> B["Four base families"]
  B --> C["Rules · LR/RF/LightGBM · IF/OCSVM/GMM · GNN heads"]
  C --> D["Time-respecting out-of-fold predictions"]
  D --> E["Meta-features: base predictions + motifs + eligible Δ and Π"]
  E --> F["Regularized LR meta-model / optional LightGBM"]
  F --> G["Later independent calibration and holdout"]
  G --> H["PASS 1 local anomaly/risk; freeze seeds"]
~~~

The uploaded diagram specifies four base families and OOF stacking. **Graph propagation cannot be a pass-1 input**, because it uses pass-1 risk as its own seed; propagation is included only in **pass-2 fusion**, capped at 25 of 100. This explicitly resolves the otherwise circular dependency.

**Supervised:** LR, RF, optional LightGBM, and GraphSAGE/GAT or temporal GNN heads where trustworthy labels exist. **Unsupervised fallback:** Isolation Forest, One-Class SVM, Gaussian Mixture and graph novelty; output **novelty rankings**, not fake criminal probabilities. **Meta-training:** expanding chronological folds, fold-local preprocessing/embeddings/MCER, independent calibration and untouched future holdout. Conformal intervals/p-values appear **only if validly calibrated and empirically evaluated**.

**Full model selection, formulas, OOF training, artifact contracts, negative controls and tests:** [Stacking architecture](docs/architecture/stacking-architecture.md), [detection module](src/clarion/detection/README.md), [training module](src/clarion/training/README.md).

## 11. Cross-layer Δ, obfuscation Π and two-pass fusion (§7–§9)

**Δ divergence:** use only trustworthy joined chain/wire views; CCA residual baseline → Δ1 Sybil-collapse, Δ2 identity-spray, Δ3 machine-rhythm, Δ4 route-inconsistency and Δ5 infrastructure-reuse **candidate explanations**. Poor TXID joins, dependence or sensor timing → **ABSTAIN**.

**Π expenditure:** verified controlled-set economic goal and minimum-cost alternative → itemized **Π_fee** (sats), **Π_hop** (counts), **Π_time** (duration), **Π_frag** (outputs/addresses) and **Π_infra** (supported infrastructure context). Unknown goal/payees/fee environment → **ABSTAIN**. High Π measures paid privacy/complexity, **not crime**.

~~~text
Stack score + motif support + valid Δ/Π -> PASS 1 provisional local risk
                                     -> FREEZE seed risk
                                     -> §10 bounded MLRP exposure
                                     -> PASS 2 final risk (propagation <=25/100)
                                     -> Priority P1–P4 + full evidence paths
~~~

The Π–Δ typology is a **two-axis explanation**, never raw Π + Δ arithmetic. Separate source reliability, uncertainty, and calibrated vs uncalibrated score types. See [risk/fusion contract](docs/architecture/risk-propagation-architecture.md) and [fusion module](src/clarion/fusion/README.md).

## 12. Multi-Level Risk Propagation (MLRP) and propagation score (§10)

This is a **risk/exposure propagation** score, not a reward. The uploaded design uses frozen first-pass seeds, typed edge conductance, monetary value-share and time decay with a hard **six-hop scoring horizon**.

~~~text
r_i(k+1) = (1-α) · s_i  +  α · Σ(j→i)[ w(edge_ji) · φ(value_share_ji) · τ(time_gap_ji) · r_j(k) ]
~~~

**Levels:** Address (tainted depth/value inflow), Transaction (value-weighted exposure), Entity (candidate membership aggregation + own Δ/Π), Host/IP (confidence-weighted *observed relay* context), ASN (host-normalized prevalence), **Country (context only; never scored)**. Each scored level uses a separately defined scale.

**Diagram's initial edge weights:** spends/funds **1.0**, observed-broadcast **0.6 × evidence confidence**, co-session **0.3**, candidate member-of **0.8**, hosted-in **0.1**. These are *design hypotheses*, not verified probabilities. To prevent wallet/IP misattribution, maintain separate value-flow and network-context evidence channels.

**Anti-contamination:** value-conserving outgoing shares; temporal/hop decay; no causal backtracking; absorbing exchanges/custodians/CoinJoin services; infrastructure never re-emits risk to other customers. Distinguish forward taint from backward provenance. Deterministic contributing paths take precedence in case dossiers over learned GAT attention.

**Final score:** MLRP is **at most 25 of the 100 risk points**, applied **once after** the frozen pass-1 score. The exact normalization/calibration and P1–P4 thresholds are Phase 4 implementation decisions. No labels → prioritize as a rank, not as an illicit-probability estimate.

**Full equation, edge-type policy, algorithm stages, scoring budget, output contract and tests:** [MLRP architecture](docs/architecture/risk-propagation-architecture.md), [propagation module](src/clarion/propagation/README.md).

## 13. Investigator dashboard, explanations and case dossiers (§11)

Build a **fully offline, investigator-focused console** using local FastAPI, React/TypeScript and a time-bounded graph visualizer. The uploaded diagram requires:

| Screen/panel | Required interactive information |
|---|---|
| **Readiness** | schema, data source/capture coverage, TXID/time alignment, labels and chain-only/cross-layer mode |
| **Ranked leads** | final priority **P1–P4**, local stack score, propagation contribution, confidence status, pattern evidence |
| **Graph explorer** | six typed nodes, chain/wire edge toggles, dated snapshots, risk heat overlay, multi-hop path tracing |
| **Entity and patterns** | MCER candidate clusters, false-merge cautions, peel-chain/mixing/layering witness paths |
| **Stack + Δ + Π** | SHAP/meta-feature explanation if supported; per-signal bars, five Δ explanations, itemized Π bill and abstention |
| **Propagation** | Address/Transaction/Entity/Host/ASN level selector, forward/backward channels, seed IDs, value share, path and boundaries |
| **Time and counterfactual** | chain and relay event timeline; re-score with wire removed when comparable to show incremental cross-layer evidence |
| **Dossier/export** | minimal sufficient graph, plain-language rationale, attribution context (uncertain), model/source IDs, audit and local PDF/CSV |

**Never label a relayed TXID as proof of IP/wallet ownership.** Country provides context only, not a risk score. Show missing evidence as **ABSTAIN**, not zero; distinguish novelty scores from calibrated probabilities. Paginate large graphs and load all fonts/icons/assets locally.

**Screen wireframe, UI data objects, proposed local API routes, export fields, access controls and end-to-end tests:** [Dashboard architecture](docs/architecture/investigator-dashboard-architecture.md), [frontend feature module](frontend/src/features/README.md), [API module](src/clarion/api/README.md), [explanations module](src/clarion/explanations/README.md).

## 14. Privacy, security and forensic integrity

Threat model covers malicious CSV/JSON/XML, XXE/billion-laughs, CSV formula injection, unsafe model deserialization, raw capture exposure, poisoned labels and weights, future leakage, unauthorized case export, supply-chain tampering and runtime network egress. Use immutable raw files with SHA-256, role-limited case access, redaction, input ceilings, safe model formats and tamper-evident audit logs. See [Security](docs/security/README.md).

## 15. Production-oriented repository structure

CLARION is a **modular offline Linux application**, with clear domain/data, graph/ML, investigative, export and security boundaries. The previous generic folders have been audited and supplemented with a **typed domain layer**, a **single application orchestrator**, source-specific adapters, per-feature API routes and dashboard screens, safe reporting and dedicated contract/property/performance tests.

~~~text
CLARION/
├── src/clarion/
│   ├── domain/ core/ application/                 # types, core, orchestration
│   ├── ingestion/adapters/ readiness/ chain/ wire/ storage/
│   ├── graph/ features/ representation/ entity_resolution/ patterns/
│   ├── training/ detection/ divergence/ expenditure/ fusion/ propagation/
│   ├── explanations/ reporting/ evaluation/ synthetic/ security/ observability/
│   ├── api/routers/ cli/
├── frontend/src/
│   ├── app/ components/ lib/ styles/
│   └── features/                                 # readiness, leads, graph,
│       ├── entities/ patterns/ signals/ propagation/ timeline/
│       └── cases/ models/ audit/
├── schemas/ configs/ data/ artifacts/
├── tests/                                       # unit, contracts, integration,
│                                               # property, leakage, adversarial,
│                                               # offline, e2e, performance, fixtures
├── docs/                                        # architecture, data, ml,
│                                               # security, operations, progress
├── experiments/ scripts/ deploy/ .github/
└── README.md
~~~

**Full file-by-file repository ownership, module dependency rules, run flow and exact migration:** [Production structure blueprint](docs/architecture/repository-structure.md). Every standard module folder has a local README describing planned interfaces and tests; `.github/` uses `ARCHITECTURE.md` so the main GitHub homepage README remains visible.

**Source-of-truth separation:** [the original full architecture](docs/architecture/architecture-v4-spec.md), [stacking](docs/architecture/stacking-architecture.md), [risk propagation](docs/architecture/risk-propagation-architecture.md) and [investigator dashboard](docs/architecture/investigator-dashboard-architecture.md) remain intact. All program files are comment-only design stubs; no trained model or functional application is implied.

## 16. Planned core public contracts

- **EvidenceSource / NormalizedTransaction / UTXO / NetworkObservation:** immutable typed record plus source ID and time accuracy.
- **ReadinessDecision:** chain/wire and supervised/unsupervised mode with coverage, statistical quality and reasons.
- **TemporalGraphSnapshot:** typed node/edge records, evidence IDs, graph window and causal cutoff.
- **EntityHypothesis:** versioned address members, signed pair evidence, conflicts, merge/split history.
- **PatternInstance:** motif type, confidence and minimal supporting path.
- **ModelScore:** score type (probability vs novelty), split/model ID, calibration status and uncertainty.
- **DivergenceResult / ExpenditureBill:** independent Δ and Π values with component availability and abstentions.
- **RiskLead / PropagationPath / CaseDossier:** frozen seed, contribution, rank/P1–P4, evidence and redaction.

Define versioned machine-readable schemas in Phase 1 before implementing data consumers; do not silently change contracts.

## 17. Five implementation phases and gates

| Phase | Blocks | Release gate |
|---|---|---|
| **P1: Foundations** | 0, 1A/1B, 2 | all three input formats → typed graph → chain-only baseline, offline tests |
| **P2: Graph and entities** | 3, 4, 5 | leakage-safe embeddings, MCER + motif proofs and false-merge controls |
| **P3: ML and evidence** | 6, 7, 8, first-pass 9 | trained models, time-safe OOF, Δ/Π abstentions, eligible calibration |
| **P4: Product integration** | second-pass 9, 10, 11 | bounded causal risk, dashboard, local API, case evidence export |
| **P5: Research and release** | 12 + all | temporal evaluations, hard-negative FPR, ablations, air-gap Linux package |

**Architecture-first state:** none of the five phases is implemented or validated. See [phase progress](docs/progress/README.md) and [full acceptance criteria](docs/architecture/architecture-v4-spec.md).

## 18. Modular engineering principles

Adopt VoiceDoc's **product-first architecture documentation style**: clear mission, boundaries, end-to-end diagram, module responsibilities, interface contracts, technology alternatives, constraints, measured validation, release criteria and explicit project status. That is a documentation style reference, **not** a reusable technology stack or functional design for this project.

Modules may depend on lower-layer evidence contracts, not circular imports. Prefer typed data interfaces, snapshot-aware functions, model wrappers, immutable run artifacts and additive migrations. No module may fabricate network ownership, use unavailable future data or erase evidence uncertainty.

## 19. Test matrix and release definition

Require parser fuzz/XXE defense, satoshi/time correctness, TXID joins, chain-wire dependence, strict temporal folds and OOF, MCER false-merge/CoinJoin controls, motif benign controls, Δ/Π abstention, conservation and service barriers, role-based reports, disconnected inference and CPU/GPU compatibility. Synthetic L0–L3 results must be labeled synthetic.

**Production-grade aspiration ≠ production-ready status.** A module is complete only after implementation, integrated passing tests, measured claims, evidence links and review signoff.

## 20. Engineering and Git workflow

Architecture scaffolding occurs in a single documentation-only PR. Subsequent implementation phases use separate feature branches and reviewable PRs; never merge unverified executable components or pretend comment stubs are working modules. Protect existing contracts and preserve a transparent phase tracker.

**First executable action after approving architecture:** P1.1 establish actual Python packaging, pinned dependencies, schema registry, secure ingestion fixtures and CI, replacing comment stubs module by module.

## 21. Project status

| Item | Current status |
|---|---|
| SIH architecture and requirement mapping | Mapped to PDF 0–12; **critical open decisions remain** |
| Original CLARION v4 long technical specification | Preserved under docs/architecture |
| VoiceDoc-inspired high-level README and module layout | Documented design scaffold |
| Functional code, trained models, installed dashboard | **Not implemented in this repository** |
| Tests run, model benchmark results and production release | **None claimed** |

## 22. References and licensing

- [SIH26146 architecture and full component design](docs/architecture/architecture-v4-spec.md).
- [VoiceDoc README — reference for **documentation organization only**](https://github.com/shanmukhdatta/VoiceDoc/blob/main/README.md).
- [Elliptic++ researcher dataset](https://github.com/juicy-candy/Elliptic); [BitcoinHeist (UCI)](https://archive.ics.uci.edu/dataset/526/bitcoinheistransomwareaddressdataset); [Bitcoin Core docs](https://developer.bitcoin.org/); [GeoLite2 terms](https://www.maxmind.com/en/geolite/eula).
- [PyTorch Geometric](https://pytorch-geometric.readthedocs.io/), [scikit-learn](https://scikit-learn.org/).

**Licensing:** choose a repository code license only after checking dependency, dataset and offline GeoIP terms; dataset/model weights may use different licenses.

---

**CLARION — Evidence first. Graph intelligence second. Investigative judgment always.**


## 23. Architecture completeness review — critical gaps and traceability

**Architecture review finding (October 2026):** earlier linked detailed design files for schema, cross-layer joins, temporal MCER, experiments, component contracts and security were TODO placeholders. They have now been replaced with proposed technical designs, **not implemented code**. They must be reviewed together against the original [CLARION v4 source specification](docs/architecture/architecture-v4-spec.md).

| Design area | Detailed review document | What must be decided before implementation can depend on it |
|---|---|---|
| Source block-by-block audit (§0–§12) | [Requirement audit and unresolved decisions](docs/architecture/REQUIREMENTS_AUDIT.md) | D01–D12; evidence-backed design gates rather than assumed feasibility |
| Integrated architecture | [Execution modes and failure paths](docs/architecture/architecture-overview.md) | Data plane, chain-only/unsupervised/Δ/Π gating and end-to-end dependency flow |
| Cross-module typing | [Component input/output contracts](docs/architecture/component-contracts.md) | Envelope, schema version, evidence IDs, confidence kinds and abstention states |
| Dataset schema and Bitcoin fidelity | [Canonical data dictionary](docs/data/data-dictionary.md) | Raw SIH arrays to transactions/outpoints/wire observations; satoshis, timestamps, scripts |
| Real and synthetic sources | [Dataset acquisition](docs/data/dataset-acquisition.md) | Separate Elliptic/BitcoinHeist/Bitcoin Core vs synthetic vs organizer dataset evaluation |
| Cross-layer feasibility | [TXID joins and dependence policy](docs/data/join-policy.md) | Does available data *actually contain* decoded observed TXIDs and independently useful wire signals? |
| Temporal clustering | [H1–H5 MCER design](docs/ml/mcer-plan.md) | Confidence, uncertain wire conflicts, false-merge target, fixed-point stop and lineage |
| Graph/model architecture | [Model selection and shared embeddings](docs/ml/model-selection.md) | CPU/hetero GNN baseline, cutoff, costs and incremental utility |
| Experimental validity | [Full experiment plan](docs/ml/experiment-plan.md) | Time-split OOF, generator shift, legitimate FP controls, ablations and confidence |
| Stack scoring | [Stacked anomaly architecture](docs/architecture/stacking-architecture.md) | Mode/calibration, OOF meta, learned vs unsupervised outputs and no MLRP feedback |
| Fusion and propagation | [MLRP scoring](docs/architecture/risk-propagation-architecture.md) | Frozen seeds, financial vs network-context channels, ≤6 hops, at most 25 points |
| Investigator product | [Dashboard/API/dossiers](docs/architecture/investigator-dashboard-architecture.md) | Roles, source-linked views, filters, report hashes, no invented ownership |
| Threat model and release | [Security threats](docs/security/threat-model.md) · [Definition of done](docs/development/definition-of-done.md) | Authorised offline Linux operation, attack tests and actual acceptance logs |

**Do not confuse diagrams and stubs with functioning ML.** The most critical unvalidated premises are real sensor TXID linkage, meaningful independent chain–wire dependence, trustworthy labels at the selected prediction level, and the controlled economic goal required for Π. The correct implementation plan must **abstain or fall back** when these premises fail; no code should fabricate missing evidence.

**Phase 1 is deliberately a feasibility-gate phase:** implement and run strict input/adapters, canonical contracts and a verifiable chain-only baseline **before** asserting that the complete cross-layer research architecture works. The detailed audit distinguishes PDF-specified parts from conservative engineering design decisions.

---
