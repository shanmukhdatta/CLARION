import type { GraphData, Lead, Motif, Propagation, RunManifest, WorkspaceData } from "./types";

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
  const [manifest, leads, graph, motifs, propagation] = await Promise.all([
    request<RunManifest>("/manifest"),
    request<Lead[]>("/leads?limit=1000"),
    request<GraphData>("/graph"),
    request<Motif[]>("/motifs"),
    request<Propagation>("/propagation"),
  ]);
  return { manifest, leads, graph, motifs, propagation };
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
