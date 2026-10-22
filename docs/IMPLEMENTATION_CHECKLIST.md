# CLARION — Requirements-to-code implementation checklist

**Source authority:** [complete v4 architecture](architecture/architecture-v4-spec.md), root README (sections 0–41), implementation playbook and the uploaded master implementation brief. This checklist is **a detailed coverage ledger, not a declaration of 100% completion**.

## Requirement totals

| Status | Count |
|---|---:|
| Implemented and tested | 59 |
| Partially implemented | 37 |
| Blocked | 8 |
| Missing | 29 |
| Implemented, untested | 39 |
| **Total requirements enumerated** | **172** |

**Status semantics:** Implemented and tested = a narrow relevant source-code path passed checks; Implemented, untested = source is written but corresponding scientific/integration acceptance is still pending; Partially implemented = code exists but required breadth, quality gates, or integration is missing; Blocked = missing genuine external data/independent premises; Missing = no executable implementation exists.

**Acceptance policy:** Do not treat unit-test success, source-file existence or a mock API as satisfying a real-world research claim. Verified cases reflect only the specific fixtures or CI checks, not the entire v4 block. The tests column gives **existing or target** paths and does not imply a test specifically asserts every row; missing assertions are listed as future work in the audit.

## Contents

- 0 · Ingestion
- 1A · Bitcoin chain
- 1B · Wire observations
- 2 · Evidence graph
- 3 · Features & representation
- 4 · MCER
- 5 · Bitcoin motifs
- 6 · Stacked learning
- 7 · Cross-layer Delta
- 8 · Economic Pi
- 9 · Fusion and typology
- 10 · MLRP
- 11 · Investigator API and UI
- 12 · Evaluation and release

## Traceability matrix

