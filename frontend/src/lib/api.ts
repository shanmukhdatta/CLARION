import type { CaseHistory, CaseRecord, EntityCandidate, GraphData, Lead, Motif, Propagation, ReviewRecord, ReviewStatus, RunManifest, WorkspaceData } from "./types";

const TIMEOUT_MS = 12000;
const BASE = "/api";

async function request<T>(path: string): Promise<T> {
  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    const response = await fetch(BASE + path, {
      signal: controller.signal,
      credentials: "same-origin",
      headers: { Accept: "application/json" },
      cache: "no-store",
    });
    if (!response.ok) throw new Error(`${response.status} ${response.statusText} on ${path}`);
    return await response.json() as T;
  } finally {
    window.clearTimeout(timer);
  }
}

export async function loadWorkspace(): Promise<WorkspaceData> {
  const [manifest, leads, graph, motifs, propagation, entities] = await Promise.all([
    request<RunManifest>("/manifest"),
    request<Lead[]>("/leads?limit=1000"),
    request<GraphData>("/graph"),
    request<Motif[]>("/motifs"),
    request<Propagation>("/propagation"),
    request<EntityCandidate[]>("/entities?limit=1000").catch(() => []),
  ]);
  return { manifest, leads, graph, motifs, propagation, entities };
}

export async function getCase(txid: string): Promise<CaseRecord> {
  if (!/^[a-f0-9]{64}$/.test(txid)) throw new Error("Invalid transaction ID");
  return request<CaseRecord>(`/cases/${txid}`);
}

export async function getCaseHistory(txid: string): Promise<CaseHistory[]> {
  if (!/^[a-f0-9]{64}$/.test(txid)) throw new Error("Invalid transaction ID");
  return request<CaseHistory[]>(`/cases/${txid}/history`);
}

export async function saveCaseReview(
  txid: string,
  change: { status: ReviewStatus; note: string; expected_revision: number; request_id: string },
  token: string,
): Promise<ReviewRecord> {
  if (!/^[a-f0-9]{64}$/.test(txid)) throw new Error("Invalid transaction ID");
  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    const response = await fetch(`${BASE}/cases/${txid}/review`, {
      method: "POST", credentials: "same-origin", signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-CLARION-REVIEW-TOKEN": token,
      },
      body: JSON.stringify(change),
      cache: "no-store",
    });
    if (!response.ok) {
      let reason = "";
      try { reason = (await response.json() as { detail?: string }).detail ?? ""; }
      catch { /* Server error may not be JSON. */ }
      throw new Error(`Review update failed (${response.status})${reason ? ": " + reason : ""}`);
    }
    return await response.json() as ReviewRecord;
  } finally { window.clearTimeout(timer); }
}

export async function exportCaseAsJson(lead: Lead, manifest: RunManifest): Promise<void> {
  const report = {
    kind: "CLARION_INVESTIGATIVE_LEAD",
    warning: "Lead only. Not a declaration of wrongdoing, identity or ownership.",
    evidence_cutoff: manifest.cutoff ?? null,
    source_hashes: manifest.data_source_hashes ?? {},
    lead,
  };
  const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  try {
    const link = document.createElement("a");
    link.href = url;
    link.download = `clarion-case-${lead.txid.slice(0, 12)}.json`;
    link.click();
  } finally {
    URL.revokeObjectURL(url);
  }
}

/** Model operations are read-only. No model weights or private evidence are uploaded. */
export interface ModelReadiness {
  status: string;
  detail: string;
}

export async function getModelReadiness(): Promise<ModelReadiness> {
  return request<ModelReadiness>("/models/readiness");
}

export async function getExperimentalPrediction(txid: string): Promise<{
  status: string;
  score_type: string;
  prediction: { score: number; subject_id: string };
  warning: string;
}> {
  if (!/^[a-f0-9]{64}$/.test(txid)) throw new Error("Invalid transaction ID");
  return request(`/models/experimental/${txid}`);
}

export interface DemoTrainingExperiment {
  training_status: string;
  model_status: string;
  model_families: string[];
  meta_model: string;
  training_protocol: string;
  metrics_synthetic_only: Record<string, number>;
  important: string;
  mlops_tracking?: string;
}

export async function getSyntheticTrainingExperiment(): Promise<DemoTrainingExperiment | null> {
  try { return await request<DemoTrainingExperiment>("/experiments/demo"); }
  catch { return null; } // Files are optional; a missing report must never be fabricated.
}
