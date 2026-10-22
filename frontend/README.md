# CLARION Investigator Console — orange/white offline UI

An **actual React 18 + Vite + TypeScript frontend** replacing the previous
placeholder scaffold. Restrained terracotta (#C96743) / ivory (#FAF9F6) theme
inspired by the requested minimalist orange-and-white palette; original CLARION
layout, copy and controls.

## Development

```bash
cd frontend
npm install
npm run typecheck
npm run dev
```

Run `clarion serve --run artifacts/demo_run --port 8000` separately. Vite
proxies `/api` to this loopback service. Production bundle: `npm run build`
then serve `frontend/dist` from the loopback API service (no CDN dependencies).

## Live read-only routes
- `GET /api/manifest`
- `GET /api/leads?limit=1000`
- `GET /api/graph`
- `GET /api/motifs`
- `GET /api/propagation`

The UI derives overview, search, filters, inspector dossiers, graph neighborhoods,
motif lists, Δ/Π abstention panels, and propagation summaries from real run files.
It **never** fabricates missing entities, cross-layer eligibility, model metrics,
or labels. Case JSON export includes source hash references and is explicitly a
reviewable lead, not a claim of guilt.

No analytics, telemetry, font CDN or outbound API; assets are locally bundled.
This source has deliberately NOT been run or built in this authoring pass per request.
