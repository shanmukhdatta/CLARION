# CLARION synthetic demo — DevOps runbook

**Intended audience:** student maintainers and SIH reviewers. This is a deliberately local demonstration, **not a multi-user secured public forensic service**. The source data in this flow are fictional and the model is an unsupervised review priority, not a criminality classifier.

## Container workflow

On a trusted machine with Docker and an internet connection *for the initial image build*:

```bash
docker compose build
docker compose up -d
docker compose ps
docker compose logs --tail=100 clarion-demo
```

Open **http://127.0.0.1:8000** on the same machine. The first start generates 10 synthetic spending episodes, runs the real v4 pipeline, validates score caps/source-contracts, then starts the local FastAPI server with the prebuilt blue/white React interface. A named Docker volume retains the generated **fictional** artifacts between restarts. Container runs with unprivileged UID, read-only root filesystem, dropped Linux capabilities and host-loopback-only port mapping.

The container uses `uvicorn 0.0.0.0` **inside Docker only**; it is limited by Compose mapping to host 127.0.0.1. **Never change this to a public port binding without designing real authentication, threat model, reverse proxy controls and privacy protections.** This is not equivalent to a proven air-gapped build, nor is it a hardened public service.

Verify HTTP and evidence:

```bash
curl --fail http://127.0.0.1:8000/api/health
curl --fail http://127.0.0.1:8000/api/models/readiness
curl --fail http://127.0.0.1:8000/api/provenance/verify
```

`/api/models/readiness` returns **MODEL_NOT_CONFIGURED** by default, because no trained/validated real-world model ships with CLARION. No fake pickle/H5 file is loaded to simulate accuracy. Δ and Π abstain on the fictional demo. Any legal/licensed data stays outside this sample image.

## CI/CD division

- **Continuous integration:** existing `CLARION CI`, `security checks`, `CLARION v4 validation`, `CLARION submission acceptance`. They verify Python, Ruff, sample integration, React build, source constraints and folder READMEs. Review **actual workflow conclusions**.
- **GitHub Pages:** `.github/workflows/showcase-pages.yml` publishes *docs only* when the repository's Pages source is configured to **GitHub Actions**. It never deploys Python, APIs, private data, model weights or credentials.
- **Container deployment:** remains manual/localhost-only. Container registry and public-cloud auto deployment are intentionally **not** configured because there is no validated real source/security policy.

## Environment and optional models

`CLARION_RUN_DIR` points to an existing completed analysis run. For controlled development, set `CLARION_MODEL_ARTIFACT` to a locally trained and SHA-verified `CLARION_LOGISTIC_JSON_V1` file **outside source control**. The UI shows readiness from the local API. The optional model inference endpoint refuses missing and future-incompatible feature rows; it does **not** modify final case scores. An API key, external MLflow server, LangGraph, and cloud account are not required for the local demo.

Use `scripts/train/record_mlflow.py` to log *aggregate synthetic metrics* locally. Install `requirements-mlops.txt` only in a separate development environment when MLflow itself is needed. GraphSAGE experiments require matching PyTorch/PyG installed manually; they are not inside the minimal container.

## Rollback, monitoring, provenance

1. Preserve input/manifest hashes and backup any separate SQLite reviewer-state database **together** with its run evidence before upgrades.
2. Check `/api/health` and `/api/provenance/verify`; a green liveness endpoint alone does not establish source integrity.
3. To stop the local service, run `docker compose down`. Do not run `down -v` unless you intentionally want to erase the demo volume.
4. For rollback, build from a known reviewed commit and recreate the container while retaining the named volume. If schema/run manifests change, use a fresh volume rather than mixing incompatible runs.

## Still blocked

Independent Bitcoin Core/reorg acceptance, true permissioned P2P sensor TXIDs, real temporal label quality, validated MCER/Δ/Π, calibrated real-world detection quality, signed offline wheelhouse/image, real-world threat testing and public multi-user controls. Follow [feature audit](../IMPLEMENTATION_CHECKLIST.md) and [submission architecture](../submission-architecture.md); never promote these to complete simply because a Dockerfile exists.
