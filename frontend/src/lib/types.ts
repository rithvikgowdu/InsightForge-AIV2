export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string | null;
  is_active: boolean;
  created_at: string;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
  user: User;
}

export interface SupportingEvidence {
  issue_number?: number;
  title?: string;
  url?: string;
  snippet?: string;
  comments_count?: number;
}

export interface ProductOpportunity {
  id: string;
  analysis_id: string;
  cluster_id?: string | null;
  title: string;
  problem_statement: string;
  business_opportunity: string;
  proposed_solution: string;
  target_customer_segment: string;
  suggested_mvp_features: string[];
  market_potential: string;
  confidence_score: number;
  confidence_explanation: string;
  supporting_evidence: SupportingEvidence[];
  supporting_doc_count: number;
  is_fallback: boolean;
  created_at: string;
}

export interface AnalysisCluster {
  id: string;
  analysis_id: string;
  cluster_label: number;
  title: string;
  summary: string;
  size: number;
  recurring_themes?: string[] | null;
  sample_issue_ids?: (number | string)[] | null;
}

export interface CollectedIssue {
  id: string;
  source_id: string;
  issue_number: number;
  title: string;
  body?: string | null;
  clean_text?: string | null;
  url: string;
  state: string;
  author?: string | null;
  labels?: string[] | null;
  comments_count: number;
  source_created_at?: string | null;
}

export type AnalysisStatus = "QUEUED" | "RUNNING" | "COMPLETED" | "FAILED";

export interface AnalysisRun {
  id: string;
  repo_owner: string;
  repo_name: string;
  repo_url: string;
  status: AnalysisStatus;
  current_step: string;
  progress_pct: number;
  total_issues_requested: number;
  total_issues_collected: number;
  total_clusters: number;
  total_opportunities: number;
  error_message?: string | null;
  is_fallback: boolean;
  created_at: string;
  completed_at?: string | null;
}

export interface AnalysisDetail extends AnalysisRun {
  clusters: AnalysisCluster[];
  opportunities: ProductOpportunity[];
  sample_issues: CollectedIssue[];
}

export interface AnalysisStatusResponse {
  id: string;
  status: AnalysisStatus;
  current_step: string;
  progress_pct: number;
  total_issues_requested: number;
  total_issues_collected: number;
  total_clusters: number;
  total_opportunities: number;
  error_message?: string | null;
  is_fallback: boolean;
  created_at: string;
  completed_at?: string | null;
}

