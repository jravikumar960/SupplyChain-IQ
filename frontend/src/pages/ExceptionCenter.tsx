import React, { useEffect, useState } from 'react';
import { fetchExceptions } from '../services/api';
import { DataIssue } from '../types';
import { AlertOctagon, AlertTriangle, CheckCircle2, ShieldAlert } from 'lucide-react';
import { StatusBadge } from '../components/StatusBadge';
import { KPICard } from '../components/KPICard';
import { LoadingSkeleton } from '../components/LoadingSkeleton';
import { EmptyState } from '../components/EmptyState';

export const ExceptionCenter: React.FC = () => {
  const [exceptions, setExceptions] = useState<DataIssue[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchExceptions().then(data => {
      setExceptions(data);
      setLoading(false);
    });
  }, []);

  const criticalCount = exceptions.filter(e => e.severity === 'Critical').length;
  const warningCount = exceptions.filter(e => e.severity === 'High' || e.severity === 'Medium').length;

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Exception Center & Anomaly Governance</h1>
            <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-rose-50 text-rose-700 border border-rose-200">
              {exceptions.length} Anomalies Detected
            </span>
          </div>
          <p className="text-slate-500 text-xs mt-1">Injected data anomalies, validation rule breaches, and deterministic edge-case governance.</p>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        <KPICard
          title="Total Exceptions"
          value={exceptions.length}
          subtitle="Governed anomaly records"
          icon={AlertOctagon}
          iconColor="rose"
        />
        <KPICard
          title="Critical Severities"
          value={criticalCount}
          subtitle="Immediate attention required"
          badge={{ text: 'Action Required', variant: 'negative' }}
          icon={ShieldAlert}
          iconColor="rose"
        />
        <KPICard
          title="Resolution Rate"
          value="100%"
          subtitle="All exceptions audited"
          badge={{ text: 'Fully Audited', variant: 'positive' }}
          icon={CheckCircle2}
          iconColor="emerald"
        />
      </div>

      {/* Exception Cards List */}
      <div className="space-y-4">
        {loading ? (
          <LoadingSkeleton variant="card" rows={3} />
        ) : exceptions.length === 0 ? (
          <EmptyState
            title="No Exceptions Detected"
            description="All supply chain data conforms to validation rules."
          />
        ) : (
          exceptions.map(ex => (
            <div key={ex.issue_id} className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-[0_1px_3px_rgba(0,0,0,0.04)] hover:shadow-md transition-shadow space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="bg-rose-50 text-rose-600 p-2.5 rounded-xl border border-rose-100">
                    <AlertTriangle className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-slate-900 text-sm tracking-tight">{ex.issue_type}</h3>
                    <p className="text-xs font-mono text-slate-400">{ex.issue_id} • Entity: <span className="text-slate-700 font-semibold">{ex.affected_entity_type} ({ex.affected_entity_id})</span></p>
                  </div>
                </div>
                <StatusBadge status={ex.severity} />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-slate-50/80 p-4 rounded-xl border border-slate-100 text-xs">
                <div>
                  <span className="text-slate-400 uppercase block font-bold mb-1">Detection Result</span>
                  <span className="font-semibold text-slate-800">{ex.detection_result}</span>
                </div>
                <div>
                  <span className="text-slate-400 uppercase block font-bold mb-1">Resolution Status</span>
                  <StatusBadge status={ex.resolution_status} size="sm" />
                </div>
              </div>

              <p className="text-xs text-slate-600 font-medium leading-relaxed bg-blue-50/40 p-3.5 rounded-xl border border-blue-100/60">
                {ex.explanation}
              </p>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
