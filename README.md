# CLARION v4
> **CLARION — Offline, Explainable Bitcoin Transaction and Network-Traffic Intelligence.** An evidence-first investigator platform for SIH26146; uses graph ML and classical learning to prioritize reviewable leads **without claiming that a relay IP owns a wallet**.

**Project:** Smart India Hackathon 2026 · SIH26146 · NTRO · Blockchain & Cybersecurity  
**Target:** Linux, fully offline at inference time · **Repository status: architecture and documentation scaffold ONLY**  
**Current stage:** Architecture gap audit and cross-component contract review. **No executable application, trained model, security test or completed benchmark is represented as working. Critical dataset and calibration decisions remain open.**

### Start implementing CLARION — follow this first

**[Beginner-friendly phase-by-phase implementation playbook](docs/development/implementation-playbook.md)** — the practical starting point for a new contributor. It explains the recommended **technology stack and libraries**, where to obtain **real Bitcoin datasets**, how to **generate synthetic CSV/JSON/XML when official data is missing**, how to structure and train baseline/GNN/stacked models without data leakage, what each existing repository module should implement, what deliverables to produce, and the **P0–P5 acceptance gates**. It also lists planned CLI interfaces clearly marked **not yet implemented**.

**Read order:** [Implementation playbook](docs/development/implementation-playbook.md) → [data acquisition](docs/data/dataset-acquisition.md) → [canonical data dictionary](docs/data/data-dictionary.md) → [development workflow](docs/development/developer-guide.md) → your assigned module README. **Do not begin by training a model or implementing the dashboard before the P1 data/readiness/chain-only slice is verified.**

---

## Current code and requirements review — October 22, 2026

**Implementation exists, but the original 13-block v4 architecture is not yet complete.** The old 2026 scaffold-only status above is historical and should not be interpreted as the current codebase. The canonical synthetic pipeline, offline React interface, and Python regression tests run; some advanced statistical claims and module blueprints remain incomplete.

- [Current executable architecture](docs/ARCHITECTURE.md)
- [172-item implementation checklist](docs/IMPLEMENTATION_CHECKLIST.md)
- [Independent feature completeness audit](docs/FINAL_FEATURE_AUDIT.md)
- [Technical decisions](docs/IMPLEMENTATION_DECISIONS.md)
- [API specification](docs/API_SPECIFICATION.md) and [SQLite case database](docs/DATABASE_DESIGN.md)
- [Local setup and verification](docs/LOCAL_TESTING.md)
- [All folder-by-folder technical guides](docs/FOLDER_README_INDEX.md)

No synthetic or uncalibrated review score is a declaration of wrongdoing. No observed relay IP is automatically a wallet owner.

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


---

## 24. Component-by-component implementation map — read before starting

