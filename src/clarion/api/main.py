"""Read-only offline investigation dashboard. Only bind to loopback."""
from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

HOME = """<!doctype html><html lang=en><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>
<title>CLARION | Local Investigator</title><style>
body{margin:0;background:#090f1c;color:#e9f3ff;font:15px system-ui}header{padding:24px 4vw;background:#111b30;border-bottom:1px solid #28405d}
h1{margin:0;font-size:30px;letter-spacing:.1em}small{color:#8eabc8}main{padding:26px 4vw;max-width:1320px;margin:auto}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}.panel{background:#14213a;border:1px solid #2e4765;border-radius:12px;padding:20px}
.metric{font-size:26px;font-weight:700;color:#80e2df}.danger{color:#ffbfae}table{border-collapse:collapse;width:100%}th,td{padding:10px;border-bottom:1px solid #354560;text-align:left}
tr:hover{background:#203251;cursor:pointer}button{border:0;border-radius:8px;background:#64d0cf;color:#061424;padding:8px 14px;cursor:pointer}
pre{white-space:pre-wrap;word-wrap:break-word;color:#c3dafa}input{background:#0f1c2e;color:white;padding:9px;border:1px solid #406080;border-radius:6px}
@media(max-width:760px){.grid{grid-template-columns:1fr}} </style>
<header><h1>CLARION <small>v4 · forensic workbench</small></h1><small>Offline demo • Fictional transactions • Leads are not accusations</small></header>
<main><div class=grid><section class=panel><h2>Evidence readiness</h2><div id=status>Loading...</div></section>
<section class=panel><h2>Investigation summary</h2><div id=metrics></div></section></div>
<section class=panel style='margin-top:20px'><h2>Prioritized transaction leads</h2><input id=filter placeholder='Filter by TXID / case / priority' style='width:60%'><table><thead><tr><th>TXID</th><th>Priority</th><th>Points</th><th>Exposure</th></tr></thead><tbody id=rows></tbody></table></section>
<section class=panel style='margin-top:20px'><h2>Evidence dossier</h2><pre id=dossier>Select a transaction above.</pre></section></main>
<script>
const $=x=>document.getElementById(x);let leads=[];
async function get(url){let r=await fetch(url);if(!r.ok)throw new Error(await r.text());return r.json()}
function cell(tr,s){let td=document.createElement('td');td.textContent=String(s);tr.appendChild(td)}
function draw(){let f=$('filter').value.toLowerCase();$('rows').replaceChildren();
for(let x of leads.filter(x=>(x.txid+x.case_id+x.priority).toLowerCase().includes(f)).slice(0,150)){
let tr=document.createElement('tr');cell(tr,x.txid.slice(0,14)+'…');cell(tr,x.priority);cell(tr,x.risk_points);cell(tr,x.propagation_points);
tr.onclick=()=>{$('dossier').textContent=JSON.stringify(x,null,2)};$('rows').appendChild(tr)}}
async function main(){try{let m=await get('/api/manifest');leads=await get('/api/leads?limit=1000');
$('status').textContent=JSON.stringify(m.readiness,null,2);$('metrics').textContent=String(m.n_leads)+' leads · '+String(m.n_chain_edges)+' UTXO edges · '+String(m.n_motifs)+' motifs';draw()}
catch(e){$('status').textContent='Unable to load local artifacts: '+e.message}}$('filter').addEventListener('input',draw);main();
</script></html>"""


def create_app(run_dir: Path) -> FastAPI:
    app = FastAPI(title="CLARION local demo", docs_url=None, redoc_url=None)
    root = run_dir.resolve()

    def read(name: str):
        target = root / name
        if not target.is_file():
            raise HTTPException(404, detail="run this project's investigate command first")
        return json.loads(target.read_text(encoding="utf-8"))

    @app.get("/", response_class=HTMLResponse)
    def home():
        return HTMLResponse(HOME, headers={"Content-Security-Policy": "default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'"})

    @app.get("/api/manifest")
    def manifest():
        return read("run_manifest.json")

    @app.get("/api/leads")
    def leads(limit: int = Query(100, ge=1, le=1000), offset: int = Query(0, ge=0)):
        return read("leads.json")[offset: offset + limit]

    @app.get("/api/graph")
    def graph():
        return read("graph.json")

    @app.get("/api/motifs")
    def get_motifs():
        return read("motifs.json")

    @app.get("/api/propagation")
    def propagation():
        return read("propagation.json")

    return app
