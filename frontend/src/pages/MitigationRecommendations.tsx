import React, { useEffect, useState } from 'react';
import { fetchShortages, fetchShortageMitigations, approveMitigation, rejectMitigation } from '../services/api';
import { Shortage, MitigationOption } from '../types';
import { ShieldCheck, CheckCircle2, XCircle, AlertCircle, ArrowRight, ShieldAlert } from 'lucide-react';

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
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center space-x-3">
            <ShieldCheck className="w-7 h-7 text-blue-600" />
            <span>Mitigation Recommendations Engine</span>
          </h1>
          <p className="text-slate-500 text-sm mt-1">Evaluate supplier POs, substitute SKUs, and production increases with automated feasibility validation.</p>
        </div>
      </div>

      {message && (
        <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 p-4 rounded-xl text-sm font-medium flex items-center justify-between shadow-sm">
          <span>{message}</span>
          <button onClick={() => setMessage(null)} className="text-emerald-600 hover:text-emerald-800 font-bold px-2">×</button>
        </div>
      )}

      {/* Select Shortage */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <label className="block text-sm font-semibold text-slate-800">Select Shortage to Mitigate:</label>
        <select
          value={currentShortage?.shortage_id || ''}
          onChange={e => {
            const found = shortages.find(s => s.shortage_id === e.target.value);
            if (found) setCurrentShortage(found);
          }}
          className="w-full bg-slate-50 border border-slate-300 rounded-xl px-4 py-3 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-600 text-slate-800 shadow-inner"
        >
          {shortages.slice(0, 50).map(s => (
            <option key={s.shortage_id} value={s.shortage_id}>
              {s.shortage_id} | SKU: {s.sku_id} | Loc: {s.location_id} | Shortage Qty: {s.shortage_quantity} | Severity: {s.severity}
            </option>
          ))}
        </select>

        {currentShortage && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-slate-100 text-sm">
            <div className="bg-slate-50 p-3 rounded-xl">
              <span className="text-slate-400 block text-xs font-semibold uppercase">SKU ID</span>
              <span className="font-mono font-semibold text-blue-600">{currentShortage.sku_id}</span>
            </div>
            <div className="bg-slate-50 p-3 rounded-xl">
              <span className="text-slate-400 block text-xs font-semibold uppercase">Location ID</span>
              <span className="font-mono font-semibold text-slate-800">{currentShortage.location_id}</span>
            </div>
            <div className="bg-slate-50 p-3 rounded-xl">
              <span className="text-slate-400 block text-xs font-semibold uppercase">Shortage Quantity</span>
              <span className="font-extrabold text-red-600">{currentShortage.shortage_quantity.toLocaleString()} units</span>
            </div>
            <div className="bg-slate-50 p-3 rounded-xl">
              <span className="text-slate-400 block text-xs font-semibold uppercase">Root Cause</span>
              <span className="font-medium text-slate-800">{currentShortage.root_cause}</span>
            </div>
          </div>
        )}
      </div>

      {/* Mitigation Options Cards */}
      <div className="space-y-4">
        <h2 className="text-lg font-bold text-slate-900">Evaluated Mitigation Options</h2>
        {mitigations.length === 0 ? (
          <div className="bg-white p-8 rounded-2xl border border-slate-200 text-center text-slate-500 shadow-sm">
            No mitigation options available for this shortage.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {mitigations.map(mit => {
              const isFeasible = mit.feasibility_status === 'Feasible';
              return (
                <div key={mit.mitigation_id} className={`bg-white p-6 rounded-2xl border shadow-sm space-y-4 relative overflow-hidden transition-all hover:shadow-md ${
                  mit.is_approved ? 'border-emerald-500 ring-2 ring-emerald-500/20 bg-emerald-50/20' :
                  isFeasible ? 'border-slate-200 hover:border-blue-300' : 'border-red-200 bg-red-50/10'
                }`}>
                  {mit.is_approved && (
                    <div className="absolute top-0 right-0 bg-emerald-600 text-white text-xs font-bold px-3 py-1 rounded-bl-xl shadow-sm">
                      APPROVED
                    </div>
                  )}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span className="px-3 py-1 bg-blue-50 text-blue-700 font-semibold text-xs rounded-full border border-blue-100">
                        {mit.mitigation_type}
                      </span>
                      {mit.supplier_id && (
                        <span className="text-xs font-mono font-medium text-slate-600 bg-slate-100 px-2.5 py-0.5 rounded-md">
                          {mit.supplier_id}
                        </span>
                      )}
                    </div>
                    <span className="text-xs font-bold text-slate-500 bg-slate-100 px-2.5 py-1 rounded-lg">
                      Score: {mit.recommendation_score}
                    </span>
                  </div>

                  {mit.feasibility_explanation && (
                    <div className={`text-xs p-3.5 rounded-xl border ${
                      isFeasible ? 'bg-slate-50 text-slate-700 border-slate-100' : 'bg-red-50/80 text-red-800 border-red-200'
                    }`}>
                      <div className="flex items-center space-x-1.5 font-semibold mb-1">
                        {isFeasible ? <CheckCircle2 className="w-4 h-4 text-emerald-600" /> : <ShieldAlert className="w-4 h-4 text-red-600" />}
                        <span>Feasibility Analysis</span>
                      </div>
                      <p className="leading-relaxed">{mit.feasibility_explanation}</p>
                    </div>
                  )}

                  <div className="grid grid-cols-2 gap-4 text-sm bg-slate-50/50 p-4 rounded-xl border border-slate-100">
                    <div>
                      <span className="text-slate-400 text-xs block font-semibold uppercase">Proposed Quantity</span>
                      <span className="font-semibold text-slate-900">{mit.proposed_quantity.toLocaleString()}</span>
                    </div>
                    <div>
                      <span className="text-slate-400 text-xs block font-semibold uppercase">Estimated Cost</span>
                      <span className="font-semibold text-slate-900">${mit.estimated_cost.toLocaleString()}</span>
                    </div>
                    <div>
                      <span className="text-slate-400 text-xs block font-semibold uppercase">Expected Arrival</span>
                      <span className="font-medium text-slate-800">{mit.expected_arrival_date}</span>
                    </div>
                    <div>
                      <span className="text-slate-400 text-xs block font-semibold uppercase">Feasibility Status</span>
                      <span className={`font-bold inline-flex items-center space-x-1 ${isFeasible ? 'text-emerald-600' : 'text-red-600'}`}>
                        {isFeasible ? <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> : <XCircle className="w-3.5 h-3.5 mr-1" />}
                        {mit.feasibility_status}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-2">
                    <span className="text-xs text-slate-400 font-medium">Impact: {mit.service_impact}</span>
                    <div className="flex items-center space-x-3">
                      <button
                        onClick={() => handleReject(mit.mitigation_id)}
                        className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-xl transition-colors"
                      >
                        Reject
                      </button>
                      <button
                        onClick={() => handleApprove(mit.mitigation_id)}
                        disabled={!isFeasible}
                        title={!isFeasible ? "Cannot approve infeasible mitigation option (violates capacity/MOQ/lead-time rules)" : "Approve mitigation action"}
                        className={`px-4 py-2 text-xs font-semibold rounded-xl transition-all shadow-sm ${
                          isFeasible
                            ? 'bg-emerald-600 hover:bg-emerald-700 text-white shadow-emerald-600/20 cursor-pointer'
                            : 'bg-slate-200 text-slate-400 cursor-not-allowed opacity-60'
                        }`}
                      >
                        Approve Action
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
