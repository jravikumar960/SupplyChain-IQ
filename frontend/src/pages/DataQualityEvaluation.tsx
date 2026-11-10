import React, { useEffect, useState } from 'react';
import { fetchEvaluationMetrics } from '../services/api';
import { EvaluationMetrics } from '../types';
import { BarChart3, CheckCircle2, Download, ShieldCheck, Activity, Award } from 'lucide-react';
import { StatusBadge } from '../components/StatusBadge';
import { KPICard } from '../components/KPICard';
import { LoadingSkeleton } from '../components/LoadingSkeleton';
import { EmptyState } from '../components/EmptyState';

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
    return (
      <div className="space-y-6 animate-fadeIn">
        <LoadingSkeleton variant="card" rows={4} />
      </div>
    );
  }

  const metricCards = [
    { label: "Demand Coverage", value: `${metrics?.demand_coverage_pct}%`, subtitle: "Forecast vs actual tracking", icon: Activity, color: "blue" },
    { label: "Shortage Precision", value: `${metrics?.shortage_detection_precision_pct}%`, subtitle: "True positive accuracy", icon: ShieldCheck, color: "emerald" },
    { label: "Shortage Recall", value: `${metrics?.shortage_detection_recall_pct}%`, subtitle: "Stockout capture rate", icon: CheckCircle2, color: "emerald" },
    { label: "Inventory Reconciliation", value: `${metrics?.inventory_reconciliation_pct}%`, subtitle: "Ledger consistency", icon: BarChart3, color: "blue" },
    { label: "Supplier Feasibility Rate", value: `${metrics?.supplier_feasibility_pct}%`, subtitle: "Capacity compliance", icon: Award, color: "indigo" },
    { label: "Mitigation Success Rate", value: `${metrics?.mitigation_success_rate_pct}%`, subtitle: "Automated resolution", icon: CheckCircle2, color: "emerald" },
  ];

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Data Quality & Model Evaluation Benchmarks</h1>
            <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
              Validated 100%
            </span>
          </div>
          <p className="text-slate-500 text-xs mt-1">Measurable performance evaluation metrics, ground truth verification, and audit reports.</p>
        </div>
      </div>

      {/* KPI Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {metricCards.map((m, idx) => {
          const Icon = m.icon;
          return (
            <KPICard
              key={idx}
              title={m.label}
              value={m.value}
              subtitle={m.subtitle}
              icon={Icon}
              iconColor={m.color as any}
            />
          );
        })}
      </div>

      {/* Financial & Integrity Summary Card */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-[0_1px_3px_rgba(0,0,0,0.04)] space-y-3">
          <h3 className="font-bold text-slate-900 text-sm tracking-tight">System Performance & Integrity</h3>
          <div className="space-y-2 text-xs">
            <div className="flex justify-between py-2 border-b border-slate-100">
              <span className="text-slate-500 font-medium">Total Mitigation Cost</span>
              <span className="font-extrabold text-slate-900">${metrics?.total_mitigation_cost.toLocaleString()}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-slate-100">
              <span className="text-slate-500 font-medium">Service Improvement</span>
              <span className="font-extrabold text-blue-600">{metrics?.service_improvement}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-slate-100">
              <span className="text-slate-500 font-medium">Data Integrity Score</span>
              <span className="font-extrabold text-emerald-600">{metrics?.data_integrity_score_pct}%</span>
            </div>
            <div className="flex justify-between py-2">
              <span className="text-slate-500 font-medium">Anomaly Detection Rate</span>
              <span className="font-extrabold text-purple-600">{metrics?.anomaly_detection_rate_pct}% ({metrics?.total_anomalies_detected} detected)</span>
            </div>
          </div>
        </div>

        {/* Dataset Reports Export */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-[0_1px_3px_rgba(0,0,0,0.04)] flex flex-col justify-between space-y-4">
          <div>
            <h3 className="font-bold text-slate-900 text-sm tracking-tight">Export Dataset Reports</h3>
            <p className="text-xs text-slate-500 mt-1">Download validated shortages and exception audit reports in CSV format for compliance review.</p>
          </div>
          <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3 pt-2">
            <a
              href="/api/export/shortages"
              target="_blank"
              rel="noreferrer"
              className="flex-1 inline-flex items-center justify-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2.5 rounded-xl text-xs font-bold shadow-sm transition-colors"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export Shortages CSV</span>
            </a>
            <a
              href="/api/export/exceptions"
              target="_blank"
              rel="noreferrer"
              className="flex-1 inline-flex items-center justify-center space-x-2 bg-slate-900 hover:bg-slate-800 text-white px-4 py-2.5 rounded-xl text-xs font-bold shadow-sm transition-colors"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export Exceptions CSV</span>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};
