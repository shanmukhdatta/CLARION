# CLARION PR Quality Bot

The GitHub Actions PR Quality Gate automatically checks every new or updated PR targeting main, and pushes to main. It installs the locked Python environment on 3.11 and 3.12, checks Ruff lint/format, mypy, pytest (including offline test guard), and builds a wheel.

## Merge policy
Configure a main branch ruleset requiring pull requests, independent review, resolution of conversations, and successful checks for both Python versions and PR review policy. Prevent direct pushes and bypasses. GitHub Actions cannot establish independent human approval on its own. Do not automatically merge PRs based on a green CI run.

## Limitations
This workflow does not certify deployed offline network isolation, data/label provenance, ML performance, security, or production readiness. Those need independent validation and evidence. The test-time network monkeypatch is not a system firewall. Run additional release security and offline integration tests before production claims.

## Follow-up
Pin third-party GitHub Actions to audited immutable commit SHAs after initial validation; confirm uv lock works on both supported Python versions; add CodeQL, SBOM/dependency audits, API/frontend checks, and real Linux air-gap smoke tests as those components become executable.
