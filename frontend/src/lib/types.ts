/** Read-only API contracts for both the initial CLARION demo and future v4 runs. */
export type Priority = "P1" | "P2" | "P3" | "P4";
export interface Readiness {
  analysis_mode?: string;
  mode?: string;
  reason?: string;
  reasons?: string[];
  cross_layer_dependence_verified?: boolean;
  wire_observation_count?: number;
  exact_txid_joined_observations?: number;
}
export interface RunManifest {
  status: string;
  kind: string;
  n_chain_edges: number;
  n_leads: number;
  n_motifs: number;
  n_wire_observations?: number;
  readiness: Readiness;
  cutoff?: string | null;
  data_source_hashes?: Record<string, string>;
  training_score_type?: string;
  unvalidated_real_world_performance?: boolean;
}
export interface Lead {
  txid: string;
  case_id?: string;
  time?: string;
  priority: Priority;
  risk_points: number;
  local_seed_points?: number;
  propagation_points: number;
  witness_path?: string[];
  delta?: { status: string; reason?: string };
  pi?: { status: string; reason?: string };
  explanation?: { model_ranking?: number; local_score?: number; rules?: Record<string, number> };
}
export interface GraphNode { id: string; type: string; label?: string }
export interface GraphEdge {
  source: string;
  target: string;
  type?: string;
  relation?: string;
  amount_sats?: number;
  evidence_id?: string;
  evidence_ref?: string;
  time?: string;
}
export interface GraphData { nodes: GraphNode[]; edges: GraphEdge[]; cutoff?: string }
export interface Motif {
  id?: string;
  kind: string;
  subject?: string;
  subject_id?: string;
  witness_txids?: string[];
  benign_alternative?: string;
  evidence_refs?: string[];
}
export interface Propagation {
  max_hops: number;
  capacity_points?: number;
  seed_count?: number;
  points?: Record<string, number>;
  propagation_prior?: Record<string, number>;
  witness_paths?: Record<string, string[]>;
  top_paths?: Record<string, string[]>;
  frozen_seed_hash?: string;
}
export interface WorkspaceData {
  manifest: RunManifest;
  leads: Lead[];
  graph: GraphData;
  motifs: Motif[];
  propagation: Propagation;
}
