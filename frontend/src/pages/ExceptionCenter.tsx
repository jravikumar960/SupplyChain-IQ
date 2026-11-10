import React, { useEffect, useState } from 'react';
import { fetchExceptions } from '../services/api';
import { DataIssue } from '../types';
import { AlertOctagon, AlertTriangle, CheckCircle2 } from 'lucide-react';

export const ExceptionCenter: React.FC = () => {
  const [exceptions, setExceptions] = useState<DataIssue[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchExceptions().then(data => {
      setExceptions(data);
      setLoading(false);
    });
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-950 tracking-tight">Exception Center</h1>
        <p className="text-slate-600 text-sm">Inspect injected data anomalies, validation failures, and edge-case exceptions.</p>
      </div>

      <div className="grid grid-cols-1 gap-6">
        {loading ? (
          <div className="bg-white p-8 rounded-2xl border border-slate-200 text-center text-slate-500">Loading exceptions...</div>
        ) : exceptions.map(ex => (
          <div key={ex.issue_id} className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="bg-red-50 text-red-600 p-2.5 rounded-xl">
                  <AlertTriangle className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-bold text-slate-900 text-base">{ex.issue_type}</h3>
                  <p className="text-xs font-mono text-slate-500">{ex.issue_id} • Affected: {ex.affected_entity_type} ({ex.affected_entity_id})</p>
                </div>
              </div>
              <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                ex.severity === 'Critical' ? 'bg-red-100 text-red-700' : 'bg-orange-100 text-orange-700'
              }`}>
                {ex.severity}
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-slate-50 p-4 rounded-xl text-sm">
              <div>
                <span className="text-slate-400 text-xs uppercase block font-semibold">Detection Result</span>
                <span className="font-medium text-slate-800">{ex.detection_result}</span>
              </div>
              <div>
                <span className="text-slate-400 text-xs uppercase block font-semibold">Resolution Status</span>
                <span className="font-semibold text-blue-600">{ex.resolution_status}</span>
              </div>
            </div>

            <p className="text-sm text-slate-700 font-medium">{ex.explanation}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
