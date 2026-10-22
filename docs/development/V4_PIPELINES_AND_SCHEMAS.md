# CLARION v4: exact static data pipeline, schemas and dependencies

## 1. Approved input

Use authorized local evidence, record copyright/data licence, origin, collection
method and SHA256. Do not scrape or import private traffic without authorization.
Canonical tables: UTF-8 CSV, JSON record array, or bounded DTD-free XML under
a single local directory. Schema models in `src/clarion/v4/contracts.py` reject
unknown fields and missing required properties.

### `transactions.csv`
`txid` (64 lowercase hex), `event_time` (ISO8601 timezone-aware),
`available_at` (ISO8601 UTC-parseable), `coinbase` (0/1), `vbytes` (optional
positive int), `fee_sats` (optional nonnegative int), `confirmation`
(mempool/confirmed/orphaned/unknown), `block_height` (optional).

Legacy demo accepts `time` instead of event_time, and discards fictional
`case_id` from evidence features.

### `inputs.csv`
`txid`, `vin` (nonnegative int), `prev_txid` (hex), `prev_vout` (int).
No owner or source IP column; inputs spend exact preceding outputs.

### `outputs.csv`
`txid`, `vout`, `value_sats` (exact integer), `address` (optional
descriptive script address), `script_type` (optional). Unknown scripts are
unknown rather than invented human/wallet identities. `BTC × 10^8` uses
`Decimal` with sub-satoshi rejection.

### `observations.csv`
`observation_id`, `sensor_id`, `host`, `event_time`, `available_at`,
`txid` (optional, only if actually decoded from observed relay),
`decode_provenance` (observed_inv/observed_tx/none),
`clock_uncertainty_ms`, `direction` (optional), `asn` and
`country` (optional validated enrichment). **Observed relays are not
origin or wallet ownership.** Duplicate sensor/host/txid/time observations
are collapsed for the graph.

### `labels.csv` (training ONLY)
`subject_id`, `subject_type`, `value` 0/1, `available_at`, `definition`.
`source_id` is generated from the import manifest. A case label is not
automatically an address label. The demo's `truth_SYNTHETIC_ONLY.csv`
is deliberately excluded from inference.

## 2. Full pipeline

```text
Source rights / SHA256
  -> bounded parser -> quarantine per invalid record
  -> canonical Tx/Input/Output/WireObservation/Label contracts
  -> as-of cutoff using available_at, exact outpoints + conservation
  -> readiness (chain-only vs conditional cross-layer eligibility)
  -> typed six-node graph + source-edge witnesses
  -> nullable causal feature rows
  -> conservative MCER ledger/candidates + structural motif witnesses
  -> unsupervised novelty rank (NO guilt probability)
  -> Δ/Π standalone gates: ABSTAIN without independent premises
  -> pass 1 provisional score, hash/freeze seeds
  -> time-directed, value-normalized propagation (<=6 hops, <=25 pts)
  -> pass 2 final capped priority (not a calibrated crime probability)
  -> immutable JSON/CSV/optional Parquet + provenance manifest
  -> React offline local investigator + PDF/JSON case review
  -> heldout scientific evaluation / ablations / false-merge audit
```

## 3. Run layout

```text
artifacts/v4_run/
  run_manifest.json      # source hashes, cutoff, run mode, limitations
  graph.json             # provenance-carrying typed evidence
  features.json          # nullable causal columns
  motifs.json            # source-witnessed candidates and benign alternatives
  entities.json          # uncertain H1 candidate groups, not verified owners
  leads.json             # priority points, NOT probability
  leads.csv              # formula-injection protected spreadsheet preview
  propagation.json       # frozen hash, risk path, capped exposure
  quarantine.json        # malformed/invalid source row errors
```

## 4. Library versions and minimum computing environment

Base Python: 3.11 / 3.12; Pydantic 2, PyYAML. Extra dependencies:
`numpy`, `scikit-learn`, `scipy`, `pyarrow`, `duckdb`,
`defusedxml`, `fastapi`, `uvicorn`. See `requirements-v4.txt`.
Optional report `reportlab`; optional PyG: `torch` and
`torch-geometric` matching each other and hardware before installation.

Frontend: React 18, TypeScript 5.7, Vite 6, lucide-react locally bundled.
No CDN/hosted font/network runtime dependency. API on loopback only.
Do NOT assume dataset columns for Elliptic++/BitcoinHeist imply UTXO.
Feature-only benchmarks require a documented external adapter and a separate
task-appropriate evaluation dataset.

## 5. Follow-up verification (requested to be delayed)

1. Install locked packages and run Ruff, mypy, pytest, `npm run typecheck`.
2. Re-run the small fictional source fixture and assert every outpoint/value.
3. Run negative controls: missing prevout, double spend, future availability,
   duplicate sensor, CoinJoin service batching, unknown goal, no paired Δ.
4. Add source-specific SIH/Core mappings from *actual* approved data.
5. Validate future holdout by independent cases and source; report FPR/cohort
   controls and bootstrap confidence intervals.
6. Run limited service-only desktop build; audit browser CSP, PDF layout, login
   if extending beyond a single user, offline dependency wheelhouse.