| ID | Original source | Subfeature | Source-code target | Libraries/dependencies | Status | Concrete acceptance evidence needed | Test location / target |
|---|---|---|---|---|---|---|---|
| REQ-001 | 0 §3.1–3.4 | Bounded CSV imports with verified header | `src/clarion/v4/contracts.py` | Pydantic, CSV/JSON/XML | **Implemented and tested** | Reject duplicated columns, oversized and malformed input | `tests/v4/test_v4_static_pipeline.py` |
| REQ-002 | 0 §3.1–3.4 | JSON list parsing with record bounds | `src/clarion/v4/contracts.py` | Pydantic, CSV/JSON/XML | **Implemented and tested** | Reject incorrect object structure and overflow | `tests/v4/test_v4_static_pipeline.py` |
| REQ-003 | 0 §3.1–3.4 | DTD-free defused XML parsing | `src/clarion/v4/contracts.py` | Pydantic, CSV/JSON/XML | **Partially implemented** | Reject entity expansion with real XML fixtures | `tests/v4/test_v4_static_pipeline.py` |
| REQ-004 | 0 §3.1–3.4 | Source SHA256 manifest and origin | `src/clarion/v4/contracts.py` | Pydantic, CSV/JSON/XML | **Implemented and tested** | Preserve verified bytes and source authorizations | `tests/v4/test_v4_static_pipeline.py` |
| REQ-005 | 0 §3.1–3.4 | Input licence and collection permissions | `src/clarion/v4/contracts.py` | Pydantic, CSV/JSON/XML | **Blocked** | Require actual dataset rights/authorization | `tests/v4/test_v4_static_pipeline.py` |
| REQ-006 | 0 §3.1–3.4 | Canonical transaction schema and enum | `src/clarion/v4/contracts.py` | Pydantic, CSV/JSON/XML | **Implemented and tested** | TXIDs are 64 hex, time aware, no unknown fields | `tests/v4/test_v4_static_pipeline.py` |
| REQ-007 | 0 §3.1–3.4 | Exact BTC decimal to satoshi conversion | `src/clarion/v4/contracts.py` | Pydantic, CSV/JSON/XML | **Implemented and tested** | Sub-satoshi/negative amounts rejected | `tests/v4/test_v4_static_pipeline.py` |
| REQ-008 | 0 §3.1–3.4 | Canonical input prevout key | `src/clarion/v4/contracts.py` | Pydantic, CSV/JSON/XML | **Implemented and tested** | Use exact TXID, vout, vin | `tests/v4/test_v4_static_pipeline.py` |
| REQ-009 | 0 §3.1–3.4 | Canonical output script and amount | `src/clarion/v4/contracts.py` | Pydantic, CSV/JSON/XML | **Implemented and tested** | Unknown scripts remain unknown | `tests/v4/test_v4_static_pipeline.py` |
| REQ-010 | 0 §3.1–3.4 | Wire observation schema and decode proof | `src/clarion/v4/contracts.py` | Pydantic, CSV/JSON/XML | **Implemented and tested** | No fabricated observed TXID | `tests/v4/test_v4_static_pipeline.py` |
| REQ-011 | 0 §3.1–3.4 | Missing-field quarantine with row messages | `src/clarion/v4/contracts.py` | Pydantic, CSV/JSON/XML | **Implemented and tested** | Malformed records included in quarantine | `tests/v4/test_v4_static_pipeline.py` |
| REQ-012 | 0 §3.1–3.4 | Provider mapping contract for SIH/Elliptic/BitcoinHeist | `src/clarion/v4/contracts.py` | Pydantic, CSV/JSON/XML | **Partially implemented** | Use verified real provider columns only | `tests/v4/test_v4_static_pipeline.py` |
| REQ-013 | 0 §3.1–3.4 | Dataset provenance/version registry | `src/clarion/v4/contracts.py` | Pydantic, CSV/JSON/XML | **Partially implemented** | Persist row lineage and rights | `tests/v4/test_v4_static_pipeline.py` |
| REQ-014 | 0 §3.1–3.4 | Training-only label separation | `src/clarion/v4/contracts.py` | Pydantic, CSV/JSON/XML | **Implemented and tested** | Labels cannot become evidence features | `tests/v4/test_v4_static_pipeline.py` |
| REQ-015 | 0 §3.1–3.4 | Input format explicit error handling | `src/clarion/v4/contracts.py` | Pydantic, CSV/JSON/XML | **Implemented and tested** | Unsupported formats rejected | `tests/v4/test_v4_static_pipeline.py` |
| REQ-016 | 0 §3.1–3.4 | Schema migrations for canonical evidence | `src/clarion/v4/contracts.py` | Pydantic, CSV/JSON/XML | **Missing** | Add versioned adapters and compatibility tests | `tests/v4/test_v4_static_pipeline.py` |
| REQ-017 | 0 §3.1–3.4 | Independent readiness and quality gates | `src/clarion/v4/contracts.py` | Pydantic, CSV/JSON/XML | **Partially implemented** | Explicit chain-only and score-type routing | `tests/v4/test_v4_static_pipeline.py` |
| REQ-018 | 1A §4.1 | Verbose Bitcoin Core JSON converter | `src/clarion/v4/graph.py` | Python, exact integer sats | **Implemented, untested** | Approved local export transforms to Tx/Input/Output | `tests/v4/test_v4_static_pipeline.py` |
| REQ-019 | 1A §4.1 | Prevout spends and directed value transfer | `src/clarion/v4/graph.py` | Python, exact integer sats | **Implemented and tested** | Each value link backed by source outpoint | `tests/v4/test_v4_static_pipeline.py` |
| REQ-020 | 1A §4.1 | Unique vin and vout validation | `src/clarion/v4/graph.py` | Python, exact integer sats | **Implemented and tested** | Reject duplicate spending indices | `tests/v4/test_v4_static_pipeline.py` |
| REQ-021 | 1A §4.1 | Known-value conservation and fee | `src/clarion/v4/graph.py` | Python, exact integer sats | **Implemented and tested** | No invented fees for unresolved inputs | `tests/v4/test_v4_static_pipeline.py` |
| REQ-022 | 1A §4.1 | Coinbase support and prohibition on parent vin | `src/clarion/v4/graph.py` | Python, exact integer sats | **Implemented and tested** | Coinbase not treated as ordinary spend | `tests/v4/test_v4_static_pipeline.py` |
| REQ-023 | 1A §4.1 | Missing prevout uncertainty flag | `src/clarion/v4/graph.py` | Python, exact integer sats | **Implemented and tested** | Incomplete ancestry remains nullable | `tests/v4/test_v4_static_pipeline.py` |
| REQ-024 | 1A §4.1 | Reorg/mempool/orphan lifecycle | `src/clarion/v4/graph.py` | Python, exact integer sats | **Partially implemented** | Version chain state and invalidate orphaned evidence | `tests/v4/test_v4_static_pipeline.py` |
| REQ-025 | 1A §4.1 | Script types multisig/taproot parsing | `src/clarion/v4/graph.py` | Python, exact integer sats | **Partially implemented** | Unit tests on actual decoded script families | `tests/v4/test_v4_static_pipeline.py` |
| REQ-026 | 1A §4.1 | Address reuse contextual features | `src/clarion/v4/graph.py` | Python, exact integer sats | **Partially implemented** | No legal wallet attribution | `tests/v4/test_v4_static_pipeline.py` |
| REQ-027 | 1A §4.1 | Confirmed block height and clock separation | `src/clarion/v4/graph.py` | Python, exact integer sats | **Partially implemented** | Block availability distinct from P2P receive time | `tests/v4/test_v4_static_pipeline.py` |
| REQ-028 | 1B §4.2 | Decoded inv/tx observed provenance | `src/clarion/v4/wire_sessions.py` | Python, timestamped sensor facts | **Implemented and tested** | Require observed TXID before joining | `tests/v4/test_extended_evidence.py` |
| REQ-029 | 1B §4.2 | Host and TXID factual relay edge | `src/clarion/v4/wire_sessions.py` | Python, timestamped sensor facts | **Implemented and tested** | Never infer origin or payer | `tests/v4/test_extended_evidence.py` |
| REQ-030 | 1B §4.2 | Source/destination TCP ports typed | `src/clarion/v4/wire_sessions.py` | Python, timestamped sensor facts | **Implemented, untested** | Port contract accepts 0..65535 or null | `tests/v4/test_extended_evidence.py` |
| REQ-031 | 1B §4.2 | Sensor-host time-gap sessionization | `src/clarion/v4/wire_sessions.py` | Python, timestamped sensor facts | **Implemented, untested** | Time-valid dedup + bounded sessions | `tests/v4/test_extended_evidence.py` |
| REQ-032 | 1B §4.2 | Observed TXID coverage features | `src/clarion/v4/wire_sessions.py` | Python, timestamped sensor facts | **Implemented, untested** | Host/sensor count with contextual type | `tests/v4/test_extended_evidence.py` |
| REQ-033 | 1B §4.2 | Port entropy per observed session | `src/clarion/v4/wire_sessions.py` | Python, timestamped sensor facts | **Implemented, untested** | No computed entropy if ports absent | `tests/v4/test_extended_evidence.py` |
| REQ-034 | 1B §4.2 | Independent source/sensor validation | `src/clarion/v4/wire_sessions.py` | Python, timestamped sensor facts | **Blocked** | Independent genuine sensors with timestamp audits | `tests/v4/test_extended_evidence.py` |
| REQ-035 | 1B §4.2 | GeoIP/ASN offline enrichment | `src/clarion/v4/wire_sessions.py` | Python, timestamped sensor facts | **Missing** | Approved offline database + versioned inference | `tests/v4/test_extended_evidence.py` |
| REQ-036 | 1B §4.2 | Subnet aggregation and co-session context | `src/clarion/v4/wire_sessions.py` | Python, timestamped sensor facts | **Partially implemented** | Do not propagate wallet risk through host | `tests/v4/test_extended_evidence.py` |
| REQ-037 | 1B §4.2 | P2P packet capture and transaction decoder | `src/clarion/v4/wire_sessions.py` | Python, timestamped sensor facts | **Missing** | Permissioned genuine Bitcoin protocol captures | `tests/v4/test_extended_evidence.py` |
| REQ-038 | 1B §4.2 | Clock skew and precision diagnostics | `src/clarion/v4/wire_sessions.py` | Python, timestamped sensor facts | **Partially implemented** | Reject noncausal pairing | `tests/v4/test_extended_evidence.py` |
| REQ-039 | 1B §4.2 | Multi-sensor propagation timing tests | `src/clarion/v4/wire_sessions.py` | Python, timestamped sensor facts | **Blocked** | Capture calibration and NAT/collisions hard negatives | `tests/v4/test_extended_evidence.py` |
| REQ-040 | 2 §5 | Typed TX/Address/Entity/Host/ASN/Country nodes | `src/clarion/v4/graph.py` | UTXO+Pydantic+optional PyG | **Partially implemented** | Allowlist all six types; version candidate edges | `tests/v4/test_v4_static_pipeline.py` |
| REQ-041 | 2 §5 | Timestamped factual spends/funds edges | `src/clarion/v4/graph.py` | UTXO+Pydantic+optional PyG | **Implemented and tested** | No causality inversion | `tests/v4/test_v4_static_pipeline.py` |
| REQ-042 | 2 §5 | Host observed relay only | `src/clarion/v4/graph.py` | UTXO+Pydantic+optional PyG | **Implemented and tested** | No host wallet-controller edge | `tests/v4/test_v4_static_pipeline.py` |
| REQ-043 | 2 §5 | Evidence references on graph edges | `src/clarion/v4/graph.py` | UTXO+Pydantic+optional PyG | **Implemented and tested** | Trace edge to original fact | `tests/v4/test_v4_static_pipeline.py` |
| REQ-044 | 2 §5 | As-of availability cutoff snapshot | `src/clarion/v4/graph.py` | UTXO+Pydantic+optional PyG | **Implemented and tested** | No future joins/features | `tests/v4/test_v4_static_pipeline.py` |
| REQ-045 | 2 §5 | Bounded graph export | `src/clarion/v4/graph.py` | UTXO+Pydantic+optional PyG | **Implemented and tested** | Limit graph size by declared threshold | `tests/v4/test_v4_static_pipeline.py` |
| REQ-046 | 2 §5 | Graph persistence and window query | `src/clarion/v4/graph.py` | UTXO+Pydantic+optional PyG | **Partially implemented** | Partition large graph and paginate | `tests/v4/test_v4_static_pipeline.py` |
| REQ-047 | 2 §5 | Tentative candidate entity-membership edge | `src/clarion/v4/graph.py` | UTXO+Pydantic+optional PyG | **Partially implemented** | Confidence type and lineage required | `tests/v4/test_v4_static_pipeline.py` |
| REQ-048 | 2 §5 | Country non-scoring context invariant | `src/clarion/v4/graph.py` | UTXO+Pydantic+optional PyG | **Implemented and tested** | Forbidden financial taint propagation | `tests/v4/test_v4_static_pipeline.py` |
| REQ-049 | 2 §5 | Hetero graph tensors with temporal edge masks | `src/clarion/v4/graph.py` | UTXO+Pydantic+optional PyG | **Implemented, untested** | Never train with future edges | `tests/v4/test_v4_static_pipeline.py` |
| REQ-050 | 2 §5 | Large-graph memory/performance | `src/clarion/v4/graph.py` | UTXO+Pydantic+optional PyG | **Missing** | Benchmark memory and spill-to-disk strategy | `tests/v4/test_v4_static_pipeline.py` |
| REQ-051 | 3 §6.1–6.2 | Causal fee/vsize/output ratio features | `src/clarion/v4/graph.py` | NumPy, scikit-learn, optional PyG | **Implemented and tested** | Missing fields stay nullable | `tests/v4/test_extended_evidence.py` |
| REQ-052 | 3 §6.1–6.2 | Multi-input/output and parent-age features | `src/clarion/v4/graph.py` | NumPy, scikit-learn, optional PyG | **Implemented and tested** | Use no future observation | `tests/v4/test_extended_evidence.py` |
| REQ-053 | 3 §6.1–6.2 | Network view count and port entropy | `src/clarion/v4/graph.py` | NumPy, scikit-learn, optional PyG | **Implemented, untested** | Sensor data not wallet identity | `tests/v4/test_extended_evidence.py` |
| REQ-054 | 3 §6.1–6.2 | Graph node degree/neighbor feature baseline | `src/clarion/v4/graph.py` | NumPy, scikit-learn, optional PyG | **Implemented, untested** | Bound graph reads | `tests/v4/test_extended_evidence.py` |
| REQ-055 | 3 §6.1–6.2 | Unsupervised IsolationForest novelty ranks | `src/clarion/v4/graph.py` | NumPy, scikit-learn, optional PyG | **Implemented and tested** | No probability score type | `tests/v4/test_extended_evidence.py` |
| REQ-056 | 3 §6.1–6.2 | GraphSAGE optional embedding challenger | `src/clarion/v4/graph.py` | NumPy, scikit-learn, optional PyG | **Partially implemented** | Train inside fold, not on test graph | `tests/v4/test_extended_evidence.py` |
| REQ-057 | 3 §6.1–6.2 | GAT optional embedding challenger | `src/clarion/v4/graph.py` | NumPy, scikit-learn, optional PyG | **Partially implemented** | Compare to non-neural baseline | `tests/v4/test_extended_evidence.py` |
| REQ-058 | 3 §6.1–6.2 | Typed HeteroConv forward path | `src/clarion/v4/graph.py` | NumPy, scikit-learn, optional PyG | **Implemented, untested** | Time-cut tensor and no Country guilt score | `tests/v4/test_extended_evidence.py` |
| REQ-059 | 3 §6.1–6.2 | Node2Vec/random-walk baseline | `src/clarion/v4/graph.py` | NumPy, scikit-learn, optional PyG | **Missing** | Real temporal splits and link prediction | `tests/v4/test_extended_evidence.py` |
| REQ-060 | 3 §6.1–6.2 | Temporal heterogeneous GNN fitted model | `src/clarion/v4/graph.py` | NumPy, scikit-learn, optional PyG | **Missing** | Causal training, edge times, heldout | `tests/v4/test_extended_evidence.py` |
| REQ-061 | 3 §6.1–6.2 | Graph link prediction and uncertainty | `src/clarion/v4/graph.py` | NumPy, scikit-learn, optional PyG | **Missing** | Calibrated temporal negative sampling | `tests/v4/test_extended_evidence.py` |
| REQ-062 | 3 §6.1–6.2 | Model-feature registry and versioning | `src/clarion/v4/graph.py` | NumPy, scikit-learn, optional PyG | **Partially implemented** | Schema and fitted cutoff validated at serving | `tests/v4/test_extended_evidence.py` |
| REQ-063 | 4 §7; §26 | H1 common-input proposal with sources | `src/clarion/v4/mcer.py` | Signed evidence partitioner | **Implemented and tested** | Exclude known multi-party/service exceptions | `tests/v4/test_v4_static_pipeline.py` |
| REQ-064 | 4 §7; §26 | H2 probable change proposal | `src/clarion/v4/mcer.py` | Signed evidence partitioner | **Implemented, untested** | Treat as weak nonidentity clue | `tests/v4/test_v4_static_pipeline.py` |
| REQ-065 | 4 §7; §26 | H3 representation cosine similarity | `src/clarion/v4/mcer.py` | Signed evidence partitioner | **Implemented, untested** | Never merge on similarity alone | `tests/v4/test_v4_static_pipeline.py` |
| REQ-066 | 4 §7; §26 | H4 independent contradictory evidence | `src/clarion/v4/mcer.py` | Signed evidence partitioner | **Implemented, untested** | No IP/location hard veto | `tests/v4/test_v4_static_pipeline.py` |
| REQ-067 | 4 §7; §26 | H5 observed infrastructure continuity | `src/clarion/v4/mcer.py` | Signed evidence partitioner | **Implemented, untested** | Small soft weight | `tests/v4/test_v4_static_pipeline.py` |
| REQ-068 | 4 §7; §26 | Signed evidence ledger | `src/clarion/v4/mcer.py` | Signed evidence partitioner | **Implemented, untested** | Source independence and timestamps | `tests/v4/test_v4_static_pipeline.py` |
| REQ-069 | 4 §7; §26 | Conservative group partition | `src/clarion/v4/mcer.py` | Signed evidence partitioner | **Implemented, untested** | No single common-input auto promotion | `tests/v4/test_v4_static_pipeline.py` |
| REQ-070 | 4 §7; §26 | Time-stamped partition lineage | `src/clarion/v4/mcer.py` | Signed evidence partitioner | **Implemented, untested** | Version candidate history | `tests/v4/test_v4_static_pipeline.py` |
| REQ-071 | 4 §7; §26 | Hard service barriers | `src/clarion/v4/mcer.py` | Signed evidence partitioner | **Partially implemented** | Require real service registry and negative controls | `tests/v4/test_v4_static_pipeline.py` |
| REQ-072 | 4 §7; §26 | Human review of false merges | `src/clarion/v4/mcer.py` | Signed evidence partitioner | **Missing** | Capture reviewer correction in versioned partition | `tests/v4/test_v4_static_pipeline.py` |
| REQ-073 | 4 §7; §26 | Multi-party CoinJoin adversarial controls | `src/clarion/v4/mcer.py` | Signed evidence partitioner | **Partially implemented** | Measurable false merge rates | `tests/v4/test_v4_static_pipeline.py` |
| REQ-074 | 4 §7; §26 | Entity ARI/NMI with trusted truth | `src/clarion/v4/mcer.py` | Signed evidence partitioner | **Blocked** | Independent ground truth absent | `tests/v4/test_v4_static_pipeline.py` |
| REQ-075 | 5 §8; §27 | Peel-like directional chain of transfers | `src/clarion/v4/analysis.py` | Python evidence graph | **Implemented and tested** | Source-witnessed 3+ TX candidate | `tests/v4/test_extended_evidence.py` |
| REQ-076 | 5 §8; §27 | Equal-output CoinJoin-like pattern | `src/clarion/v4/analysis.py` | Python evidence graph | **Implemented and tested** | Privacy use not automatically criminal | `tests/v4/test_extended_evidence.py` |
| REQ-077 | 5 §8; §27 | Fan-in/fan-out structure | `src/clarion/v4/analysis.py` | Python evidence graph | **Implemented and tested** | Label batching as benign alternative | `tests/v4/test_extended_evidence.py` |
| REQ-078 | 5 §8; §27 | Multi-step layered aggregation | `src/clarion/v4/analysis.py` | Python evidence graph | **Implemented, untested** | Witnessed parent and child paths | `tests/v4/test_extended_evidence.py` |
| REQ-079 | 5 §8; §27 | Script-address revisitation candidate | `src/clarion/v4/analysis.py` | Python evidence graph | **Implemented, untested** | Never equate with same controller | `tests/v4/test_extended_evidence.py` |
| REQ-080 | 5 §8; §27 | Circular transaction cash flow under UTXO DAG | `src/clarion/v4/analysis.py` | Python evidence graph | **Partially implemented** | Distinguish DAG from script reuse | `tests/v4/test_extended_evidence.py` |
| REQ-081 | 5 §8; §27 | Learned motif novelty embedding | `src/clarion/v4/analysis.py` | Python evidence graph | **Missing** | Train and audit false positives | `tests/v4/test_extended_evidence.py` |
| REQ-082 | 5 §8; §27 | Real wallet-change hard negative patterns | `src/clarion/v4/analysis.py` | Python evidence graph | **Blocked** | Approved labeled legitimate examples | `tests/v4/test_extended_evidence.py` |
| REQ-083 | 5 §8; §27 | Per-pattern confidence and calibration | `src/clarion/v4/analysis.py` | Python evidence graph | **Partially implemented** | Evaluate precision by service cohort | `tests/v4/test_extended_evidence.py` |
| REQ-084 | 6 §9; §28 | Logistic supervised baseline | `src/clarion/v4/ml.py` | scikit-learn, JSON artifacts | **Implemented and tested** | Temporal eligible labels only | `tests/v4/test_extended_evidence.py` |
| REQ-085 | 6 §9; §28 | Random Forest baseline | `src/clarion/v4/ml.py` | scikit-learn, JSON artifacts | **Implemented and tested** | Train only historical groups | `tests/v4/test_extended_evidence.py` |
| REQ-086 | 6 §9; §28 | IsolationForest unsupervised baseline | `src/clarion/v4/ml.py` | scikit-learn, JSON artifacts | **Implemented and tested** | Score rank, never guilt likelihood | `tests/v4/test_extended_evidence.py` |
| REQ-087 | 6 §9; §28 | Chronological OOF meta-logistic | `src/clarion/v4/ml.py` | scikit-learn, JSON artifacts | **Implemented and tested** | No in-sample leakage | `tests/v4/test_extended_evidence.py` |
| REQ-088 | 6 §9; §28 | Group-purged future holdout | `src/clarion/v4/ml.py` | scikit-learn, JSON artifacts | **Partially implemented** | Audit dependent entity families at fold boundary | `tests/v4/test_extended_evidence.py` |
| REQ-089 | 6 §9; §28 | Optional PyG GraphSAGE/GAT embeddings | `src/clarion/v4/ml.py` | scikit-learn, JSON artifacts | **Partially implemented** | Per-fold rebuild required | `tests/v4/test_extended_evidence.py` |
| REQ-090 | 6 §9; §28 | LightGBM, OCSVM and GMM full family zoo | `src/clarion/v4/ml.py` | scikit-learn, JSON artifacts | **Missing** | Complete comparative benchmarks required | `tests/v4/test_extended_evidence.py` |
| REQ-091 | 6 §9; §28 | Uncalibrated JSON logistic export | `src/clarion/v4/ml.py` | scikit-learn, JSON artifacts | **Implemented, untested** | No pickle execution and SHA verified | `tests/v4/test_extended_evidence.py` |
| REQ-092 | 6 §9; §28 | JSON logistic inference endpoint/script | `src/clarion/v4/ml.py` | scikit-learn, JSON artifacts | **Implemented, untested** | Feature/schema/cutoff checks | `tests/v4/test_extended_evidence.py` |
| REQ-093 | 6 §9; §28 | Supervised calibration + conformal uncertainty | `src/clarion/v4/ml.py` | scikit-learn, JSON artifacts | **Missing** | Independent calibration cohort needed | `tests/v4/test_extended_evidence.py` |
| REQ-094 | 6 §9; §28 | Model registry rollback and signed artifacts | `src/clarion/v4/ml.py` | scikit-learn, JSON artifacts | **Partially implemented** | Lock checkpoints, input digests and model lineage | `tests/v4/test_extended_evidence.py` |
| REQ-095 | 6 §9; §28 | Drift population stability analysis | `src/clarion/v4/ml.py` | scikit-learn, JSON artifacts | **Implemented, untested** | Diagnostic only, sample sufficiency | `tests/v4/test_extended_evidence.py` |
| REQ-096 | 6 §9; §28 | CPU/GPU execution configuration | `src/clarion/v4/ml.py` | scikit-learn, JSON artifacts | **Partially implemented** | Matching torch/CUDA wheel and seeding | `tests/v4/test_extended_evidence.py` |
| REQ-097 | 6 §9; §28 | Real measured AUROC/AUPRC | `src/clarion/v4/ml.py` | scikit-learn, JSON artifacts | **Blocked** | Trusted external labels and legal dataset | `tests/v4/test_extended_evidence.py` |
| REQ-098 | 7 §10; §29.1 | Paired view input and independence gate | `src/clarion/v4/signals.py` | CCA, permutation tests | **Partially implemented** | Verified capture independence | `tests/v4/test_v4_static_pipeline.py` |
| REQ-099 | 7 §10; §29.1 | Heldout CCA dependence baseline | `src/clarion/v4/signals.py` | CCA, permutation tests | **Implemented, untested** | Chronological distinct train/holdout samples | `tests/v4/test_v4_static_pipeline.py` |
| REQ-100 | 7 §10; §29.1 | Permutation null against chance pairing | `src/clarion/v4/signals.py` | CCA, permutation tests | **Implemented, untested** | Corrected p values across comparisons | `tests/v4/test_v4_static_pipeline.py` |
| REQ-101 | 7 §10; §29.1 | Δ1 joint dependence report | `src/clarion/v4/signals.py` | CCA, permutation tests | **Partially implemented** | No individual guilt attribution | `tests/v4/test_v4_static_pipeline.py` |
| REQ-102 | 7 §10; §29.1 | Δ2 timing residual component | `src/clarion/v4/signals.py` | CCA, permutation tests | **Missing** | Capture/network confound control | `tests/v4/test_v4_static_pipeline.py` |
| REQ-103 | 7 §10; §29.1 | Δ3 session residual component | `src/clarion/v4/signals.py` | CCA, permutation tests | **Missing** | Validated P2P session semantics | `tests/v4/test_v4_static_pipeline.py` |
| REQ-104 | 7 §10; §29.1 | Δ4 geography contextual component | `src/clarion/v4/signals.py` | CCA, permutation tests | **Missing** | No controller-location inference | `tests/v4/test_v4_static_pipeline.py` |
| REQ-105 | 7 §10; §29.1 | Δ5 infrastructure continuity component | `src/clarion/v4/signals.py` | CCA, permutation tests | **Missing** | Sensor source bias audited | `tests/v4/test_v4_static_pipeline.py` |
| REQ-106 | 7 §10; §29.1 | Contrastive cross-view residual model | `src/clarion/v4/signals.py` | CCA, permutation tests | **Missing** | Independent real pairs and benchmarks | `tests/v4/test_v4_static_pipeline.py` |
| REQ-107 | 7 §10; §29.1 | Mandatory ABSTAIN on missing premises | `src/clarion/v4/signals.py` | CCA, permutation tests | **Implemented and tested** | Absent evidence never reported as zero | `tests/v4/test_v4_static_pipeline.py` |
| REQ-108 | 8 §11; §29.2 | Economic goal explicit schema | `src/clarion/v4/signals.py` | Unit-aware counterfactual ratios | **Implemented, untested** | Verified same-payee/goal constraints | `tests/v4/test_v4_static_pipeline.py` |
| REQ-109 | 8 §11; §29.2 | Actual fee burden satoshis | `src/clarion/v4/signals.py` | Unit-aware counterfactual ratios | **Implemented, untested** | Known fee+prevout only | `tests/v4/test_v4_static_pipeline.py` |
| REQ-110 | 8 §11; §29.2 | Path hop overhead | `src/clarion/v4/signals.py` | Unit-aware counterfactual ratios | **Implemented, untested** | Observed actual path versus feasible baseline | `tests/v4/test_v4_static_pipeline.py` |
| REQ-111 | 8 §11; §29.2 | Time delay overhead | `src/clarion/v4/signals.py` | Unit-aware counterfactual ratios | **Implemented, untested** | Complete recorded time windows | `tests/v4/test_v4_static_pipeline.py` |
| REQ-112 | 8 §11; §29.2 | Output fragmentation overhead | `src/clarion/v4/signals.py` | Unit-aware counterfactual ratios | **Implemented, untested** | Count repeated/competing outputs | `tests/v4/test_v4_static_pipeline.py` |
| REQ-113 | 8 §11; §29.2 | Infrastructure cost overhead | `src/clarion/v4/signals.py` | Unit-aware counterfactual ratios | **Implemented, untested** | Explicit offline provider cost evidence | `tests/v4/test_v4_static_pipeline.py` |
| REQ-114 | 8 §11; §29.2 | Controlled minimum same-goal counterfactual | `src/clarion/v4/signals.py` | Unit-aware counterfactual ratios | **Blocked** | Cannot be fabricated from public chain | `tests/v4/test_v4_static_pipeline.py` |
| REQ-115 | 8 §11; §29.2 | Component-wise ABSTAIN and units | `src/clarion/v4/signals.py` | Unit-aware counterfactual ratios | **Implemented and tested** | Never sum heterogeneous raw units | `tests/v4/test_v4_static_pipeline.py` |
| REQ-116 | 9 §12 | Pass-1 local review priority score | `src/clarion/v4/analysis.py` | Deterministic bounded scoring | **Implemented and tested** | No propagation input | `tests/v4/test_v4_static_pipeline.py` |
| REQ-117 | 9 §12 | Explicit anomaly vs probability score type | `src/clarion/v4/analysis.py` | Deterministic bounded scoring | **Implemented and tested** | Synthetic model score not treated as guilt | `tests/v4/test_v4_static_pipeline.py` |
| REQ-118 | 9 §12 | Optional Δ entry only when eligible | `src/clarion/v4/analysis.py` | Deterministic bounded scoring | **Partially implemented** | Validate signal provenance | `tests/v4/test_v4_static_pipeline.py` |
| REQ-119 | 9 §12 | Optional Π entry only when eligible | `src/clarion/v4/analysis.py` | Deterministic bounded scoring | **Partially implemented** | Validate baseline and counterfactual | `tests/v4/test_v4_static_pipeline.py` |
| REQ-120 | 9 §12 | Motif rule contribution ledger | `src/clarion/v4/analysis.py` | Deterministic bounded scoring | **Implemented and tested** | Store witness and alternative | `tests/v4/test_v4_static_pipeline.py` |
| REQ-121 | 9 §12 | P1–P4 review ranking | `src/clarion/v4/analysis.py` | Deterministic bounded scoring | **Implemented and tested** | Output points 0..100 | `tests/v4/test_v4_static_pipeline.py` |
| REQ-122 | 9 §12 | Π–Δ high/low typology quadrants | `src/clarion/v4/analysis.py` | Deterministic bounded scoring | **Missing** | Abstain-safe classification and holdout checks | `tests/v4/test_v4_static_pipeline.py` |
| REQ-123 | 9 §12 | Learned calibrated fusion/uncertainty | `src/clarion/v4/analysis.py` | Deterministic bounded scoring | **Missing** | Independent labeled production cohort | `tests/v4/test_v4_static_pipeline.py` |
| REQ-124 | 9 §12 | Immutable seed manifest | `src/clarion/v4/analysis.py` | Deterministic bounded scoring | **Implemented and tested** | Frozen first-pass hash | `tests/v4/test_v4_static_pipeline.py` |
| REQ-125 | 10 §13 | Forward value-weighted spends propagation | `src/clarion/v4/analysis.py` | Directed, capped temporal exposure | **Implemented and tested** | Exact causal outpoint | `tests/v4/test_v4_static_pipeline.py` |
| REQ-126 | 10 §13 | Six-hop and 25-point hard caps | `src/clarion/v4/analysis.py` | Directed, capped temporal exposure | **Implemented and tested** | Never exceed bounds | `tests/v4/test_v4_static_pipeline.py` |
| REQ-127 | 10 §13 | Hop attenuation and time order | `src/clarion/v4/analysis.py` | Directed, capped temporal exposure | **Implemented and tested** | No self-circular risk | `tests/v4/test_v4_static_pipeline.py` |
| REQ-128 | 10 §13 | Unscored Country context | `src/clarion/v4/analysis.py` | Directed, capped temporal exposure | **Implemented and tested** | No country crime score | `tests/v4/test_v4_static_pipeline.py` |
| REQ-129 | 10 §13 | Blocked service transaction barrier | `src/clarion/v4/analysis.py` | Directed, capped temporal exposure | **Implemented and tested** | No contamination across known service | `tests/v4/test_v4_static_pipeline.py` |
| REQ-130 | 10 §13 | Source-to-target witness paths | `src/clarion/v4/analysis.py` | Directed, capped temporal exposure | **Implemented and tested** | Traceable contributions | `tests/v4/test_v4_static_pipeline.py` |
| REQ-131 | 10 §13 | Distinct five scored-level aggregate outputs | `src/clarion/v4/analysis.py` | Directed, capped temporal exposure | **Partially implemented** | No host/ASN crime classification without calibration | `tests/v4/test_v4_static_pipeline.py` |
| REQ-132 | 10 §13 | Nonfinancial co-session context channel | `src/clarion/v4/analysis.py` | Directed, capped temporal exposure | **Missing** | Display only, never financial taint | `tests/v4/test_v4_static_pipeline.py` |
| REQ-133 | 10 §13 | Backward exposure view | `src/clarion/v4/analysis.py` | Directed, capped temporal exposure | **Missing** | Evidence-aware inversion not guilt propagation | `tests/v4/test_v4_static_pipeline.py` |
| REQ-134 | 10 §13 | Sensitivity and counterfactual propagation audit | `src/clarion/v4/analysis.py` | Directed, capped temporal exposure | **Missing** | Service hard negatives and false positive budgets | `tests/v4/test_v4_static_pipeline.py` |
| REQ-135 | 11 §14–15 | Localhost-only API serve mode | `src/clarion/api/main.py` | FastAPI, React, SQLite | **Implemented and tested** | No public listener | `tests/v4/test_review_api.py` |
| REQ-136 | 11 §14–15 | Read-only lead and manifest endpoints | `src/clarion/api/main.py` | FastAPI, React, SQLite | **Implemented and tested** | Actual run evidence | `tests/v4/test_review_api.py` |
| REQ-137 | 11 §14–15 | Server-side search, priority and sorting | `src/clarion/api/main.py` | FastAPI, React, SQLite | **Implemented, untested** | Paged, bounded filter | `tests/v4/test_review_api.py` |
| REQ-138 | 11 §14–15 | Bounded neighborhood graph queries | `src/clarion/api/main.py` | FastAPI, React, SQLite | **Implemented, untested** | Selected TXID only | `tests/v4/test_review_api.py` |
| REQ-139 | 11 §14–15 | Orange/white responsive dashboard | `src/clarion/api/main.py` | FastAPI, React, SQLite | **Implemented and tested** | React TypeScript build | `tests/v4/test_review_api.py` |
| REQ-140 | 11 §14–15 | Lead queue and case dossier drawer | `src/clarion/api/main.py` | FastAPI, React, SQLite | **Implemented and tested** | Real JSON and source links | `tests/v4/test_review_api.py` |
| REQ-141 | 11 §14–15 | Motif/MCER/Delta/Pi evidence panels | `src/clarion/api/main.py` | FastAPI, React, SQLite | **Partially implemented** | Missing fields shown as unavailable | `tests/v4/test_review_api.py` |
| REQ-142 | 11 §14–15 | Live local case review page | `src/clarion/api/main.py` | FastAPI, React, SQLite | **Implemented, untested** | Evidence-linked persisted state | `tests/v4/test_review_api.py` |
| REQ-143 | 11 §14–15 | SQLite case review schema/migrations | `src/clarion/api/main.py` | FastAPI, React, SQLite | **Implemented, untested** | Persistent across restart | `tests/v4/test_review_api.py` |
| REQ-144 | 11 §14–15 | Optimistic review updates and idempotency | `src/clarion/api/main.py` | FastAPI, React, SQLite | **Implemented, untested** | Conflicts 409, replay stable | `tests/v4/test_review_api.py` |
| REQ-145 | 11 §14–15 | Token-gated local write authorization | `src/clarion/api/main.py` | FastAPI, React, SQLite | **Implemented, untested** | No unauthenticated writes | `tests/v4/test_review_api.py` |
| REQ-146 | 11 §14–15 | Tamper-evident case review event ledger | `src/clarion/api/main.py` | FastAPI, React, SQLite | **Implemented, untested** | Audit hash verifies locally | `tests/v4/test_review_api.py` |
| REQ-147 | 11 §14–15 | Provenance hash verification endpoint | `src/clarion/api/main.py` | FastAPI, React, SQLite | **Implemented, untested** | Detect altered evidence artifacts | `tests/v4/test_review_api.py` |
| REQ-148 | 11 §14–15 | CSV evidence and JSON dossier export | `src/clarion/api/main.py` | FastAPI, React, SQLite | **Implemented and tested** | No formula injection | `tests/v4/test_review_api.py` |
| REQ-149 | 11 §14–15 | PDF report exporter | `src/clarion/api/main.py` | FastAPI, React, SQLite | **Partially implemented** | Render and visually QA | `tests/v4/test_review_api.py` |
| REQ-150 | 11 §14–15 | Full six-type temporal graph interactions | `src/clarion/api/main.py` | FastAPI, React, SQLite | **Partially implemented** | Bounded preview; true time graph needed | `tests/v4/test_review_api.py` |
| REQ-151 | 11 §14–15 | Timeline and heatmap visualizations | `src/clarion/api/main.py` | FastAPI, React, SQLite | **Missing** | Historical filters and reusable view | `tests/v4/test_review_api.py` |
| REQ-152 | 11 §14–15 | SHAP model explanations | `src/clarion/api/main.py` | FastAPI, React, SQLite | **Missing** | Real fitted model and holdout calibration | `tests/v4/test_review_api.py` |
| REQ-153 | 11 §14–15 | Real role-based multiuser authorization | `src/clarion/api/main.py` | FastAPI, React, SQLite | **Missing** | Single-user token is not RBAC | `tests/v4/test_review_api.py` |
| REQ-154 | 11 §14–15 | Accessible mobile and keyboard controls | `src/clarion/api/main.py` | FastAPI, React, SQLite | **Partially implemented** | E2E UX and accessibility testing | `tests/v4/test_review_api.py` |
| REQ-155 | 12 §18–21; §30–33 | Synthetic L0/L1 transaction fixtures | `src/clarion/v4/evaluation.py` | pytest, GitHub Actions, report docs | **Implemented and tested** | Deterministic source and truth sidecar | `tests/v4/test_extended_evidence.py` |
| REQ-156 | 12 §18–21; §30–33 | Independent synthetic holdout and ROC/PR | `src/clarion/v4/evaluation.py` | pytest, GitHub Actions, report docs | **Implemented and tested** | No claim real-world accuracy | `tests/v4/test_extended_evidence.py` |
| REQ-157 | 12 §18–21; §30–33 | Case/group time-leakage checks | `src/clarion/v4/evaluation.py` | pytest, GitHub Actions, report docs | **Partially implemented** | Verify folds and entity version timestamps | `tests/v4/test_extended_evidence.py` |
| REQ-158 | 12 §18–21; §30–33 | Test missing prevout and conservation | `src/clarion/v4/evaluation.py` | pytest, GitHub Actions, report docs | **Implemented and tested** | Reject incorrect money totals | `tests/v4/test_extended_evidence.py` |
| REQ-159 | 12 §18–21; §30–33 | Test relay nonownership and abstention | `src/clarion/v4/evaluation.py` | pytest, GitHub Actions, report docs | **Implemented and tested** | No host→wallet risk | `tests/v4/test_extended_evidence.py` |
| REQ-160 | 12 §18–21; §30–33 | Independent legitimate-service hard negatives | `src/clarion/v4/evaluation.py` | pytest, GitHub Actions, report docs | **Blocked** | Real representative legitimate datasets | `tests/v4/test_extended_evidence.py` |
| REQ-161 | 12 §18–21; §30–33 | Closed-loop human validation and false positives | `src/clarion/v4/evaluation.py` | pytest, GitHub Actions, report docs | **Missing** | Review corrections and sample metrics | `tests/v4/test_extended_evidence.py` |
| REQ-162 | 12 §18–21; §30–33 | Ablation benchmark and uncertainty intervals | `src/clarion/v4/evaluation.py` | pytest, GitHub Actions, report docs | **Implemented, untested** | Same holdout across study arms | `tests/v4/test_extended_evidence.py` |
| REQ-163 | 12 §18–21; §30–33 | MCER false merge and ARI/NMI | `src/clarion/v4/evaluation.py` | pytest, GitHub Actions, report docs | **Partially implemented** | Trusted entity truth required | `tests/v4/test_extended_evidence.py` |
| REQ-164 | 12 §18–21; §30–33 | Calibration, Brier and FPR budget metrics | `src/clarion/v4/evaluation.py` | pytest, GitHub Actions, report docs | **Missing** | External heldout cohort | `tests/v4/test_extended_evidence.py` |
| REQ-165 | 12 §18–21; §30–33 | API auth and database regression tests | `src/clarion/v4/evaluation.py` | pytest, GitHub Actions, report docs | **Implemented, untested** | Token, revision, invalid payload | `tests/v4/test_extended_evidence.py` |
| REQ-166 | 12 §18–21; §30–33 | Frontend TS build and responsive shell | `src/clarion/v4/evaluation.py` | pytest, GitHub Actions, report docs | **Implemented and tested** | React compile and smoke | `tests/v4/test_extended_evidence.py` |
| REQ-167 | 12 §18–21; §30–33 | Docker/Compose offline packaging | `src/clarion/v4/evaluation.py` | pytest, GitHub Actions, report docs | **Missing** | Secure image, signed local assets | `tests/v4/test_extended_evidence.py` |
| REQ-168 | 12 §18–21; §30–33 | Linux installer and recovery automation | `src/clarion/v4/evaluation.py` | pytest, GitHub Actions, report docs | **Missing** | Verifiable rollback and signed release | `tests/v4/test_extended_evidence.py` |
| REQ-169 | 12 §18–21; §30–33 | Dependency lockfile and SBOM | `src/clarion/v4/evaluation.py` | pytest, GitHub Actions, report docs | **Missing** | Reproducibility and license scan | `tests/v4/test_extended_evidence.py` |
| REQ-170 | 12 §18–21; §30–33 | CI tests, lint, security, docs integrity | `src/clarion/v4/evaluation.py` | pytest, GitHub Actions, report docs | **Implemented and tested** | All required branch checks pass | `tests/v4/test_extended_evidence.py` |
| REQ-171 | 12 §18–21; §30–33 | Offline egress/security policy checks | `src/clarion/v4/evaluation.py` | pytest, GitHub Actions, report docs | **Partially implemented** | OS and browser firewall acceptance | `tests/v4/test_extended_evidence.py` |
| REQ-172 | 12 §18–21; §30–33 | Evidence retention, backup, data removal | `src/clarion/v4/evaluation.py` | pytest, GitHub Actions, report docs | **Partially implemented** | Documented case lifecycle and legal rules | `tests/v4/test_extended_evidence.py` |

## Important mismatches and follow-up

The original `src/clarion/chain/`, `wire/`, `detection/`, `frontend/src/features/` and other modular paths include many comment-only blueprint files. Existing working logic is concentrated in `src/clarion/v4/`, `src/clarion/application/`, `src/clarion/api/main.py` and `frontend/src/app/App.tsx`. Do not count a placeholder as complete merely because a directory README describes the intended module.

**High-risk external blockers:** permissioned Bitcoin Core/SIH data, independent P2P TXID observation semantics, real label definitions, empirically calibrated cross-view Δ residuals, verified same-goal economic Π counterfactuals, false-merge ground truth and real deployment-quality accuracy. No result is fabricated to close these rows. The new local review API adds practical functionality, but a single-user secret is not a multi-user authentication/authorization system.

**Change procedure:** update the corresponding REQ row, implementation path, fixture/test and result after every future code change. Re-run all local/CI checks and the source-specific acceptance criterion before promoting to "Implemented and tested". 
