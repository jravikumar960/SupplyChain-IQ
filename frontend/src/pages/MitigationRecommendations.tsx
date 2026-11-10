import React, { useEffect, useState } from 'react';
import { fetchShortages, fetchShortageMitigations, approveMitigation, rejectMitigation } from '../services/api';
import { Shortage, MitigationOption } from '../types';
import { ShieldCheck, CheckCircle2, XCircle, AlertCircle, ArrowRight } from 'lucide-react';

interface MitigationProps {
  selectedShortageId?: string | null;
}

export const MitigationRecommendations: React.FC<MitigationProps> = ({ selectedShortageId }) => {
  const [shortages, setShortages] = useState<Shortage[]>([]);
  const [currentShortage, setCurrentShortage] = useState<Shortage | null>(null);
  const [mitigations, setMitigations] = useState<MitigationOption[]>([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    fetchShortages().then(data => {
      setShortages(data);
      if (data.length > 0) {
        const target = selectedShortageId
          ? data.find((s: Shortage) => s.shortage_id === selectedShortageId) || data[0]
          : data[0];
        setCurrentShortage(target);
      }
      setLoading(false);
    });
  }, [selectedShortageId]);

  useEffect(() => {
    if (currentShortage) {
      fetchShortageMitigations(currentShortage.shortage_id).then(mits => {
        setMitigations(mits);
      });
    }
  }, [currentShortage]);

  const handleApprove = async (mitId: string) => {
    try {
      const res = await approveMitigation(mitId);
      setMessage(res.message);
      // Refresh mitigations
      if (currentShortage) {
        const mits = await fetchShortageMitigations(currentShortage.shortage_id);
        setMitigations(mits);
      }
    } catch (err: any) {
      alert(err.message || "Failed to approve mitigation (infeasible or blocked)");
    }
  };

  const handleReject = async (mitId: string) => {
    try {
      const res = await rejectMitigation(mitId);
      setMessage(res.message);
      if (currentShortage) {
        const mits = await fetchShortageMitigations(currentShortage.shortage_id);
        setMitigations(mits);
      }
    } catch (err: any) {
      alert("Failed to reject");
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-950 tracking-tight">Mitigation Recommendations</h1>
        <p className="text-slate-600 text-sm">Evaluate and approve feasible mitigation strategies (Supplier PO, Substitutes, Production).</p>
      </div>

      {message && (
        <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 p-4 rounded-xl text-sm font-medium flex items-center justify-between">
          <span>{message}</span>
          <button onClick={() => setMessage(null)} className="text-emerald-600 hover:text-emerald-800 font-bold">×</button>
        </div>
      )}

      {/* Select Shortage */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <label className="block text-sm font-bold text-slate-800">Select Shortage to Mitigate:</label>
        <select
          value={currentShortage?.shortage_id || ''}
          onChange={e => {
            const found = shortages.find(s => s.shortage_id === e.target.value);
            if (found) setCurrentShortage(found);
          }}
          className="w-full bg-slate-50 border border-slate-300 rounded-xl px-4 py-3 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-600 text-slate-800"
        >
          {shortages.slice(0, 50).map(s => (
            <option key={s.shortage_id} value={s.shortage_id}>
              {s.shortage_id} | SKU: {s.sku_id} | Loc: {s.location_id} | Shortage Qty: {s.shortage_quantity} | Severity: {s.severity}
            </option>
          ))}
        </select>

        {currentShortage && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-slate-100 text-sm">
            <div>
              <span className="text-slate-400 block text-xs">SKU</span>
              <span className="font-mono font-semibold text-slate-800">{currentShortage.sku_id}</span>
            </div>
            <div>
              <span className="text-slate-400 block text-xs">Location</span>
              <span className="font-mono font-semibold text-slate-800">{currentShortage.location_id}</span>
            </div>
            <div>
              <span className="text-slate-400 block text-xs">Shortage Quantity</span>
              <span className="font-bold text-red-600">{currentShortage.shortage_quantity}</span>
            </div>
            <div>
              <span className="text-slate-400 block text-xs">Root Cause</span>
              <span className="font-medium text-slate-800">{currentShortage.root_cause}</span>
            </div>
          </div>
        )}
      </div>

      {/* Mitigation Options Cards */}
      <div className="space-y-4">
        <h2 className="text-lg font-bold text-slate-900">Evaluated Mitigation Options</h2>
        {mitigations.length === 0 ? (
          <div className="bg-white p-8 rounded-2xl border border-slate-200 text-center text-slate-500">
            No mitigation options available for this shortage.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {mitigations.map(mit => (
              <div key={mit.mitigation_id} className={`bg-white p-6 rounded-2xl border shadow-sm space-y-4 relative overflow-hidden ${
                mit.is_approved ? 'border-emerald-500 ring-2 ring-emerald-500/20' : 'border-slate-200'
              }`}>
                {mit.is_approved && (
                  <div className="absolute top-0 right-0 bg-emerald-600 text-white text-xs font-semibold px-3 py-1 rounded-bl-xl">
                    APPROVED
                  </div>
                )}
                <div className="flex items-center justify-between">
                  <span className="px-3 py-1 bg-blue-50 text-blue-700 font-semibold text-xs rounded-full">
                    {mit.mitigation_type}
                  </span>
                  <span className="text-xs font-bold text-slate-500">
                    Score: {mit.recommendation_score}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-slate-400 text-xs block">Proposed Quantity</span>
                    <span className="font-semibold text-slate-900">{mit.proposed_quantity}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 text-xs block">Estimated Cost</span>
                    <span className="font-semibold text-slate-900">${mit.estimated_cost.toLocaleString()}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 text-xs block">Expected Arrival</span>
                    <span className="font-medium text-slate-800">{mit.expected_arrival_date}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 text-xs block">Feasibility Status</span>
                    <span className={`font-semibold ${mit.feasibility_status === 'Feasible' ? 'text-emerald-600' : 'text-red-600'}`}>
                      {mit.feasibility_status}
                    </span>
                  </div>
                </div>

                <div className="flex items-center justify-end space-x-3 pt-4 border-t border-slate-100">
                  <button
                    onClick={() => handleReject(mit.mitigation_id)}
                    className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-xl transition-colors"
                  >
                    Reject
                  </button>
                  <button
                    onClick={() => handleApprove(mit.mitigation_id)}
                    disabled={mit.feasibility_status !== 'Feasible'}
                    className={`px-4 py-2 text-xs font-semibold rounded-xl transition-colors ${
                      mit.feasibility_status === 'Feasible'
                        ? 'bg-emerald-600 hover:bg-emerald-700 text-white shadow-md shadow-emerald-600/20'
                        : 'bg-slate-200 text-slate-400 cursor-not-allowed'
                    }`}
                  >
                    Approve Action
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
