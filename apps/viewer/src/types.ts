export interface ComparisonRunSummary {
  id: string;
  session_id: string;
  ok: boolean;
  verdict: string;
  reference_action_count: number;
  evidence_action_count: number;
  completeness_claim: string;
  created_at: string;
}

export interface HopFinding {
  kind: string;
  reference_index?: number | null;
  evidence_index?: number | null;
  tool_name?: string | null;
  detail: string;
}

export interface TraceAction {
  index: number;
  tool_name: string;
  action_id?: string | null;
  arguments_digest?: string | null;
}

export interface ComparisonRunDetail extends ComparisonRunSummary {
  reference: { actions: TraceAction[] };
  evidence: { actions: TraceAction[]; completeness_claim?: string };
  report: { findings?: HopFinding[]; note?: string };
}

export interface HealthResponse {
  ok: boolean;
  service: string;
  store: string;
  version: string;
}
