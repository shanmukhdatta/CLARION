import { useCallback, useEffect, useMemo, useState } from "react";
import { AlertCircle, CheckCircle2, FileClock, LockKeyhole, RefreshCcw, Save, Search, ShieldCheck } from "lucide-react";
import { getCase, getCaseHistory, saveCaseReview } from "../../lib/api";
import type { CaseHistory, CaseRecord, Lead, ReviewStatus } from "../../lib/types";

interface Props {
  leads: Lead[];
  onOpenDossier: (lead: Lead) => void;
}

const ALLOWED: Record<ReviewStatus, ReviewStatus[]> = {
  NEW: ["IN_REVIEW"],
  IN_REVIEW: ["DISMISSED", "ESCALATED"],
  DISMISSED: ["IN_REVIEW"],
  ESCALATED: ["IN_REVIEW"],
};

export default function CasesPage({ leads, onOpenDossier }: Props) {
  const [search, setSearch] = useState("");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [caseRecord, setCaseRecord] = useState<CaseRecord | null>(null);
  const [events, setEvents] = useState<CaseHistory[]>([]);
  const [nextStatus, setNextStatus] = useState<ReviewStatus>("IN_REVIEW");
  const [note, setNote] = useState("");
  const [token, setToken] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const matching = useMemo(() => leads.filter(x => !search ||
    x.txid.toLowerCase().includes(search.toLowerCase()) ||
    (x.case_id || "").toLowerCase().includes(search.toLowerCase())).slice(0, 150), [leads, search]);

  const loadSelected = useCallback(async (txid: string) => {
    setBusy(true);
    setError("");
    setMessage("");
    try {
      const [item, history] = await Promise.all([getCase(txid), getCaseHistory(txid)]);
      setCaseRecord(item);
      setEvents(history);
      setNextStatus(ALLOWED[item.review.status][0] ?? "IN_REVIEW");
      setNote("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to read this review");
      setCaseRecord(null);
      setEvents([]);
    } finally { setBusy(false); }
  }, []);

  useEffect(() => {
    if (selectedId) void loadSelected(selectedId);
  }, [selectedId, loadSelected]);

  const save = async () => {
    if (!caseRecord || !selectedId || busy) return;
    if (!ALLOWED[caseRecord.review.status].includes(nextStatus)) {
      setError("The selected status transition is not permitted.");
      return;
    }
    if (!note.trim() || !token.trim()) {
      setError("Enter a review rationale and your locally configured reviewer token.");
      return;
    }
    setBusy(true);
    setError("");
    setMessage("");
    try {
      const revised = await saveCaseReview(selectedId, {
        status: nextStatus, note: note.trim(),
        expected_revision: caseRecord.review.revision,
        request_id: crypto.randomUUID(),
      }, token.trim());
      setCaseRecord({ ...caseRecord, review: revised });
      setEvents(await getCaseHistory(selectedId));
      setNextStatus(ALLOWED[revised.status][0] ?? "IN_REVIEW");
      setNote("");
      setToken("");
      setMessage("Review saved to local SQLite with an auditable revision.");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Review save failed");
      if (selectedId) await loadSelected(selectedId);
    } finally { setBusy(false); }
  };

  return <div>
    <div className="page-head">
      <div>
        <div className="eyebrow">Human evidence review</div>
        <h1>Case workbench</h1>
        <p>Track review decisions separately from immutable blockchain evidence. Escalation is not an accusation.</p>
      </div>
    </div>
    <div className="notice"><ShieldCheck size={18} style={{ flexShrink: 0 }} />
      <div><strong>Local, evidence-linked reviews</strong>
        Review writes are disabled until CLARION_REVIEW_TOKEN is configured on your machine. Tokens are never saved by this page.</div>
    </div>
    <div className="columns">
      <section className="card">
        <div className="card-heading"><h2>Select an investigation lead</h2><span className="meta">{matching.length} visible</span></div>
        <label className="input-wrap" style={{ marginBottom: 15 }}>
          <Search size={15} color="var(--muted)" />
          <input placeholder="Search transaction or case ID" aria-label="Search cases" value={search}
            onChange={e => setSearch(e.target.value)} />
        </label>
        <div style={{ maxHeight: 470, overflowY: "auto" }}>
          {matching.map(lead => <button key={lead.txid}
            className={`navbutton ${selectedId === lead.txid ? "active" : ""}`}
            style={{ alignItems: "flex-start", display: "flex" }}
            onClick={() => setSelectedId(lead.txid)}>
            <FileClock size={16} style={{ flexShrink: 0 }} />
            <span style={{ minWidth: 0, flex: 1 }}>
              <span className="mono" style={{ display: "block", wordBreak: "break-all" }}>{lead.txid.slice(0, 24)}…</span>
              <span style={{ display: "block", color: "var(--muted)", fontSize: 11, marginTop: 5 }}>
                {lead.priority} · {lead.risk_points.toFixed(1)} review points
              </span>
            </span>
          </button>)}
          {!matching.length && <p style={{ color: "var(--muted)", fontSize: 12 }}>No leads match this search.</p>}
        </div>
      </section>
      <section className="card" aria-live="polite">
        <div className="card-heading">
          <h2>Persistent review</h2>
          {selectedId && <button className="secondary-btn" onClick={() => void loadSelected(selectedId)}
            disabled={busy}><RefreshCcw size={14} /> Reload</button>}
        </div>
        {!selectedId && <div className="empty"><LockKeyhole size={26} />
          <h3>Select a transaction</h3><p>Choose a lead to inspect review status, edit a decision, and see its audit history.</p></div>}
        {selectedId && !caseRecord && !busy && <p style={{ color: "var(--muted)", fontSize: 12 }}>
          The requested review is unavailable. See the error below.</p>}
        {busy && !caseRecord && <p style={{ color: "var(--muted)", fontSize: 12 }}>Loading local review…</p>}
        {caseRecord && <div>
          <p className="mono-small">{caseRecord.review.txid}</p>
          <div className="info-pair"><span>Status</span><strong>{caseRecord.review.status.replaceAll("_", " ")}</strong></div>
          <div className="info-pair"><span>Revision</span><strong>{caseRecord.review.revision}</strong></div>
          <div className="info-pair"><span>Reviewer</span><strong>{caseRecord.review.reviewer || "Not yet reviewed"}</strong></div>
          <button className="secondary-btn" style={{ margin: "15px 0" }} onClick={() => onOpenDossier(caseRecord.lead)}>
            Inspect immutable lead evidence
          </button>
          <div style={{ borderTop: "1px solid var(--border)", paddingTop: 16, marginTop: 3 }}>
            <label style={{ display: "block", fontSize: 12, fontWeight: 650, marginBottom: 8 }} htmlFor="review-state">
              Change review status</label>
            <select id="review-state" value={nextStatus} onChange={e => setNextStatus(e.target.value as ReviewStatus)}
              style={{ width: "100%", border: "1px solid var(--border)", padding: 11, borderRadius: 8, background: "#fff" }}>
              {ALLOWED[caseRecord.review.status].map(value => <option key={value} value={value}>
                {value.replaceAll("_", " ")}
              </option>)}
            </select>
            <label style={{ display: "block", fontSize: 12, fontWeight: 650, margin: "18px 0 8px" }}
              htmlFor="review-note">Evidence-based decision rationale</label>
            <textarea id="review-note" rows={3} maxLength={4000}
              placeholder="Explain the source evidence and legitimate alternatives..."
              value={note} onChange={e => setNote(e.target.value)}
              style={{ width: "100%", padding: 12, resize: "vertical", border: "1px solid var(--border)", borderRadius: 8 }} />
            <label style={{ display: "block", fontSize: 12, fontWeight: 650, margin: "15px 0 8px" }}
              htmlFor="review-token">Local reviewer token</label>
            <input id="review-token" type="password" autoComplete="off" value={token}
              placeholder="From your CLARION_REVIEW_TOKEN setting" onChange={e => setToken(e.target.value)}
              style={{ width: "100%", padding: 12, border: "1px solid var(--border)", borderRadius: 8 }} />
            <button className="primary-btn" disabled={busy || !note.trim() || !token.trim()}
              style={{ marginTop: 14 }} onClick={() => void save()}>
              <Save size={15} /> Save review
            </button>
          </div>
          <h3 style={{ fontSize: 14, margin: "25px 0 12px" }}>Audit history</h3>
          {events.length ? events.map(event => <div className="motif-row" key={event.seq}>
            <strong>{event.previous_status} → {event.next_status}</strong>
            <p>{event.note}</p>
            <p className="mono-small">{event.timestamp} · rev {event.revision}</p>
          </div>) : <p style={{ fontSize: 12, color: "var(--muted)" }}>No review events yet.</p>}
        </div>}
        {message && <p role="status" style={{ color: "var(--green)", fontSize: 12, display: "flex", gap: 8 }}>
          <CheckCircle2 size={16} /> {message}</p>}
        {error && <p role="alert" style={{ color: "var(--red)", fontSize: 12, display: "flex", gap: 8 }}>
          <AlertCircle size={16} /> {error}</p>}
      </section>
    </div>
  </div>;
}