This new part is intentionally structured like the **40-section [VoiceDoc README](https://github.com/shanmukhdatta/VoiceDoc/blob/main/README.md)**: instead of putting all mechanisms into one high-level picture, **each architecture block has its own internal flow, operations, module ownership, input/output contract, failure response and small first implementation task.** The architectures below are **proposed implementations**, not claims that these modules currently run. Sections 1–23 above and all detailed design documents remain unchanged.

**How the numbering maps to the SIH v4 source:** §25 = block 0; §26 = 1A; §27 = 1B; §28 = 2; §29 = 3; §30 = 4; §31 = 5; §32 = 6; §33 = 7; §34 = 8; §35 = 9; §36 = 10; §37 = 11; §38 = 12. §39 explains operational orchestration and §40 gives a practical contributor route.

| First question | Read here | Phase | Expected first visible evidence |
|---|---|---|---|
| Where do approved transactions/IP records come from? | [§25](#25-block-0--source-readiness-and-evidence-ingestion-architecture) | P1 | source hashes, row diagnostics, readiness route |
| How is real Bitcoin value flow recovered? | [§26](#26-block-1a--bitcoin-utxo-and-on-chain-feature-architecture) | P1 | linked TXID:vout edges and correct satoshi accounting |
| What can an IP/TXID sensor actually establish? | [§27](#27-block-1b--network-observation-and-context-architecture) | P1 | observed-relay edges, not wallet owner claims |
| How are six node types assembled? | [§28](#28-block-2--temporal-cross-layer-evidence-graph-architecture) | P1 | typed as-of graph with source references |
| How do representations get trained? | [§29](#29-block-3--causal-feature-and-graph-representation-architecture) | P2 | reproducible tabular and graph embeddings |
| How does MCER merge/split candidate entities? | [§30](#30-block-4--mcer-temporal-entity-hypothesis-architecture) | P2 | H1–H5 evidence ledger and tentative memberships |
| How are peeling/mixing/layering patterns found? | [§31](#31-block-5--motif-and-behavior-pattern-architecture) | P2 | timestamped witness path and benign alternative |
| Which model should be trained and stacked? | [§32](#32-block-6--detectors-oof-stacking-and-training-architecture) | P3 | time-safe OOF matrix and honest score type |
| When is cross-layer Δ legal/valid? | [§33](#33-block-7--delta-cross-layer-divergence-architecture) | P3 | paired residual or explicit ABSTAIN |
| When can Π be computed? | [§34](#34-block-8--pi-economic-expenditure-architecture) | P3 | itemized cost units or explicit ABSTAIN |
| How does a provisional lead become final? | [§35](#35-block-9--two-pass-local-fusion-architecture) | P3/P4 | frozen local seed, once-only final fusion |
| How is exposure propagated without guilt by proximity? | [§36](#36-block-10--bounded-multi-level-risk-propagation-architecture) | P4 | directed six-hop path and hard service barrier |
| What does the investigator see? | [§37](#37-block-11--local-investigator-dashboard-and-report-architecture) | P4 | reproducible lead → graph → dossier |
| How do we know the model works? | [§38](#38-block-12--evaluation-ablation-and-scientific-validity-architecture) | P5 | audited held-out tests, limitation report |
| How is everything actually operated? | [§39](#39-cross-cutting-operations--orchestration-security-and-artifacts) / [§40](#40-contributor-walkthrough--build-it-in-the-right-order) | P0–P5 | repeatable run with phase acceptance proof |

**Technology and dataset selection are in [§5](#5-recommended-technology-stack) and [the implementation playbook](docs/development/implementation-playbook.md).** Existing \`src/clarion/\` module folders are file ownership boundaries; most implementation files remain documentation/comment stubs. Interface/function names in this appendix describe **responsibilities to implement**, not existing callables.

## 25. Block 0 — Source readiness and evidence ingestion architecture

**Purpose:** make potentially untrusted CSV, JSON and XML inputs auditable before allowing any graph/model stage. Source material can be official SIH samples, a properly documented local Bitcoin Core export, an approved benchmark or clearly named synthetic fixtures.

~~~mermaid
flowchart LR
 A["Authorized file + data rights"] --> B["Hash / source & sensor manifest"]
 B --> C["Bounded CSV / JSON / XML reader"]
 C --> D["Source-specific adapter"]
 D --> E["Units + UTC + schema validator"]
 E --> F["Canonical Parquet + quarantine"]
 F --> G["TXID/time/label/coverage audit"]
 G --> H{"Evidence sufficient?"}
 H -->|No wire| I["CHAIN_ONLY"]
 H -->|No labels| J["UNSUPERVISED_ONLY"]
 H -->|Gates valid| K["Eligible additional stages"]
~~~

**Internal operations and ownership:**

| Operation (planned responsibility) | How it works | File(s) / tool |
|---|---|---|
| Source registration | inspect permission/license, record SHA-256, origin, import time and true dataset schema | \`storage/manifest.py\`, \`storage/catalog.py\`; hashlib |
| Safe parse | bounded file size and row/depth, reject unsafe XML external entities and malformed arrays, preserve source row IDs | \`ingestion/readers.py\`; Python CSV/JSON, defusedxml |
| Adapter mapping | distinguish SIH, Core, Elliptic++, BitcoinHeist rather than treating unlike data as the same schema | \`ingestion/adapters/\` |
| Canonical validation | parse decimal BTC into exact integer sats; assert UTC offset/time precision, unique keys, valid TXIDs and explicit nulls | \`ingestion/validation.py\`, \`domain/\`; Pydantic |
| Evidence persistence | original files read-only; write rebuildable Parquet and a quarantine/error ledger | \`storage/parquet_store.py\`; PyArrow/DuckDB |
| Readiness decision | measure coverage, exact TXID joins, clock accuracy, label provenance and independent pairing | \`readiness/{coverage,joins,routing}.py\` |

**Inputs → outputs:** original authorized bytes and a source manifest → \`EvidenceSource\`, normalized Transaction/Input/Output/NetworkObservation records, failure report and \`ReadinessDecision\`. **Fallback:** if SIH data is missing, begin with reproducible *labeled-as-synthetic* fixtures; if network rows lack genuine decoded observed TXIDs, route to CHAIN_ONLY. Dataset links, source limitations and generation details: [acquisition](docs/data/dataset-acquisition.md), [data dictionary](docs/data/data-dictionary.md), [playbook §4–5](docs/development/implementation-playbook.md).

**First contributor task:** create a tiny permitted dataset with two valid transfers, one malformed row and two independent sensor observations. Define expected normalized rows **before** implementing parsers. **Proof:** same semantic records after CSV/JSON/XML import; bad row gets a named error; nothing derives a wallet owner from IP.

## 26. Block 1A — Bitcoin UTXO and on-chain feature architecture

**Purpose:** reproduce on-chain transaction/value relationships precisely rather than drawing arbitrary address-to-address money edges. Bitcoin inputs spend specific previous outputs (\`prev_txid:vout\`); address associations can be absent or ambiguous.

~~~mermaid
flowchart LR
 A["Validated transactions + prevouts"] --> B["Classify coinbase / standard / nonstandard"]
 B --> C["Resolve outpoint references"]
 C --> D["Track UTXO spend / fund facts"]
 D --> E["Fee + size / script eligibility"]
 E --> F["As-of chain features"]
 F --> G["Directed on-chain evidence edges"]
 C -. "Unresolved prevout" .-> H["UNKNOWN amount / partial lineage"]
~~~

**Internal operations:**

| Operation | What a junior implements | Owner |
|---|---|---|
| Transaction decoding | preserve txid, inputs and outputs, block status, locktime and scripts with valid units | \`chain/transactions.py\` |
| UTXO lookup | map each input's prevout to precisely one earlier output when source material contains it | \`chain/utxo.py\` |
| Value conservation | for fully known ordinary transactions check \`sum(inputs) = sum(outputs) + fee\` in sats; otherwise keep fee unknown | \`chain/transactions.py\` / tests |
| Change/address heuristics | annotate possible change and address reuse as hypotheses, not conclusive ownership | \`chain/features.py\` |
| Behavioral features | record input/output count, fan-out, fee-per-vbyte when known, burst windows and value-flow statistics with cutoff | \`chain/features.py\`, \`features/chain.py\` |

**Input → output:** valid tx/input/output and prevout tables → directed spends/funds evidence, numeric and nullable features, source row links and an explicit unknown-lineage mask. **Technology:** exact integer accounting, Parquet/DuckDB; only small correctness graphs in NetworkX. **Fail safely:** coinbase needs separate accounting; unresolved prevout, unknown script/address and reorganization state cannot be guessed. Header timestamp is not global relay time.

**First task:** document two linked transactions with one \`txid:vout\` spent; verify value plus fee conservation and show a failed/unresolved prevout scenario. **Proof:** every financial edge points to a real referenced outpoint and retains source IDs.

## 27. Block 1B — Network observation and context architecture

**Purpose:** represent observations made by a lawfully operated P2P sensor, not supposed wallet identities. A TXID may appear at many relays; repeated sightings are not independent proof of origination.

~~~mermaid
flowchart LR
 A["Authorized sensor logs"] --> B["Validate sensor/vantage/time"]
 B --> C["Decode actual observed TXID if present"]
 C --> D["Deduplicate same-sensor retransmissions"]
 D --> E["Bounded sessions + host features"]
 E --> F["Optional local ASN / GeoIP lookup"]
 F --> G["J1 observed-relay edges / J2 context"]
 C -->|No TXID proof| H["No J1 association"]
~~~

**Internal operations:**

| Operation | Explanation | Owner |
|---|---|---|
| Observation record | keep sensor ID, observation time and precision, src/dst IP/port, direction/event type, TXID decoding provenance | \`wire/observations.py\` |
| Sessionization | window events by sensor and endpoint identity; distinguish repeat from independent view; compute port/rhythm features | \`wire/sessions.py\` |
| TXID matching | exact decoded TXID equality only; no match inferred from timing, location or equal amounts | \`readiness/joins.py\` |
| IP enrichment | licensed local ASN/country/hosting DB with version and UNKNOWN when absent | \`wire/enrichment.py\` |
| Coverage gate | count true TXID-bearing messages, independent sensors and temporal overlap; route CHAIN_ONLY when unsuitable | \`readiness/coverage.py\` |

**Input → output:** permitted tagged network observations → timestamped Host–Transaction *observed relay* facts, Host–Host session context, optional ASN/Country metadata, coverage and uncertainty. **Never output:** Host→Address owner or "original broadcaster" asserted from relay alone. Cross-layer data can improve a model only after the separate dependence test.

**First task:** one TXID, three hosts, duplicate same-sensor observation, missing TXID in another record. **Proof:** three valid relay observations as supported, deduplicated repeats per policy, **zero** ownership edges, and an explicit missing-data mode. See [J0–J3 policy](docs/data/join-policy.md).

## 28. Block 2 — Temporal cross-layer evidence graph architecture

**Purpose:** join verified chain facts and permissible observational context into a queryable six-type graph. Every edge has a type, event time, cutoff, source ID and *observed vs inferred* confidence category.

~~~mermaid
flowchart TD
 A["Canonical chain records"] --> C["Evidence edge factory"]
 B["Eligible wire / enrichment"] --> C
 C --> D["Node & edge allowlist"]
 D --> E["Timestamp + evidence-reference checks"]
 E --> F["As-of graph snapshots"]
 F --> G["Query paths / neighborhoods"]
 F --> H["PyG typed sparse adapter"]
 I["Versioned MCER candidate membership"] -. "Only candidate edge" .-> D
~~~

**Node contract:** Transaction, Address, Entity (candidate), Host, ASN, Country. **Edge contract:** spends/funds in the correct financial direction, observed-relay Host→Transaction, contextual co-session and hosting/geography, candidate Address→Entity. **Forbidden:** observational host-to-wallet ownership; arbitrary Country risk.

**Internal operations:**

| Operation | Internal contract | Owner |
|---|---|---|
| Type registry | define stable typed IDs, allowable source/target relations and edge semantics | \`graph/types.py\` |
| Builder | materialize edges only from normalized evidence or separately marked candidate hypotheses | \`graph/builder.py\` |
| Snapshot service | include facts only available by cutoff T; version entity memberships and reorg status | \`graph/snapshots.py\` |
| ML representation adapter | export type-specific tensors, index maps, edge times and missingness masks | \`graph/pyg_adapter.py\` |
| Query boundary | limit hop, row and time windows; retain path-to-raw evidence in graph explorer | \`api/routers/graph.py\` (P4) |

**Input → output:** normalized source tables + versioned candidate membership → immutable/rebuildable typed snapshot, node/edge index and explicit evidence trail. **First task:** build the graph for a three-transaction synthetic fixture, write down expected node types and edge directions, then test that removing an edge after cutoff does not change an earlier snapshot.

## 29. Block 3 — Causal feature and graph representation architecture

**Purpose:** derive model-ready information from as-of evidence. Begin with understandable numeric features, then compare learned embeddings only when data and evaluation warrant them. Sharing an embedding space does not imply a common human controller.

~~~mermaid
flowchart LR
 A["As-of graph snapshot"] --> B["Train-safe feature registry"]
 B --> C["Chain / optional wire features"]
 C --> D["Baseline statistics / Node2Vec"]
 C --> E["Sampled GraphSAGE"]
 E --> F["Optional typed GAT / temporal encoder"]
 D --> G["Versioned embeddings + masks"]
 F --> G
 G --> H["MCER / motif / detector / eligible Delta"]
~~~

**Internal operations:**

| Operation | Function and choice | Owner |
|---|---|---|
| Feature specification | define name, subject, units, \`available_at\`, missingness and provenance; fit scalers on past-only folds | \`features/registry.py\`, \`features/{chain,wire,temporal}.py\` |
| Non-neural baseline | small-graph degree and random-walk/Node2Vec embedding, reproducible seed | \`representation/random_walk.py\` |
| Inductive encoder | PyTorch/PyG GraphSAGE with train-period graph and bounded temporal neighbor sampling | \`representation/graphsage.py\` |
| Optional attention | GAT as a measured challenger, not as causality/ownership proof | \`representation/gat.py\` |
| Heterogeneous / time-aware | type-specific projections and permitted paired views only; no future edges | \`representation/hetero_temporal.py\` |

**Input → output:** graph and fold cutoff → embeddings keyed by stable subject ID, snapshot hash, schema, missingness mask and model version. **Default training route:** scikit-learn baseline → 2-layer GraphSAGE on a manageable eligible graph → optional GAT/temporal challenger after measured future-holdout uplift. A CPU baseline is mandatory; use CUDA/PyG only after compatibility benchmarking.

**First task:** compute degrees and a simple feature table for a known snapshot, train a small *task-appropriate* graph model if labels are eligible, and demonstrate a feature-level future-edge leakage test. See [model selection](docs/ml/model-selection.md).

## 30. Block 4 — MCER temporal entity hypothesis architecture

**Purpose:** derive cautious *candidate* address groups through Mutual-Constraint Temporal Entity Resolution (MCER), rather than pretending one shared transaction or observed IP proves a single wallet owner.

~~~mermaid
flowchart TD
 A["Snapshot + eligible embeddings"] --> B["H1 common-input / H2 change / H3 similarity proposals"]
 A --> C["H4 uncertain wire conflicts / H5 continuity hypotheses"]
 B --> D["Signed evidence ledger"]
 C --> D
 D --> E["CoinJoin / service / source-independence constraints"]
 E --> F["Conservative partition optimizer"]
 F --> G{"Stable, not contradicted?"}
 G -->|No| F
 G -->|Yes / budget exhausted| H["Versioned tentative entities + unknown pairs"]
 H --> I["Merge/split lineage at next cutoff"]
~~~

**H1:** common inputs are a *positive heuristic* except multi-party spending. **H2:** probable change outputs are hypotheses. **H3:** embedding similarity proposes neighbors, does not force merges. **H4:** wire timing/country disagreement is not a reliable hard identity veto without independent proof. **H5:** same infrastructure/port rhythms can support a *continuity hypothesis*, not real controller identity.

**Internal operations:** \`entity_resolution/proposals.py\` generates evidence-carrying address pairs; \`constraints.py\` groups correlated sensors, records signed support/conflict and avoids known CoinJoin/service false merges; \`optimizer.py\` makes conservative bounded iterations and abstains on contradictory pairs; \`lineage.py\` records candidate group merge/split versions and historical explanations.

**Input → output:** graph snapshot, H1–H5 pair proposals and conflict ledger → entity version, members, confidence **kind**, unresolved pairs, signed source paths and lineage. **First task:** one normal co-spend and one multi-party CoinJoin-like transaction. The second must not collapse unrelated users into one confirmed entity; compare false merges against sealed synthetic truth. Details: [MCER plan](docs/ml/mcer-plan.md).

## 31. Block 5 — Motif and behavior pattern architecture

**Purpose:** find suspicious-*looking* transaction behavior as candidate graph structures with verifiable witness paths, alongside legitimate alternatives. Motifs are not independent evidence of criminal motive.

~~~mermaid
flowchart LR
 A["UTXO graph snapshot + candidate entities"] --> B["Bounded temporal path enumeration"]
 B --> C["Peel chains"]
 B --> D["Mixing / CoinJoin-like structures"]
 B --> E["Layering / fan-in / fan-out / cycles"]
 C --> F["Motif witness ledger"]
 D --> F
 E --> F
 F --> G["Benign service and time controls"]
 G --> H["Candidate instance + sources + alternatives"]
~~~

**Internal operations:** \`patterns/peel.py\` searches repeated partial value transfers with plausible change paths; \`patterns/mixing.py\` recognizes multi-party/value-equal structures but marks privacy/service alternatives; \`patterns/layering.py\` handles time-consistent fan-in/out and bounded cycles without fabricating ownership; \`patterns/novelty.py\` optionally compares subgraph representations with learned/background patterns.

**Input → output:** as-of UTXO subgraph and service/candidate-entity context → \`PatternInstance\` with kind, witness node/edge IDs, times, uncertainty and benign alternatives. **Libraries:** sparse graph traversals and simple rules first; optional learned subgraph embeddings later. **First task:** mark a generated peel-like path and an innocent processor-batching hard negative. Explain which *actual edges* make a candidate; a classifier should not become the only explanation.

## 32. Block 6 — Detectors, OOF stacking and training architecture

**Purpose:** learn usable *rankings or supported probabilities* from valid historical evidence, without temporal data leakage, same-fold meta-label leakage or fabricated training data.

~~~mermaid
flowchart TD
 A["Task + label subject/provenance audit"] --> B{"Usable labels and future holdout?"}
 B -->|No| C["IF / GMM novelty only"]
 B -->|Yes| D["Chronological, purged expanding folds"]
 D --> E["Fold-local features / graph / MCER / encoder"]
 E --> F["Rules + LR/RF + IF + GraphSAGE heads"]
 F --> G["Forward OOF base prediction table"]
 G --> H["LR meta-model; eligible motif/Delta/Pi masks"]
 H --> I["Later independent calibration, if justified"]
 I --> J["Untouched future holdout + model registry"]
 C --> K["Novelty score type, never fraud probability"]
~~~

**Four base families:** explicit rules, supervised Logistic Regression/Random Forest/optional LightGBM, unsupervised Isolation Forest/One-Class SVM/GMM, and graph classification/novelty heads (GraphSAGE/GAT where viable).

**Internal operations:**

| Operation | Exactly what is required | Owner |
|---|---|---|
| Split design | fix prediction subject and label availability; group/purge temporal overlap; reserve latest holdout | \`training/splits.py\` |
| Fitted transforms | rebuild scaler, feature registry, MCER and embeddings within each training fold | \`training/trainer.py\` |
| Base learners | train/score separate model families on eligible fold-local features | \`detection/{supervised,unsupervised,graph_heads}.py\` |
| OOF meta | join base predictions by subject/cutoff/fold; train regularized LR only on honest forward OOF rows | \`detection/stacking.py\` |
| Calibration & registry | later independent calibration only with valid labels; persist split, hash, model, schema, subject and score type | \`training/registry.py\` |
| Drift/decision | re-evaluate on later data and hard benign cohorts; keep baseline if challenger fails | \`training/drift.py\` |

**Input → output:** frozen eligible datasets + chronological folds → per-fold model files, OOF matrix, meta-model, holdout report, explanations and calibrated score only where justified. **No labels?** A novelty-ranked list, not percent criminality. **No enough OOF?** best single model or explicitly non-trained combination. **Never include same-run propagation in pass-1 model features.**

**First task:** run logistic regression, random forest and Isolation Forest on one *properly matched* track/subject task; show exact folds and honest held-out scores. Add GraphSAGE only after this baseline. Detailed training recipe: [playbook §9](docs/development/implementation-playbook.md), [stacking architecture](docs/architecture/stacking-architecture.md).

## 33. Block 7 — Δ cross-layer divergence architecture

**Purpose:** test whether *genuinely paired* chain and network observations disagree more than plausible baseline behavior. An unpaired or weakly dependent dataset must yield **ABSTAIN**, not an invented Δ score.

~~~mermaid
flowchart TD
 A["Chain view + exact J1 sensor TXID view"] --> B["Join/clock/coverage gate"]
 B --> C{"Sufficient independent paired evidence?"}
 C -->|No| Z["Delta ABSTAIN + reason"]
 C -->|Yes| D["Sensor-aware dependence null test"]
 D --> E{"Out-of-sample association credible?"}
 E -->|No| Z
 E -->|Yes| F["Past-only CCA / residual baseline"]
 F --> G["Delta1..5 candidate diagnostics"]
 G --> H["Residual + named sources + uncertainty"]
~~~

**Internal operations:** \`divergence/paired_views.py\` constructs valid subject-level aligned views without assuming same operator; \`cca.py\` fits a train-only linear CCA/residual comparator before contrastive challengers; \`components.py\` reports Δ1 Sybil-collapse, Δ2 identity spray, Δ3 machine rhythm, Δ4 supported route inconsistency and Δ5 infrastructure reuse *as candidate explanations only*; \`abstain.py\` enforces source/clock/independence/null-test gates.

**Input → output:** qualified paired chain/wire features, source precision and train-only null model → unit/scale-aware residual, per-component evidence, coverage and confidence, **or ABSTAIN**. **Important:** IP geography and one TXID seen across many hosts cannot be used as proof of multiple controlled wallets or physical impossibility.

**First task:** on controlled synthetic paired logs, compare correctly paired vs sensor/time-preserving shuffled pairs; demonstrate failure of unpaired input and low coverage. Never market success here as real-world cross-layer attribution. See [join policy](docs/data/join-policy.md).

## 34. Block 8 — Π economic expenditure architecture

**Purpose:** characterize extra observable effort/cost required by a **specified and supported economic goal**. Expensive privacy, extra hops or unusual fees are not automatically crime.

~~~mermaid
flowchart TD
 A["Verified goal / controlled inputs / payee constraints"] --> B{"Cost objective identifiable?"}
 B -->|No| Z["Pi component or total ABSTAIN"]
 B -->|Yes| C["Build feasible minimum-cost baseline"]
 C --> D["Observed outcome + fee environment"]
 D --> E["Pi_fee / hop / time / frag / infra"]
 E --> F["Itemized units + assumptions + evidence"]
 F --> G["Uncertainty and independent eligibility"]
~~~

**Internal operations:** \`expenditure/objectives.py\` validates known actor-controlled set, intended outcome and time restrictions without guessing from a graph; \`baseline.py\` constructs a feasible matched comparison under known fee and transfer constraints; \`components.py\` computes separate fee (sats), hop (count), delay (time), fragmentation (count) and supportable infrastructure context, preserving **different units**; \`abstain.py\` marks each unknown goal, missing prevout/fee regime or counterfactual infeasibility.

**Input → output:** supported objective, fee environment, controlled transaction subset and a comparison baseline → itemized \`ExpenditureBill\` **or item-level ABSTAIN**. **Do not add sats + hops + seconds numerically**; any normalized summary requires its own validated interpretation.

**First task:** construct two legitimate simulated paths to the same payment goal, a direct transfer and a delayed/multi-hop transfer. Validate their bill and rerun after hiding the payee: the unsupported cost must abstain. See [economic objective dictionary](docs/data/data-dictionary.md).

## 35. Block 9 — Two-pass local fusion architecture

**Purpose:** combine distinct evidence streams into a reviewed lead without circular use of risk propagation or claiming unsupported calibrated probabilities.

~~~mermaid
flowchart LR
 A["Eligible stack or novelty"] --> E["Pass-1 local fusion"]
 B["Motif witnesses"] --> E
 C["Delta if valid"] --> E
 D["Pi if valid"] --> E
 E --> F["Freeze+hash s(T) local seeds"]
 F --> G["Block 10 MLRP"]
 G --> H["Single capped pass-2 fusion"]
 E --> H
 H --> I["Priority + separate contributions + caveats"]
~~~

**Internal operations:** \`fusion/local.py\` checks subject/score type, missingness, evidence independence and appropriate calibration; \`fusion/typology.py\` describes the Π–Δ two-axis category **only when both axes are usable**; \`fusion/final.py\` freezes provisional vector and computes a final ranking with propagation **applied once** at a maximum **25/100 points**, including an auditable decomposition.

**Input → output:** named local signals → provisional score/rank, immutable seed manifest + hash → final lead object with priority P1–P4 **only where threshold policy is calibrated/justified**, otherwise honest review rank. Do not sum correlated p-values or coerce ABSTAIN to zero; thresholds await valid independent evidence. **No pass-1 feedback from current MLRP.**

**First task:** test identical frozen seeds with propagation enabled/disabled; assert repeat evaluation cannot inflate the second-pass contribution. Evaluate how priority behaves when labels, Δ and Π are missing. Details: [two-pass fusion](docs/architecture/risk-propagation-architecture.md).

## 36. Block 10 — Bounded Multi-Level Risk Propagation architecture

**Purpose:** estimate bounded evidence-connected *exposure*, not inherited guilt by association. Frozen pass-1 local leads are the only seeds. All financial and observational channels retain different causal semantics.

~~~mermaid
flowchart TD
 A["Hashed pass-1 seeds"] --> B["Eligible as-of typed edge filter"]
 B --> C["Forward financial value-share traversal"]
 B --> D["Separate observational host/context paths"]
 C --> E["Hop <= 6 / time decay / service absorption"]
 D --> F["No host/ASN customer-to-customer risk relay"]
 E --> G["Path ledger and per-level exposure"]
 F --> G
 G --> H["Single <=25/100 point contribution"]
~~~

**Internal operations:** \`propagation/edges.py\` validates type/direction, conductance and spendable-value fractions; \`diffusion.py\` calculates hop/time-decayed exposure from immutable s without backwards time travel; \`boundaries.py\` applies absorbing exchange/custody/CoinJoin policies, prevents infrastructure contagion and forbids numeric Country risk; \`paths.py\` records reproducible ordered contributing source edges and uncertainty.

**Levels:** Address, Transaction, candidate Entity, Host and ASN can have **distinctly defined** exposure scales; the sixth, Country, is **context only** and unscored. Graph source edge weights described in the architecture are design hypotheses requiring tests, not verified risk probabilities. **Financial risk must not spread through a shared ASN, IP or relay into unrelated customers.** Preserve forward exposure vs backward provenance.

**Input → output:** frozen seed manifest and valid snapshot → bounded path contribution, separate context/financial summaries, cut-off/stop reasons and final cap-ready adjustment. **First task:** seed one synthetic address then compare one normal downstream flow, a 1→200 fan-out, a custodian boundary and an innocent one-hop neighbor. Demonstrate conservation, time ordering, ≤6 hops and capped adjustment. See [MLRP design](docs/architecture/risk-propagation-architecture.md).

## 37. Block 11 — Local investigator dashboard and report architecture

**Purpose:** make leads *auditable* in a disconnected Linux environment. The UI should explain evidence and uncertainty rather than reimplement model inference.

~~~mermaid
flowchart LR
 A["Versioned local run snapshots"] --> B["FastAPI: typed read-only endpoints"]
 B --> C["Readiness and ranked leads"]
 C --> D["Time-filtered graph / entity / motif / signals"]
 D --> E["Propagation / why this lead?"]
 E --> F["Reviewer notes, authorized case dossier"]
 F --> G["CSV / JSON / PDF with hashes and redaction"]
 B --> H["Local access and audit policy"]
~~~

**Internal operations:**

| Screen/route | Investigator action and contract | Implementation target |
|---|---|---|
| Readiness | inspect dataset/sensor/label gates and CHAIN_ONLY reasons | \`frontend/src/features/readiness/\`; \`api/routers/runs.py\` |
| Leads | filter P1–P4 or rank with score type, source quality and uncertainty | \`features/leads/\`; \`api/routers/leads.py\` |
| Graph/timeline | bounded as-of neighborhood, typed edges and original evidence IDs | \`features/graph/\`, \`timeline/\`; graph router |
| Entity/patterns | candidate memberships and change history; witness motifs, benign alternatives | \`features/entities/\`, \`patterns/\` |
| Signals/propagation | stack contribution, Δ/Π itemized/ABSTAIN and bounded source paths | \`features/signals/\`, \`propagation/\` |
| Cases | authorized redact/export with report hash, no raw private path leak | \`features/cases/\`; \`reporting/\`, case router |
| Model/audit | trained artifact metadata, calibration status, analyst actions and evaluation limits | \`features/models/\`, \`audit/\` |

**Technology:** locally bound FastAPI/Pydantic, React/TypeScript/Vite, a bounded graph renderer, local fonts/icons and audited CSV/JSON/PDF. **Security:** role-limited reports, size/hop/time pagination, CSV formula sanitization, immutable raw hash references, input rejection and no external CDN/telemetry. The model is trained outside serving; HTTP handlers only read authorized scored artifacts.

**Input → output:** local run ID, legal user context and paginated evidence results → defensible case report with hashes and explicit uncertainty. **First task:** click from one synthetic lead → source TXID → evidence path → model/source version → redacted exported case, entirely offline. See [investigator design](docs/architecture/investigator-dashboard-architecture.md).

## 38. Block 12 — Evaluation, ablation and scientific validity architecture

**Purpose:** demonstrate what genuinely works, what only works with synthetic truth, and what remains unverified. No claims of clinical-like/forensic certainty or real-world identification from artificial generator success.

~~~mermaid
flowchart TD
 A["Dataset provenance + task/label audit"] --> B["Freeze chronological / grouped split"]
 B --> C["Train-only graph, features and models"]
 C --> D["Untouched holdout / synthetic tiers L0-L3"]
 D --> E["Prediction / MCER / motif / Delta-Pi / MLRP metrics"]
 E --> F["Hard-benign controls + ablations + shift tests"]
 F --> G["Reproducibility, calibration & resource report"]
 G --> H["Release gate + explicit limitations"]
~~~

**Internal operations:** \`evaluation/metrics.py\` calculates only justified task-specific PR-AUC, precision@K, Brier/calibration and pairwise clustering ARI/NMI; \`evaluation/leakage.py\` audits fold-local embeddings and cutoff; \`evaluation/ablations.py\` tests incremental value of wire, graph encoder, MCER, stack, Δ/Π and MLRP where each is eligible; \`evaluation/robustness.py\` probes service false positives, independent sensor dropout, clock skew, generator shift and abuse.

**Tracks must stay separate:** A1 Elliptic++ graph task; A2 BitcoinHeist address task; A3 Bitcoin Core UTXO correctness; B controlled synthetic end-to-end truth; C official SIH dataset only after verified access/schema. Synthetic tiers L0–L3 show controlled difficulty, **not observed real criminal behavior**. No fabricated labels, measured improvements or accuracy percentages.

**Input → output:** future-fold predictions, evidence trace and *sealed* independent truth → versioned metrics, cohort counts, ablation tables, runtime peak memory/time, abstentions, failures and known limitations. **First task:** demonstrate one real chronological split, a deliberately leaky version caught by tests and a benign false-positive control. [Experiment design](docs/ml/experiment-plan.md) and [definition of done](docs/development/definition-of-done.md) govern release.

## 39. Cross-cutting operations — orchestration, security and artifacts

The 14 source blocks cannot be implemented as isolated notebooks. The \`src/clarion/application/\` orchestrator is a **planned single coordinator** for stage ordering, safe retries and artifact compatibility; algorithms remain in their own modules.

~~~mermaid
flowchart TD
 A["Developer registers approved source"] --> B["Import and readiness manifest"]
 B --> C["Select CHAIN_ONLY/CROSS_LAYER and SUPERVISED/NOVELTY"]
 C --> D["Build as-of graph and features"]
 D --> E["Load version-matched model OR train in separate dev job"]
 E --> F["MCER + motifs + supported Delta/Pi"]
 F --> G["Pass-1 seeds frozen and hashed"]
 G --> H["MLRP then capped pass-2"]
 H --> I["Evidence dossier + localhost UI"]
 I --> J["Audit, reproducibility and safe offline package"]
~~~

**How each supporting operation works:**

| Operation | Planned implementation responsibility | Important invariant |
|---|---|---|
| Run configuration | \`core/config.py\`, \`configs/profiles/\` CPU/GPU/chain-only/cross-layer modes | unknown config keys and incompatible schema versions fail explicitly |
| Domain contracts | \`domain/\`, \`schemas/\` | one versioned meaning of TXID, sat, UTC, source reference, score type and ABSTAIN |
| Stage coordination | \`application/{pipeline,stages,run_manager,mode_policy}.py\` | restart uses matching source/config/model hashes; no hidden re-fitting |
| CLI | \`cli/main.py\` and future command handlers | current \`clarion\` supports basic help/version; **other subcommands are planned**, not working |
| Safe training | \`training/\`, \`scripts/train/\` | dev-initiated, train-only folds; no on-demand model fitting inside API |
| Model and asset registry | \`artifacts/models/\` manifests and trusted serialized model assets | reject incompatible or untrusted weights; no internet dependency at inference |
| Security and logging | \`security/\`, \`observability/\`, \`tests/adversarial/\` | privacy-redacted audit and uploads; no inference-time egress |
| Final distribution | \`deploy/\`, \`scripts/release/\`, \`tests/offline/\` | locally bundled Python wheels, fonts, UI assets and approved model/GeoIP data |

**Sample local execution story (a target acceptance test, not commands supported by the current CLI):** contributor creates a reproducible synthetic fixture; imports and hashes it; gets CHAIN_ONLY and UNSUPERVISED_ONLY when wire/labels are missing; builds a typed graph and rule lead; opens a local ranked lead, follows two evidential source links, sees that Δ/Π abstained, and exports a redacted dossier. Later research PRs replace rule-only analytics with eligible trained models without altering the evidence interface.

**Artifacts must be versioned:** input hashes and rights; canonical/parquet schema; graph cutoff; features and missingness; candidate entity/motif version; model/split/calibration card; separate Δ/Π status; frozen pass-1 vector; MLRP paths and cap; final risk rank; case/export hashes; actual tests and operating environment. See [repository structure](docs/architecture/repository-structure.md), [developer guide](docs/development/developer-guide.md), and [operations](docs/operations/README.md).

## 40. Contributor walkthrough — build it in the right order

**For a fresher starting today:** use [the implementation playbook](docs/development/implementation-playbook.md) as the full step-by-step plan; this README explains *why each stage exists and how its internal pieces connect*. Every contributor should work on a small reviewable phase PR, not promise the entire architecture in one branch.

**Phase-by-phase practical route:**

1. **P0 — understand and inspect:** clone on Linux, read source constraints, run currently available \`uv sync --locked\`, \`uv run clarion --help\` and existing tests, record actual outcomes; read §25–§28 and the dataset licenses. If required tools are unavailable, install them using their official instructions first.
2. **P1 — make one end-to-end chain-only slice real:** generate tiny clearly synthetic CSV/JSON/XML cases with known truth; implement and test schema, SHA-256 provenance, Bitcoin prevout resolution, wire-absence readiness and six-node-type graph; produce an explainable *rule* lead. Never invent official SIH metadata or IP ownership.
3. **P2 — add causal representation and hypotheses:** as-of feature registry, statistical baselines, optional GraphSAGE with PyG, conservative MCER and edge-backed motifs; compare with innocuous batching and CoinJoin hard negatives.
4. **P3 — train one task properly:** choose transaction *or* address label, lock chronological folds, fit only on past data, compare LR/RF/IF with graph challenger, assemble OOF meta-predictions, calculate Δ and Π **only if data gates pass**, freeze pass-1 seeds. Maintain supervised versus novelty output types.
5. **P4 — turn results into a local product:** implement capped six-hop MLRP, independent financial/context channels, once-only final fusion, local FastAPI, React graph/lead screens and redacted dossier; test no network access and source-link reproducibility.
6. **P5 — verify, do not merely demo:** distinct real-benchmark and synthetic evaluations, time-leakage and benign cohort controls, Δ/Π abstention, MLRP contamination, CPU/memory benchmarks, offline Linux packaging, installation/run docs and limitations report.

**What each team PR should contain:** (1) exact v4 block and module responsibility; (2) source rights/data units and example fixture; (3) inputs/outputs and schema version; (4) negative/fallback case; (5) tests **actually** run with logs; (6) input/model/result hashes; (7) reviewer acceptance and rollback; (8) progress status in [docs/progress](docs/progress/README.md). Never mark implementation VERIFIED because a comment stub, README or test filename exists.

**Release acceptance story:** on a disconnected Linux computer with locally preinstalled compatible assets, a reviewer imports an allowed evidence file, sees a truthful readiness decision, reconstructs a source-linked graph, receives a supported lead with available/abstained signals, explores bounded propagation, and exports an audited report. Any absent data or invalid label is handled openly. A separate research report compares simple baselines and advanced models on genuinely eligible holdouts.

> **Documentation status:** Sections 24–40 describe **how to implement and validate** every original block while preserving sections 1–23. They do not assert those features, trained checkpoints, dataset joins, model accuracy or offline application have been implemented or tested. Follow [module folders](src/clarion/README.md) and [definition of done](docs/development/definition-of-done.md) to promote each stage from design → implemented → verified.

---

## 41. Static v4 code and orange/white frontend — October 22, 2026

**Read this update before treating the architecture as implemented or validated.**
The original sections 1–40 above have been preserved. The new implementation
branch adds substantial **statically authored** Python/React code while leaving
research premises and scientific verification explicitly conditional.

- [Beginner setup and later commands](docs/development/V4_BEGINNER_START_HERE.md)
- [Exact canonical data pipeline and schemas](docs/development/V4_PIPELINES_AND_SCHEMAS.md)
- [Block-by-block implementation audit and unverified status](docs/development/V4_STATIC_IMPLEMENTATION_STATUS.md)
- Python modules: `src/clarion/v4/` (contracts, ingestion, UTXO graph,
  MCER H1–H5 proposal ledger, motifs, models, Δ/Π gates, risk fusion,
  propagation, storage, evaluation, reports and security)
- React application: `frontend/` (minimalist terracotta orange/white, offline
  pages for overview/leads/graph/patterns/entities/Δ/Π/propagation/models/cases/audit)
- Canonical local CLI: `scripts/v4_pipeline.py`
- Bitcoin Core converter: `scripts/data/prepare_bitcoin_core.py`
- Static tests: `tests/v4/`. Opt-in verification: `.github/workflows/v4-manual-review.yml`

**Not verified:** The newly authored source, tests, TypeScript build and training
were intentionally not executed during this pass. Several earlier module stubs
remain, and the new modules do not certify full production implementation.
No real-world AML accuracy, independently valid chain–wire Δ, or verified
economic Π can be honestly asserted without actual evidence.

**Science-first default:** questionable network observation never means a
wallet-owner relationship; Country is context only; absent independent paired
evidence or goals means ABSTAIN; synthetic labels are training/evaluation fixtures
and never evidence of guilt. Avoid merging without downstream integration checks.

<!-- CLARION_FOLDER_INDEX_LINK -->
## Folder-by-folder technical architecture and implementation audit

Browse [all 103 folder READMEs](docs/FOLDER_README_INDEX.md) for a file index, diagrams, interfaces, technologies and status. [Feature coverage audit](docs/architecture/FEATURE_IMPLEMENTATION_AUDIT.md) separates tested synthetic paths, partial methods and missing real-world evidence.
<!-- /CLARION_FOLDER_INDEX_LINK -->
