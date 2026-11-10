export interface DashboardSummary {
  total_skus: number;
  total_locations: number;
  total_suppliers: number;
  total_forecast_demand: number;
  total_shortages: number;
  critical_shortages: number;
  total_shortage_exposure: number;
  supplier_capacity_utilization_pct: number;
  inventory_coverage_weeks: number;
  mitigation_success_rate_pct: number;
  exceptions_detected: number;
}

export interface DashboardCharts {
  shortages_by_severity: Record<string, number>;
  shortages_by_root_cause: Record<string, number>;
  weekly_demand_trend: Array<{ week: string; forecast_demand: number }>;
}

export interface Shortage {
  shortage_id: string;
  sku_id: string;
  location_id: string;
  week_start: string;
  demand_quantity: number;
  projected_available: number;
  shortage_quantity: number;
  severity: string;
  root_cause: string;
  priority_score: number;
  status: string;
}

export interface MitigationOption {
  mitigation_id: string;
  shortage_id: string;
  mitigation_type: string;
  proposed_quantity: number;
  estimated_cost: number;
  expected_arrival_date: string;
  service_impact: string;
  feasibility_status: string;
  recommendation_score: number;
  is_approved: boolean;
}

export interface Supplier {
  supplier_id: string;
  supplier_name: string;
  region: string;
  reliability_score: number;
  is_active: boolean;
}

export interface DataIssue {
  issue_id: string;
  issue_type: string;
  affected_entity_type: string;
  affected_entity_id: string;
  detection_result: string;
  severity: string;
  explanation: string;
  resolution_status: string;
}

export interface AuditLog {
  audit_id: string;
  entity_type: string;
  entity_id: string;
  previous_state: string;
  new_state: string;
  event_type: string;
  timestamp: string;
  explanation: string;
}

export interface EvaluationMetrics {
  demand_coverage_pct: number;
  shortage_detection_precision_pct: number;
  shortage_detection_recall_pct: number;
  inventory_reconciliation_pct: number;
  supplier_feasibility_pct: number;
  mitigation_success_rate_pct: number;
  total_mitigation_cost: number;
  service_improvement: string;
  data_integrity_score_pct: number;
  anomaly_detection_rate_pct: number;
  total_anomalies_detected: number;
}
