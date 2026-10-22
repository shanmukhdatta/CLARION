# CLARION v4 static implementation audit — 22 October 2026

**READ THIS BEFORE CLAIMING COMPLETION.** Code was authored and committed *without
running tests, training, the UI build, or integration smoke tests in this pass*,
per request. A file existing is not proof it runs. No actual SIH production
dataset, authorized Bitcoin Core import, real paired P2P capture or calibrated
ground-truth labels are verified here.

## Source of truth and feature-by-feature status

| Block | Implemented statically | Important missing evidence / validation |
|---|---|---|
| 0 Ingestion | `v4/contracts.py`, `v4/ingest.py`, explicit map adapter, bounded CSV/JSON/XML, quarantine and SHA-256 | Provider-specific source mapping & dataset licences need verified actual columns; no automatic SIH schema assumptions |
| 1A Bitcoin UTXO | outpoint keys, fee/satoshi checks, unresolved lineage masks, Bitcoin Core tx adapter | Real chain reorg handling and complex scripts require verified fixtures |
| 1B Wire | timestamped observed TXIDs/sensor dedup, separate host/ASN/country context | No genuine authorized P2P sensor evidence available; never infer origin/wallet owner |
| 2 Graph | six typed nodes, allowlisted typed edges, as-of timestamps, PyG heterodata | Large-data tuning and historical entity versions not benchmarked |
| 3 Representation | causal tabular features, degree baseline, optional SAGE/GAT training and hetero forward | Untrained hetero forward != validated trained GNN; temporal fold recomputation required |
| 4 MCER | cautious common-input candidates, hard CoinJoin/service exclusions, tentative grouping | H2–H5 evidence calibration and longitudinal merge/split error require independent truth |
| 5 Motifs | peel-like, equal-output CoinJoin-like, fan-in/out candidate witnesses | Proper wallet/service hard negatives and precision evaluation remain |
| 6 Models | sklearn logistic/RF/IsolationForest, chrono OOF stack, optional PyG challenger | Independent real labels, proper model registry, calibrated probabilities, full temporal GNN training not validated |
| 7 Δ | heldout CCA and global permutation gate, ABSTAIN fallback | Independent pairing, validated background/null, Δ2–Δ5 local components not established |
| 8 Π | five unit-bearing component ratios for independently verified same-goal baseline, ABSTAIN fallback | Real controlled economic objective / counterfactual unavailable |
| 9 Fusion | explicit bounded local priority and final 0–100 score | Weights are illustrative, *not learned/calibrated* without cohort labels |
| 10 MLRP | frozen pass-one, directional spend links, max six hops, 25-point final cap, no IP/Country financial taint | Service boundaries must be externally documented, propagation sensitivity benchmarking needed |
| 11 UI/API/report | React orange/white dashboard, read-only loopback API, JSON/PDF export | Frontend build/API integration, authentication for shared/multiuser deployments and visual PDF QA unverified |
| 12 Evaluation | heldout metrics, grouped bootstrap, ablations and leakage audit | No independently validated real-world results or full negative-control matrix |

## Implementation readiness flags

- `WRITTEN_STATIC`: New v4 library, training/evaluation, storage, UI and documentation files were written.
- `UNVERIFIED`: No Python tests, TypeScript checks, npm installs, model fit or build were executed **in this pass**.
- `DATA_BLOCKED`: Δ, Π, real provider mapping, production model calibration and wallet attribution cannot be invented.
- `INTEGRATION_BLOCKED`: Later end-to-end acceptance and real datasets still require manual validation.
- `UNMODIFIED_BLUEPRINTS`: Many older `src/clarion/**` planned stubs remain for compatibility/organizational reasons; the functioning new implementation lives in `src/clarion/v4/` and `frontend/`. Don't mistake those stubs for implemented features.

## Static code entrypoints

- Canonical import: `clarion.v4.ingest.import_canonical`
- Full local evidence run: `python scripts/v4_pipeline.py analyze --data ... --out ... --licence ... --origin ...`
- Time-safe training: `python scripts/v4_pipeline.py train --data ... --out ... --licence ... --origin ...`
- Offline UI API: `clarion serve --run <run-dir>` (already existing loopback CLI)
- React frontend: `cd frontend && npm install && npm run build`
- Optional torch+PyG: CPU baseline first, matching wheel builds for single GPU later.
- Optional ReportLab PDF: `clarion.v4.reporting.case_pdf_from_json`.

**Research integrity:** no uploaded IP can establish the controlling wallet; no country
gets guilt/risk points. A novel behavioral motif or high novelty rank is not
an illicit finding. CI/demo success would still not prove deployment accuracy.
