import { useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import {
  Activity, ArrowDownRight, ArrowRight, BarChart3, BookOpenText, CheckCircle2,
  ChevronDown, CircleAlert, CircleHelp, Clock3, Copy, Download, FileSearch,
  FileText, Fingerprint, GitBranch, Layers3, LayoutDashboard, ListFilter,
  LockKeyhole, Network, RefreshCw, Search, Settings2, ShieldCheck,
  ShieldQuestion, SlidersHorizontal, Sparkles, Waypoints, X,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { exportCaseAsJson, loadWorkspace } from "../lib/api";
import CasesPage from "../features/cases/CasesPage";
import type { GraphData, GraphEdge, Lead, Motif, Priority, WorkspaceData } from "../lib/types";

type Page =
  | "overview" | "leads" | "graph" | "patterns" | "entities"
  | "signals" | "propagation" | "models" | "cases" | "audit" | "settings";

const NAV: Array<{ page: Page; label: string; icon: LucideIcon; group: string }> = [
  { page: "overview", label: "Overview", icon: LayoutDashboard, group: "Workspace" },
  { page: "leads", label: "Investigation leads", icon: FileSearch, group: "Workspace" },
  { page: "graph", label: "Evidence graph", icon: Network, group: "Workspace" },
  { page: "patterns", label: "Pattern library", icon: Layers3, group: "Intelligence" },
  { page: "entities", label: "Entity hypotheses", icon: Fingerprint, group: "Intelligence" },
  { page: "signals", label: "Δ & Π signals", icon: Activity, group: "Intelligence" },
  { page: "propagation", label: "Risk propagation", icon: Waypoints, group: "Intelligence" },
  { page: "models", label: "Models & evaluation", icon: BarChart3, group: "Operations" },
  { page: "cases", label: "Case dossiers", icon: BookOpenText, group: "Operations" },
  { page: "audit", label: "Provenance audit", icon: ShieldCheck, group: "Operations" },
  { page: "settings", label: "Run settings", icon: Settings2, group: "Operations" },
];

const fmt = (value: number) => new Intl.NumberFormat("en-US").format(value);
const short = (str: string, n = 12) => str.length > n ? `${str.slice(0, n)}…` : str;
const readable = (text: string) => text.replaceAll("_", " ").replaceAll("-", " ");
const simpleTime = (date?: string | null) => date ? new Date(date).toLocaleString() : "Latest snapshot";
const PRIORITIES: Priority[] = ["P1", "P2", "P3", "P4"];

function Tag({ children, kind }: { children: ReactNode; kind: string }) {
  return <span className={`badge ${kind.toLowerCase()}`}>{children}</span>;
}

function PageHeader({ eyebrow, title, subtitle, action }: {
  eyebrow: string; title: string; subtitle: string; action?: ReactNode;
}) {
  return (
    <div className="page-head">
      <div><div className="eyebrow">{eyebrow}</div><h1>{title}</h1><p>{subtitle}</p></div>
      {action}
    </div>
  );
}

function Info({ name, value }: { name: string; value: ReactNode }) {
  return <div className="info-pair"><span>{name}</span><strong>{value}</strong></div>;
}

function Empty({ title, message }: { title: string; message: string }) {
  return <div className="empty"><ShieldQuestion size={30} strokeWidth={1.5}/><h3>{title}</h3><p>{message}</p></div>;
}

function Caution({ text }: { text: string }) {
  return (
    <div className="notice"><CircleAlert size={19} style={{flexShrink:0, marginTop:1}}/>
      <div><strong>Research-grade evidence only</strong>{text}</div>
    </div>
  );
}

function Stat({ label, value, hint, icon: Icon }: {
  label: string; value: string | number; hint: string; icon: LucideIcon;
}) {
  return (
    <div className="card stat">
      <div className="title">{label}<span className="icon-box"><Icon size={16}/></span></div>
      <div className="value">{value}</div><div className="foot">{hint}</div>
    </div>
  );
}

function LeadsTable({ leads, onSelect, compact = false }: {
  leads: Lead[]; onSelect: (lead: Lead) => void; compact?: boolean;
}) {
  return (
    <div style={{overflowX:"auto"}}>
      <table className="data-table" aria-label="Investigation leads">
        <thead><tr><th>TRANSACTION</th>{!compact && <th>CASE</th>}
          <th>PRIORITY</th><th>RISK POINTS</th><th>EXPOSURE</th>
          {!compact && <th>EVENT TIME</th>}</tr></thead>
        <tbody>
        {leads.map(lead => (
          <tr key={lead.txid} tabIndex={0}
            onClick={() => onSelect(lead)}
            onKeyDown={e => { if (e.key === "Enter") onSelect(lead); }}>
            <td className="mono" title={lead.txid}>{short(lead.txid, compact ? 9 : 16)}</td>
            {!compact && <td className="mono">{lead.case_id ?? "—"}</td>}
            <td><Tag kind={lead.priority}>{lead.priority}</Tag></td>
            <td><strong>{lead.risk_points.toFixed(1)}</strong><span style={{color:"var(--muted)"}}> / 100</span></td>
            <td style={{color:"var(--orange)"}}>+{lead.propagation_points.toFixed(1)}</td>
            {!compact && <td style={{color:"var(--muted)"}}>{simpleTime(lead.time)}</td>}
          </tr>
        ))}
        </tbody>
      </table>
    </div>
  );
}

function RiskBars({ leads }: { leads: Lead[] }) {
  const values = PRIORITIES.map(p => ({name:p, amount:leads.filter(l=>l.priority===p).length}));
  const max = Math.max(1, ...values.map(x=>x.amount));
  return (
    <div>
      {values.map(entry=>(
        <div className="risk-line" key={entry.name}>
          <Tag kind={entry.name}>{entry.name}</Tag>
          <div className="bar-rail"><div className="bar-fill" style={{width:`${entry.amount / max * 100}%`}}/></div>
          <span className="pct">{entry.amount}</span>
        </div>
      ))}
      <div style={{color:"var(--muted)",fontSize:11,lineHeight:1.7,marginTop:21}}>
        P1–P4 are analyst review priorities, not estimated probabilities of criminality.
      </div>
    </div>
  );
}

function MiniGraph({ graph, focus, onSelect }: {
  graph: GraphData; focus?: string; onSelect: (id:string)=>void;
}) {
  const shown = useMemo(() => {
    const edges = graph.edges.filter(e => (
      e.relation === "spends_outpoint" || e.type === "spends-outpoint" ||
      e.type === "spends_outpoint"
    ));
    const focused = focus ? edges.filter(e=>e.source.endsWith(focus) || e.target.endsWith(focus) ||
      e.source === focus || e.target === focus) : [];
    const selected = (focused.length ? focused : edges).slice(0, 30);
    const ids = Array.from(new Set(selected.flatMap(e=>[e.source,e.target]))).slice(0,26);
    return {
      edges:selected.filter(e=>ids.includes(e.source) && ids.includes(e.target)),
      ids,
    };
  }, [graph, focus]);
  if (!shown.ids.length) return <Empty title="No verified graph edges" message="Import the source data and construct an as-of UTXO graph first."/>;
  const coord = new Map(shown.ids.map((id,index)=>{
    const step=index / Math.max(1, shown.ids.length);
    const x=70 + 650*step;
    const y=170 + 75*Math.sin(step * Math.PI * 4);
    return [id,{x,y}] as const;
  }));
  return (
    <div>
      <svg className="graph-svg" viewBox="0 0 790 350" aria-label="Verified UTXO graph preview" role="img">
        <defs><marker id="arrowhead" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto">
          <path d="M0,0 L7,3.5 L0,7" fill="#9EB9DE"/></marker></defs>
        {shown.edges.map((e,index)=>{
          const a=coord.get(e.source), b=coord.get(e.target);
          if (!a || !b) return null;
          return <line key={index} x1={a.x} y1={a.y} x2={b.x} y2={b.y}
            stroke="#9EB9DE" strokeWidth="1.7" markerEnd="url(#arrowhead)"/>;
        })}
        {shown.ids.map((id,index)=>{
          const c=coord.get(id)!;
          const highlight=id===focus || id.endsWith(focus ?? "___");
          return <g key={id} onClick={()=>onSelect(id.replace(/^tx:/,""))}
            style={{cursor:"pointer"}} tabIndex={0} role="button" aria-label={`Inspect ${id}`}>
            <circle cx={c.x} cy={c.y} r={highlight?17:12}
              fill={highlight?"#2563EB":index%3===0?"#C6DBFE":"#EAF2FF"}
              stroke={highlight?"#1D4ED8":"#89B5F4"} strokeWidth="1.5"/>
            <text x={c.x} y={c.y+31} textAnchor="middle"
              fontSize="9" fontFamily="monospace" fill="#6C87AA">{id.slice(0,7)}</text>
          </g>;
        })}
      </svg>
      <p style={{fontSize:11,color:"var(--muted)",lineHeight:1.6,marginTop:12}}>
        Limited to {shown.ids.length} visible nodes. Arrows show recorded output spending, not wallet-owner identity.
      </p>
    </div>
  );
}

function Drawer({ lead, onClose, onExport }: {
  lead: Lead | null; onClose: ()=>void; onExport: (l:Lead)=>void;
}) {
  if (!lead) return null;
  return (
    <div onClick={onClose} style={{position:"fixed",inset:0,background:"rgba(42,33,27,.34)",zIndex:20,display:"flex",justifyContent:"flex-end"}}>
      <section onClick={e=>e.stopPropagation()} role="dialog" aria-modal="true" aria-label="Investigation dossier"
        style={{background:"white",height:"100%",width:"min(490px,100%)",padding:28,overflowY:"auto",boxShadow:"-8px 0 45px #3e281a25"}}>
        <div style={{display:"flex",justifyContent:"space-between",alignItems:"center"}}>
          <span className="eyebrow">Transaction dossier</span>
          <button className="secondary-btn" onClick={onClose} aria-label="Close dossier"><X size={17}/></button>
        </div>
        <h2 style={{fontSize:23,letterSpacing:"-.03em",marginBottom:12}}>Evidence overview</h2>
        <p className="mono-small">{lead.txid}</p>
        <div style={{margin:"20px 0 12px"}}><Tag kind={lead.priority}>{lead.priority} — Review priority</Tag></div>
        <Info name="Total priority points" value={`${lead.risk_points.toFixed(2)} / 100`}/>
        <Info name="Frozen first-pass seed" value={lead.local_seed_points?.toFixed(2) ?? "Unavailable"}/>
        <Info name="Propagation exposure" value={`+${lead.propagation_points.toFixed(2)}`}/>
        <Info name="Cross-layer Δ" value={<Tag kind="warn">{lead.delta?.status ?? "ABSTAIN"}</Tag>}/>
        <Info name="Economic Π" value={<Tag kind="warn">{lead.pi?.status ?? "ABSTAIN"}</Tag>}/>
        <Info name="TXID source case" value={lead.case_id ?? "Not provided"}/>
        <Info name="Event time" value={simpleTime(lead.time)}/>
        <h3 style={{fontSize:14,margin:"27px 0 10px"}}>Recorded witness path</h3>
        {(lead.witness_path ?? []).length ? (
          <div className="detail">{(lead.witness_path ?? []).map((id,i)=><p key={id} style={{margin:0}}>{i+1}. {id}</p>)}</div>
        ) : <p style={{fontSize:12,color:"var(--muted)"}}>No witness path available.</p>}
        <h3 style={{fontSize:14,margin:"27px 0 10px"}}>Machine-generated evidence breakdown</h3>
        <div className="detail">{JSON.stringify(lead.explanation ?? {},null,2)}</div>
        <p style={{fontSize:11,lineHeight:1.7,color:"var(--muted)",margin:"18px 0"}}>
          A lead is neither a finding of wrongdoing nor attribution of any address to a person.
          Relay observations do not establish wallet ownership.
        </p>
        <button className="primary-btn" onClick={()=>onExport(lead)}><Download size={15}/> Export reviewable JSON</button>
      </section>
    </div>
  );
}

function Overview({ data, onSelect, navigate }: {
  data: WorkspaceData; onSelect: (l:Lead)=>void; navigate: (page:Page)=>void;
}) {
  const {manifest,leads,motifs}=data;
  return <>
    <PageHeader eyebrow="Intelligence workspace" title="Investigation overview"
      subtitle="A clear view of evidence readiness, candidate signals, and prioritized Bitcoin transactions."
      action={<button className="primary-btn" onClick={()=>navigate("leads")}>Explore leads <ArrowRight size={16}/></button>}/>
    <Caution text="Demonstration outputs and model scores are unvalidated for real-world criminality. All IP sightings are observational, never wallet ownership."/>
    <div className="stats-grid">
      <Stat label="Investigation leads" value={fmt(manifest.n_leads ?? leads.length)}
        hint="Candidate transactions to review" icon={FileSearch}/>
      <Stat label="Verified chain edges" value={fmt(manifest.n_chain_edges ?? data.graph.edges.length)}
        hint="Outpoint-backed transfers" icon={GitBranch}/>
      <Stat label="Behavior patterns" value={fmt(manifest.n_motifs ?? motifs.length)}
        hint="With source-linked witnesses" icon={Layers3}/>
      <Stat label="Wire observations" value={fmt(manifest.n_wire_observations ?? 0)}
        hint="Relay context; not origin proof" icon={Network}/>
    </div>
    <div className="columns">
      <section className="card">
        <div className="card-heading"><h2>Top priority leads</h2>
          <button className="secondary-btn" onClick={()=>navigate("leads")}>View all <ArrowRight size={14}/></button></div>
        <LeadsTable leads={[...leads].sort((a,b)=>b.risk_points-a.risk_points).slice(0,7)} compact onSelect={onSelect}/>
      </section>
      <section className="card">
        <div className="card-heading"><h2>Priority distribution</h2><span className="meta">Current run</span></div>
        <RiskBars leads={leads}/>
        <div style={{borderTop:"1px solid var(--border)",marginTop:25,paddingTop:18}}>
          <div style={{display:"flex",alignItems:"center",gap:9,fontSize:13,fontWeight:650,marginBottom:9}}>
            <ShieldCheck size={17} color="var(--green)"/> Evidence mode
          </div>
          <p style={{fontSize:12,color:"var(--muted)",lineHeight:1.7}}>
            {manifest.readiness?.analysis_mode ?? manifest.readiness?.mode ?? "Unknown"}
            {" · "}{manifest.readiness?.reason ?? manifest.readiness?.reasons?.[0] ?? "No further readiness detail"}
          </p>
        </div>
      </section>
    </div>
    <div className="card" style={{marginTop:19}}>
      <div className="card-heading"><h2>Evidence neighborhood</h2>
        <button className="secondary-btn" onClick={()=>navigate("graph")}>Open graph <ArrowRight size={14}/></button></div>
      <MiniGraph graph={data.graph} onSelect={(id)=>{const lead=leads.find(x=>x.txid===id);if(lead) onSelect(lead);}}/>
    </div>
  </>;
}

function Leads({ data, onSelect }: {data:WorkspaceData;onSelect:(l:Lead)=>void}) {
  const [filter,setFilter]=useState("");
  const [priority,setPriority]=useState("ALL");
  const [sort,setSort]=useState("risk");
  const selection = useMemo(()=>{
    const text=filter.trim().toLowerCase();
    const rows=data.leads.filter(x=>(priority==="ALL" || x.priority===priority)
      && (!text || [x.txid,x.case_id ?? "",x.priority].some(s=>s.toLowerCase().includes(text))));
    rows.sort(sort==="time"?(a,b)=>(b.time??"").localeCompare(a.time??"")
      : (a,b)=>b.risk_points-a.risk_points);
    return rows.slice(0,1000);
  },[data.leads,filter,priority,sort]);
  return <>
    <PageHeader eyebrow="Evidence triage" title="Investigation leads"
      subtitle="Filter, review and export evidence-linked transaction leads without assuming criminal intent."/>
    <div className="card">
      <div className="filters">
        <label className="input-wrap"><Search size={16} color="var(--muted)"/><input aria-label="Search transactions"
          value={filter} onChange={e=>setFilter(e.target.value)} placeholder="Search TXID or case…"/></label>
        <select aria-label="Filter priority" value={priority} onChange={e=>setPriority(e.target.value)}>
          <option value="ALL">All priorities</option>{PRIORITIES.map(p=><option key={p}>{p}</option>)}
        </select>
        <select aria-label="Sort leads" value={sort} onChange={e=>setSort(e.target.value)}>
          <option value="risk">Highest priority first</option><option value="time">Most recent first</option>
        </select>
        <span style={{fontSize:11,color:"var(--muted)",marginLeft:"auto"}}>{selection.length} results</span>
      </div>
      {selection.length ? <LeadsTable leads={selection} onSelect={onSelect}/> :
        <Empty title="No matching leads" message="Try another priority or search phrase."/>}
    </div>
  </>;
}

function GraphPage({ data, onSelect }: { data:WorkspaceData;onSelect:(lead:Lead)=>void }) {
  const [focus,setFocus]=useState("");
  const [chosen,setChosen]=useState<string|null>(null);
  const neigh=data.graph.edges.filter(e=>!!chosen && (e.source===chosen || e.target===chosen ||
      e.source.endsWith(chosen) || e.target.endsWith(chosen))).slice(0,25);
  return <>
    <PageHeader eyebrow="Forensic link analysis" title="Evidence graph"
      subtitle="Browse bounded transaction-spending paths and inspect recorded source evidence."/>
    <Caution text="Only exact UTXO spends form monetary flow. A host relaying a TXID cannot be treated as the transaction creator."/>
    <div className="columns">
      <section className="card">
        <div className="card-heading"><h2>As-of graph snapshot</h2><span className="meta">{data.graph.edges.length} recorded edges</span></div>
        <div className="filters"><label className="input-wrap"><Search size={15}/>
          <input value={focus} onChange={e=>setFocus(e.target.value)} placeholder="Focus TXID…"/></label></div>
        <MiniGraph graph={data.graph} focus={focus || undefined} onSelect={id=>{
          setChosen(id);const lead=data.leads.find(x=>x.txid===id);if(lead) onSelect(lead);
        }}/>
      </section>
      <section className="card">
        <div className="card-heading"><h2>Source-linked edges</h2><span className="meta">Selected neighborhood</span></div>
        {!chosen ? <Empty title="Select a node" message="Click a graph node to inspect matching links and their recorded evidence."/> :
          <><p className="mono-small">{chosen}</p>{neigh.map((e,i)=><div className="motif-row" key={i}>
            <strong>{readable(e.relation ?? e.type ?? "spend")}</strong>
            <p className="mono-small">{short(e.source,17)} → {short(e.target,17)}</p>
            <p className="mono-small">{e.evidence_ref ?? e.evidence_id ?? "Reference not exported"}</p>
          </div>)}</>}
      </section>
    </div>
  </>;
}

function Patterns({ data, onSelect }: {data:WorkspaceData;onSelect:(lead:Lead)=>void}) {
  const [filter,setFilter]=useState("ALL");
  const kinds=Array.from(new Set(data.motifs.map(x=>x.kind)));
  const listed=data.motifs.filter(m=>filter==="ALL"||m.kind===filter);
  return <>
    <PageHeader eyebrow="Structural behavior" title="Pattern library"
      subtitle="Motif candidates carry witness TXIDs, uncertainty, and legitimate alternative explanations."/>
    <div className="card"><div className="filters">
      <select value={filter} onChange={e=>setFilter(e.target.value)} aria-label="Pattern type">
        <option value="ALL">All patterns</option>{kinds.map(k=><option value={k} key={k}>{readable(k)}</option>)}
      </select><span style={{fontSize:12,color:"var(--muted)"}}>{listed.length} matching motifs</span></div>
      {listed.length===0 ? <Empty title="No patterns recorded" message="Run pattern extraction on an approved as-of graph."/>:
        listed.slice(0,150).map((motif,i)=><div className="motif-row" key={motif.id ?? i}>
          <div style={{display:"flex",justifyContent:"space-between",gap:15}}>
            <strong>{readable(motif.kind)}</strong><Tag kind="warn">Hypothesis</Tag></div>
          <p className="mono-small">{motif.subject ?? motif.subject_id ?? "Unknown subject"}</p>
          <p>Benign alternative: {motif.benign_alternative ?? "Not documented"}</p>
          <button className="secondary-btn" style={{marginTop:12}} onClick={()=>{
            const id=motif.subject ?? motif.subject_id;
            const match=data.leads.find(l=>l.txid===id);
            if(match) onSelect(match);
          }}>Inspect related lead <ArrowRight size={13}/></button>
        </div>)}
    </div>
  </>;
}

function Signals({ data }: {data:WorkspaceData}) {
  const example=data.leads.find(x=>x.delta || x.pi);
  return <>
    <PageHeader eyebrow="Research signal eligibility" title="Δ & Π signals"
      subtitle="Cross-view residual consistency and verified-goal expenditure are optional, independently gated research signals."/>
    <Caution text="Synthetic relay observations do not establish chain/wire dependence or wallet-to-IP ownership; missing evidence must result in ABSTAIN."/>
    <div className="columns">
      <section className="card">
        <div className="card-heading"><h2>Δ — Cross-layer divergence</h2><Tag kind="warn">{example?.delta?.status??"ABSTAIN"}</Tag></div>
        <p style={{fontSize:12,lineHeight:1.8,color:"var(--muted)"}}>
          Requires genuinely paired independent observations, chronology, sensor coverage,
          clock-accuracy audit and a held-out dependence null test.
        </p>
        <Info name="Current gate" value={example?.delta?.status??"ABSTAIN"}/>
        <Info name="Reason" value={example?.delta?.reason??"No validated paired-view estimate"}/>
      </section>
      <section className="card">
        <div className="card-heading"><h2>Π — Economic expenditure</h2><Tag kind="warn">{example?.pi?.status??"ABSTAIN"}</Tag></div>
        <p style={{fontSize:12,lineHeight:1.8,color:"var(--muted)"}}>
          Requires an independently verified economic objective and a controlled same-goal
          baseline before fee, hop, time, fragmentation or infrastructure comparisons.
        </p>
        <Info name="Current gate" value={example?.pi?.status??"ABSTAIN"}/>
        <Info name="Reason" value={example?.pi?.reason??"Controlled economic goal absent"}/>
      </section>
    </div>
  </>;
}

function PropagationPage({data}:{data:WorkspaceData}){
  const sorted=Object.entries(data.propagation.points??data.propagation.propagation_prior??{})
    .sort((a,b)=>b[1]-a[1]).slice(0,25);
  return <>
    <PageHeader eyebrow="Bounded financial exposure" title="Risk propagation"
      subtitle="Frozen first-pass seeds flow across verified directed outpoints, with separate contextual observations."/>
    <div className="stats-grid">
      <Stat label="Propagation cap" value="25" hint="Maximum additional points" icon={ShieldCheck}/>
      <Stat label="Maximum hops" value={data.propagation.max_hops??"—"} hint="Causal, bounded path length" icon={Waypoints}/>
      <Stat label="Seed transactions" value={data.propagation.seed_count??"—"} hint="Immutable pass-one risk vector" icon={GitBranch}/>
      <Stat label="Exposed leads" value={fmt(sorted.length)} hint="Top recorded exposure values" icon={Activity}/>
    </div>
    <div className="card"><div className="card-heading"><h2>Highest verified exposure</h2>
      <Tag kind="warn">Not an accusation</Tag></div>
      {sorted.length===0?<Empty title="No propagation output" message="A frozen seed and time-ordered UTXO paths are required."/>:
        sorted.map(([id,points])=><div className="risk-line" key={id}
          style={{gridTemplateColumns:"150px 1fr 60px"}}>
          <span className="mono" title={id}>{short(id,13)}</span>
          <div className="bar-rail"><div className="bar-fill" style={{width:`${Math.max(0,Math.min(100,points/25*100))}%`}}/></div>
          <span className="pct">{points.toFixed(2)}</span>
        </div>)}
    </div>
  </>;
}

function StatusPage({data,kind,onSelect}:{data:WorkspaceData;kind:Page;onSelect:(lead:Lead)=>void}){
  const {manifest}=data;
  if(kind==="entities") return <>
    <PageHeader eyebrow="Uncertain graph hypotheses" title="Entity hypotheses"
      subtitle="Conservative common-input proposals; never identities inferred from host metadata."/>
    <div className="card">
      {!data.entities.length ? <Empty title="No entity memberships proposed"
        message="MCER needs independent multi-input witnesses and service/CoinJoin exclusions; single-input episodes do not justify merges."/>:
        data.entities.map((e,i)=><div className="motif-row" key={e.entity_id??i}>
          <div style={{display:"flex",justifyContent:"space-between"}}>
            <strong className="mono-small">{e.entity_id??`Hypothesis ${i+1}`}</strong>
            <Tag kind="warn">{e.status??"Tentative"}</Tag></div>
          <p>{e.members.length} candidate addresses; not confirmed co-ownership</p>
          <p className="mono-small">{e.members.slice(0,6).join(" · ")}</p>
          <p>Witnesses: {(e.support??[]).slice(0,4).join(", ") || "No verified source references exported"}</p>
        </div>)}
    </div>
  </>;
  if(kind==="models") return <>
    <PageHeader eyebrow="Scientific evaluation" title="Models & evaluation"
      subtitle="Out-of-fold, chronological modeling with explicit synthetic-only status."/>
    <Caution text="No independently validated real-world precision, AUROC, calibration or external holdout has been established."/>
    <div className="card">
      <Info name="Score type" value={manifest.training_score_type ?? "Unknown/unvalidated"}/>
      <Info name="Real-world validation" value="Not established"/>
      <Info name="External benchmark" value="Not supplied"/>
      <Info name="Predictor warning" value="Scores ≠ illicit probability"/>
    </div>
  </>;
  if(kind==="audit") return <>
    <PageHeader eyebrow="Evidence integrity" title="Provenance audit"
      subtitle="Source digests anchor the local run. Check bytes against these identifiers before review."/>
    <div className="card">
      {Object.entries(manifest.data_source_hashes??{}).map(([name,hash])=>
        <div className="info-pair" key={name}><span>{name}</span><strong className="mono-small">{hash}</strong></div>)}
      {!Object.keys(manifest.data_source_hashes??{}).length&&
        <Empty title="No source hashes available" message="Import files with provenance manifests and SHA-256 digests."/>}
      <Info name="Run mode" value={manifest.status}/>
      <Info name="Event cutoff" value={simpleTime(manifest.cutoff)}/>
    </div>
  </>;
  if(kind==="settings") return <>
    <PageHeader eyebrow="Local configuration" title="Run settings"
      subtitle="Review the active analysis mode, privacy boundaries, and pipeline eligibility."/>
    <div className="card">
      <Info name="Mode" value={manifest.readiness.analysis_mode??manifest.readiness.mode??"Not reported"}/>
      <Info name="Runtime" value="Local, offline analysis"/>
      <Info name="Read-only UI" value="Enabled"/>
      <Info name="TXID-origin inference" value="Prohibited"/>
      <Info name="Country-level criminal risk" value="Prohibited"/>
      <Info name="Real-world validation" value="Not established"/>
      <div className="notice" style={{marginTop:25}}>Run configuration is edited in version-controlled YAML,
        not through browser controls. No remote telemetry or public backend is required.</div>
    </div>
  </>;
  return <>
    <PageHeader eyebrow="Reviewable investigative evidence" title="Case dossiers"
      subtitle="Select a lead and export an evidence-linked JSON snapshot. A dossier is not proof of guilt."/>
    <div className="card">
      {data.leads.length ? <LeadsTable leads={data.leads.slice(0,25)} onSelect={onSelect}/> :
        <Empty title="No case leads" message="No investigation run has emitted a candidate transaction lead."/>}
    </div>
  </>;
}

export default function App(){
  const [data,setData]=useState<WorkspaceData|null>(null);
  const [error,setError]=useState<string|null>(null);
  const [loading,setLoading]=useState(true);
  const [page,setPage]=useState<Page>("overview");
  const [selected,setSelected]=useState<Lead|null>(null);

  const refresh=()=>{
    setLoading(true);setError(null);
    loadWorkspace().then(setData).catch((e:unknown)=>setError(e instanceof Error?e.message:String(e))).finally(()=>setLoading(false));
  };
  useEffect(()=>{refresh();},[]);
  const chosen=NAV.find(n=>n.page===page)!;
  const render=()=>{
    if(!data) return null;
    if(page==="overview") return <Overview data={data} navigate={setPage} onSelect={setSelected}/>;
    if(page==="leads") return <Leads data={data} onSelect={setSelected}/>;
    if(page==="graph") return <GraphPage data={data} onSelect={setSelected}/>;
    if(page==="patterns") return <Patterns data={data} onSelect={setSelected}/>;
    if(page==="signals") return <Signals data={data}/>;
    if(page==="propagation") return <PropagationPage data={data}/>;
    if(page==="cases") return <CasesPage leads={data.leads} onOpenDossier={setSelected}/>;
    return <StatusPage data={data} kind={page} onSelect={setSelected}/>;
  };
  const sections=["Workspace","Intelligence","Operations"];
  return <>
    <div className="app">
      <aside className="sidebar">
        <div className="logo"><span className="logo-mark"><GitBranch size={20}/></span>
          <div>CLARION<small>INVESTIGATOR</small></div></div>
        {sections.map(section=><div key={section}>
          <div className="navgroup">{section}</div>
          {NAV.filter(n=>n.group===section).map(({page:p,label,icon:Icon})=>
            <button key={p} className={`navbutton ${page===p?"active":""}`}
              onClick={()=>setPage(p)} aria-current={page===p?"page":undefined}>
              <Icon/><span>{label}</span>{p==="leads" && !!data && <span className="count">{data.leads.length}</span>}
            </button>)}
        </div>)}
        <div className="sidebar-footer"><strong><span className="dot"/> Local research mode</strong>
          <span>Evidence-based leads · Not guilt labels</span></div>
      </aside>
      <main className="workspace">
        <header className="topbar">
          <div className="breadcrumb">CLARION <span> / </span> <strong>{chosen.label}</strong></div>
          <div className="topactions">
            <span className="status-pill"><span className="dot"/> Offline ready</span>
            <button className="secondary-btn" onClick={refresh} aria-label="Reload run" title="Refresh run files">
              <RefreshCw size={14}/></button>
            <span className="avatar">C4</span>
          </div>
        </header>
        <nav className="mobile-nav" aria-label="Workspace navigation">
          {NAV.map(n=><button className={page===n.page?"active":""} key={n.page} onClick={()=>setPage(n.page)}>{n.label}</button>)}
        </nav>
        <div className="content">
          {loading && !data && <div className="card"><div className="empty"><RefreshCw size={28}/><h3>Loading local evidence</h3><p>Reading the selected run snapshot…</p></div></div>}
          {error && <div className="card"><Empty title="Cannot read local run"
            message={`${error}. Start the CLARION backend on 127.0.0.1:8000 after producing run artifacts.`}/>
            <button className="primary-btn" onClick={refresh}>Retry connection <RefreshCw size={15}/></button></div>}
          {!loading || data ? render() : null}
        </div>
      </main>
    </div>
    <Drawer lead={selected} onClose={()=>setSelected(null)}
      onExport={lead=>{if(data) void exportCaseAsJson(lead,data.manifest);}}/>
  </>;
}
