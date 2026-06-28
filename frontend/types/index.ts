export type User = {
  id: string;
  email: string;
  full_name: string;
  role: "Super Admin" | "Admin" | "Analyst" | "Viewer";
};

export type Workspace = {
  id: string;
  name: string;
  slug: string;
  owner_id: string;
  created_at: string;
};

export type Connection = {
  id: string;
  workspace_id: string;
  name: string;
  kind: "postgresql" | "mysql" | "sqlite" | "mongodb";
  masked_uri: string;
  is_read_only: boolean;
  selected_assets: string[];
};

export type QueryResult = {
  log_id: string;
  question: string;
  engine: string;
  generated_query: string | Record<string, unknown>[];
  explanation: string;
  safe: boolean;
  rows: Record<string, string | number | null>[];
  columns: string[];
  insights: {
    summary: string;
    trends: string[];
    anomalies: string[];
    recommendations: string[];
    highlight?: Record<string, unknown>;
  };
  chart: { type: string; x?: string; y?: string; columns?: string[] };
  follow_up_questions: string[];
  agent_trace?: AgentTraceItem[];
  final_confidence?: number;
  query_confidence?: {
    confidence_score?: number;
    reasoning_summary?: string;
    risk_level?: string;
    suggested_corrections?: string[];
  };
};

export type AgentTraceItem = {
  agent: string;
  latency_ms: number;
  tokens: { prompt: number; completion: number };
  success: boolean;
  error?: string | null;
};

export type AgentWorkflowTrace = {
  id: string;
  workspace_id?: string;
  user_id?: string;
  question?: string;
  intent?: string;
  engine?: string;
  agent_trace: AgentTraceItem[];
  execution_order: string[];
  token_usage: { prompt?: number; completion?: number };
  errors: string[];
  retries: number;
  success: boolean;
  final_confidence: number;
  agent_outputs?: {
    data_quality?: { quality_score?: number; issues?: unknown[]; affected_tables?: string[]; recommendations?: string[] };
    anomaly_detection?: { severity?: string; anomalies?: unknown[]; affected_metrics?: string[]; recommended_next_agent?: string };
    etl?: { source_type?: string; import_status?: string; rows_processed?: number; validation_errors?: string[]; cleaning_summary?: Record<string, unknown> };
    cost_governance?: { estimated_ai_cost?: number; query_cost_score?: number; workspace_usage_status?: string; warnings?: string[] };
    semantic_layer?: { metric_count?: number; matched_metrics?: unknown[] };
    data_lineage?: { affected_dashboards?: string[]; affected_reports?: string[]; affected_kpis?: string[] };
    collaboration?: { human_in_the_loop?: boolean; approval_required_before?: string[] };
    scheduling?: { cadence?: string; scheduled_reports?: boolean; delivery_channels?: string[] };
    monitoring?: { agent_status?: string; latency_ms?: number; success_rate?: number; prometheus_ready?: boolean };
    model_route?: { selected_model?: string; mode?: string; fallback?: string };
    workflow_plan?: { fallback_path?: string; agents_to_run?: string[]; retry_plan?: Record<string, unknown> };
    governance?: { decision?: string; retention_policy?: string; forbidden_datasets?: string[]; approval_requirements?: Record<string, boolean> };
    supervisor_plan?: { parallel_groups?: string[][]; retry_policy?: string; conflict_resolution?: string };
  };
  created_at?: string;
};
