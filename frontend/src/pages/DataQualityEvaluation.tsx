import React, { useEffect, useState } from 'react';
import { fetchEvaluationMetrics } from '../services/api';
import { EvaluationMetrics } from '../types';
import { BarChart3, CheckCircle2, Download } from 'lucide-react';

export const DataQualityEvaluation: React.FC = () => {
  const [metrics, setMetrics] = useState<EvaluationMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchEvaluationMetrics().then(data => {
      setMetrics(data);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return <div className="text-center py-12 text-slate-500">Loading evaluation metrics...</div>;
  }

  const metricCards = [
    { label: "Demand Coverage", value: `${metrics?.demand_coverage_pct}%`, color: "text-blue-600" },
    { label: "Shortage Detection Precision", value: `${metrics?.shortage_detection_precision_pct}%`, color: "text-emerald-600" },
    { label: "Shortage Detection Recall", value: `${metrics?.shortage_detection_recall_pct}%`, color: "text-emerald-600" },
    { label: "Inventory Reconciliation", value: `${metrics?.inventory_reconciliation_pct}%`, color: "text-blue-600" },
    { label: "Supplier Feasibility Rate", value: `${metrics?.supplier_feasibility_pct}%`, color: "text-indigo-600" },
    { label: "Mitigation Success Rate", value: `${metrics?.mitigation_success_rate_pct}%`, color: "text-emerald-600" },
    { label: "Total Mitigation Cost", value: `$${metrics?.total_mitigation_cost.toLocaleString()}`, color: "text-slate-900" },
    { label: "Service Improvement", value: metrics?.service_improvement, color: "text-blue-600" },
    { label: "Data Integrity Score", value: `${metrics?.data_integrity_score_pct}%`, color: "text-emerald-600" },
    { label: "Anomaly Detection Rate", value: `${metrics?.anomaly_detection_rate_pct}% (${metrics?.total_anomalies_detected} detected)`, color: "text-purple-600" },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-950 tracking-tight">Data Quality & Evaluation</h1>
        <p className="text-slate-600 text-sm">Measurable performance evaluation metrics, ground truth verification, and CSV exports.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {metricCards.map((m, idx) => (
          <div key={idx} className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">{m.label}</span>
            <div className={`text-2xl font-bold ${m.color}`}>{m.value}</div>
          </div>
        ))}
      </div>

      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
        <div>
          <h3 className="font-bold text-slate-900 text-base">Export Dataset Reports</h3>
          <p className="text-slate-500 text-sm">Download validated shortages and exception audit reports in CSV format.</p>
        </div>
        <div className="flex space-x-3">
          <a
            href="/api/export/shortages"
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2.5 rounded-xl text-sm font-semibold shadow-md shadow-blue-600/20 transition-colors"
          >
            <Download className="w-4 h-4" />
            <span>Export Shortages CSV</span>
          </a>
          <a
            href="/api/export/exceptions"
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center space-x-2 bg-slate-800 hover:bg-slate-700 text-white px-4 py-2.5 rounded-xl text-sm font-semibold transition-colors"
          >
            <Download className="w-4 h-4" />
            <span>Export Exceptions CSV</span>
          </a>
        </div>
      </div>
    </div>
  );
};
