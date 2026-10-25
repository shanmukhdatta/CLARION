# Optional localhost-only demo image. Build needs network; runtime reads only local assets.
FROM node:22-bookworm-slim AS frontend-build
WORKDIR /build/frontend
COPY frontend/package*.json ./
RUN npm install --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 CLARION_RUN_DIR=/workspace/artifacts/submission_demo/investigation
WORKDIR /workspace
COPY pyproject.toml README.md requirements-v4.txt requirements-demo.txt ./
COPY src ./src
COPY scripts ./scripts
COPY --from=frontend-build /build/frontend/dist ./frontend/dist
RUN python -m pip install --no-cache-dir -e . -r requirements-v4.txt -r requirements-demo.txt \
 && useradd --create-home --uid 10001 clarion \
 && mkdir -p /workspace/artifacts \
 && chown -R clarion:clarion /workspace/artifacts
USER clarion
EXPOSE 8000
CMD ["sh", "scripts/release/container_entrypoint.sh"]
