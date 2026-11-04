# CLARION v4 — Git, Branch and Pull Request Workflow

## Branch policy
- Fetch latest main and record its SHA before starting.
- Implement on phase/task branches, not directly on main.
- Suggested branches: implementation/p0-repository-audit, implementation/p1-mini24-fixture, implementation/p2-chain-wire, implementation/p3-temporal-graph, implementation/p4-mcer-motifs, implementation/p5-model-baselines, implementation/p6-delta-pi-fusion, implementation/p7-mlrp, implementation/p8-investigator-ui, implementation/p9-validation-release.
- Use a short topic suffix for multiple PRs in one phase.

## Task workflow
1. Fetch main; inspect worktree and record SHA.
2. Read owner module, tests, folder README and master-plan section.
3. Record task/REQ IDs, expected behavior, inputs/outputs, dependencies and tests in the phase ledger.
4. Implement the smallest complete slice; add positive, negative and boundary tests.
5. Run targeted, integration and regression checks.
6. Update requirement status only when evidence supports it.
7. Regenerate folder READMEs in write mode, then check mode.
8. Record SHA, commands, environment, exit codes, logs, artifact hashes and blockers.
9. Push branch and open a reviewable PR. Do not merge around required CI/review checks.

## Commit policy
Use one coherent task per commit. Examples: chore(p0): record repository baseline; feat(p1): add deterministic mini24 fixture; feat(p2): validate chain and wire contracts; feat(p3): add temporal graph snapshots; feat(p4): add MCER lineage; feat(p5): add chronological OOF stack; feat(p6): gate Delta and Pi; feat(p7): enforce bounded propagation; feat(p8): connect UI to run artifacts; test(p9): add offline acceptance.

## PR checklist
Include phase/task and REQ IDs, canonical owner, changed files/interfaces, data rights and subject semantics, dependencies/licenses, exact tests/results, artifact hashes, security/privacy impact, limitations, blockers, next handoff and rollback plan.

## Non-negotiable rules
Never force-push, overwrite collaborator work, delete/weaken failing tests, disable CI, bypass reviews, claim unrun tests passed, or commit credentials, private captures, confidential SIH data, unlicensed bulk datasets or unapproved model binaries. A merged PR is not automatically VERIFIED; P9 offline acceptance is required for release.
