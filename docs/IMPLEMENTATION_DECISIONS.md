# CLARION implementation decisions

These decisions reconcile old v4 blueprint claims with source-code evidence and the uploaded master prompt. Changes that invalidate the original architecture must be proposed explicitly and tested.

| Decision | Reason | Adopted implementation | Remaining validation |
|---|---|---|---|
| D-01 Offline first | Original SIH constraints prohibit online dependence at inference | Local source files, FastAPI loopback, React bundle, no online dataset requests | OS egress and signed release test |
| D-02 Bitcoin UTXO primary | Address-directed transfers can fabricate true money flow | Directed exact (TXID,vout) spends and integer satoshis | Real script/coinbase/reorg fixtures |
| D-03 Evidence before identity | P2P relay doesn't imply wallet owner | Host→observed relay→Transaction only; country contextual | Independent sensor test |
| D-04 Truth and features separated | Synthetic/case labels cannot leak into inference | Labels for opt-in time-safe model fitting, separate source/time field | Real label availability analysis |
| D-05 Conservative MCER | Single common input/change is uncertain, particularly CoinJoin/service traffic | Signed H1/H2 evidence, independently supported tentative partition, H3–H5 callable research proposals | Calibrated independence/conflicts, false merge truth |
| D-06 Δ/Π abstention | Data cannot support fabricated residual/economic intent | Global CCA gate and per-component economic ratios only with verified premises | Case-specific Δ1–Δ5 and verified same-goal Π |
| D-07 Non-circular fusion | Model stack cannot consume propagated risk that seeds itself | Freeze 0–75 local points, one pass on spend graph, ≤25 extra points | Five-level context study |
| D-08 Review annotations separated | Human status changes must not mutate case evidence | SQLite review store scoped by run SHA, optimistic revisions and hash-linked events | External trusted signed audit |
| D-09 Local write protection | Single-machine UI default has no identity provider | Only POST token writes; no default secret or Internet bind; unconfigured = disabled | Genuine multi-user RBAC would need separate design |
| D-10 No unsafe model unpickling | Untrusted pickle can execute arbitrary code | Logistic model inference uses versioned JSON coefficients, training cutoff and SHA-256 | Signature/registration and GNN safe formats |
| D-11 CI truthfulness | Previous synthetic checks do not prove full original architecture | Separate Python v4 tests, Ruff, frontend build, canonical smoke, documentation inventory | Real benchmark protocols and full E2E |
| D-12 Preserve user decisions and README | Existing 100+ detailed folder guides must not be discarded | New implementation modules and docs coexist with historical blueprints, explicit status matrix | Rewrite legacy stubs only with working replacements |

**Nondecision:** No real-world criminality accuracy percentage, legal identity, or calibrated probability is claimed. The original original 13-block v4 architecture is a target; current code only covers parts of it. See [172 requirement rows](IMPLEMENTATION_CHECKLIST.md).
