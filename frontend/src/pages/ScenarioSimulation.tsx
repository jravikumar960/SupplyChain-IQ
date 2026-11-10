import React, { useState, useEffect } from 'react';
import { runSimulation, fetchSimulationHistory } from '../services/api';
import { Sliders, Play, AlertTriangle, DollarSign, Activity, Package, MapPin, AlertCircle, ArrowUpRight, ArrowDownRight, Layers, Sparkles, History } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts';

export function ScenarioSimulation() {
  const [runName, setRunName] = useState('Q3 Stress Test & Demand Surge');
  const [demandMultiplier, setDemandMultiplier] = useState(1.2);
  const [capacityMultiplier, setCapacityMultiplier] = useState(0.8);
  const [delayDays, setDelayDays] = useState(7);

  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [currentResult, setCurrentResult] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const data = await fetchSimulationHistory();
      setHistory(data);
      if (data && data.length > 0 && !currentResult) {
        setCurrentResult(data[0]);
      }
    } catch (err) {
      console.error("Failed to load simulation history", err);
    }
  };

  const handleRunSimulation = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg(null);
    try {
      const params = new URLSearchParams({
        run_name: runName,
        demand_multiplier: demandMultiplier.toString(),
        supplier_capacity_multiplier: capacityMultiplier.toString(),
        lead_time_delay_days: delayDays.toString(),
      });
      const res = await fetch(`/api/simulation/run?${params.toString()}`, { method: 'POST' });
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Simulation failed");
      }
      const data = await res.json();
      setCurrentResult(data);
      await loadHistory();
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to execute simulation run");
    } finally {
      setLoading(false);
    }
  };

  const chartData = currentResult ? [
    { metric: 'Shortages', Baseline: currentResult.baseline_shortages_count, Simulated: currentResult.simulated_shortages_count },
    { metric: 'Qty (k)', Baseline: Math.round(currentResult.baseline_total_shortage_qty / 1000), Simulated: Math.round(currentResult.simulated_total_shortage_qty / 1000) },
    { metric: 'Backorders (k)', Baseline: Math.round(currentResult.baseline_backorder_qty / 1000), Simulated: Math.round(currentResult.simulated_backorder_qty / 1000) },
    { metric: 'Safety Deficit (k)', Baseline: Math.round(currentResult.baseline_safety_deficit / 1000), Simulated: Math.round(currentResult.simulated_safety_deficit / 1000) },
    { metric: 'Exposure ($k)', Baseline: Math.round(currentResult.baseline_exposure_value / 1000), Simulated: Math.round(currentResult.simulated_exposure_value / 1000) }
  ] : [];

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Title Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Scenario Analysis & What-If Simulation Engine</h1>
            <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
              Interactive
            </span>
          </div>
          <p className="text-slate-500 text-xs mt-1">
            Deterministic sequential inventory projection testing demand surges, supplier capacity reductions, and lead-time delays.
          </p>
        </div>
      </div>

      {errorMsg && (
        <div className="bg-rose-50 border border-rose-200 text-rose-700 px-5 py-4 rounded-xl flex items-center space-x-3 text-xs font-semibold shadow-xs">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Simulation Parameter Controls */}
        <div className="bg-white p-6 rounded-2xl shadow-[0_1px_3px_rgba(0,0,0,0.04)] border border-slate-200/80 lg:col-span-1 space-y-6">
          <div className="border-b border-slate-100 pb-4">
            <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
              <Sliders className="w-4 h-4 text-blue-600" />
              <span>Simulation Controls</span>
            </h3>
            <p className="text-xs text-slate-400 mt-1">Configure macroeconomic or network shocks.</p>
          </div>

          <form onSubmit={handleRunSimulation} className="space-y-5">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-1.5">Scenario Label</label>
              <input
                type="text"
                value={runName}
                onChange={(e) => setRunName(e.target.value)}
                className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs font-semibold focus:ring-2 focus:ring-blue-600 focus:bg-white text-slate-800 transition-all"
                required
              />
            </div>

            <div className="bg-slate-50/80 p-3.5 rounded-xl border border-slate-100 space-y-2">
              <div className="flex justify-between text-xs font-bold text-slate-700">
                <span>Demand Surge Multiplier</span>
                <span className="text-blue-600 font-extrabold">{demandMultiplier.toFixed(2)}x (+{Math.round((demandMultiplier - 1.0) * 100)}%)</span>
              </div>
              <input
                type="range"
                min="1.0"
                max="2.0"
                step="0.05"
                value={demandMultiplier}
                onChange={(e) => setDemandMultiplier(parseFloat(e.target.value))}
                className="w-full accent-blue-600 cursor-pointer"
              />
              <span className="text-[10px] text-slate-400 block">Baseline demand scaled up to 200%.</span>
            </div>

            <div className="bg-slate-50/80 p-3.5 rounded-xl border border-slate-100 space-y-2">
              <div className="flex justify-between text-xs font-bold text-slate-700">
                <span>Supplier Capacity Disruption</span>
                <span className="text-blue-600 font-extrabold">{capacityMultiplier.toFixed(2)}x ({Math.round((1.0 - capacityMultiplier) * 100)}% cut)</span>
              </div>
              <input
                type="range"
                min="0.5"
                max="1.0"
                step="0.05"
                value={capacityMultiplier}
                onChange={(e) => setCapacityMultiplier(parseFloat(e.target.value))}
                className="w-full accent-blue-600 cursor-pointer"
              />
              <span className="text-[10px] text-slate-400 block">Reduces weekly supplier delivery throughput.</span>
            </div>

            <div className="bg-slate-50/80 p-3.5 rounded-xl border border-slate-100 space-y-2">
              <div className="flex justify-between text-xs font-bold text-slate-700">
                <span>Inbound Lead Time Delay</span>
                <span className="text-blue-600 font-extrabold">+{delayDays} Days</span>
              </div>
              <input
                type="range"
                min="0"
                max="21"
                step="1"
                value={delayDays}
                onChange={(e) => setDelayDays(parseInt(e.target.value))}
                className="w-full accent-blue-600 cursor-pointer"
              />
              <span className="text-[10px] text-slate-400 block">Simulates port congestion or transit delays.</span>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-xl shadow-md shadow-blue-600/30 flex items-center justify-center space-x-2 transition-all disabled:opacity-50 text-xs"
            >
              <Play className="w-3.5 h-3.5" />
              <span>{loading ? 'Executing Projection Engine...' : 'Run Scenario Simulation'}</span>
            </button>
          </form>
        </div>

        {/* Results & Comparison Dashboard */}
        <div className="space-y-6 lg:col-span-2">
          {currentResult ? (
            <>
              {/* Top Delta Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                <div className="bg-white p-5 rounded-2xl shadow-[0_1px_3px_rgba(0,0,0,0.04)] border border-slate-200/80">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Simulated Shortages</p>
                      <h4 className="text-2xl font-black text-slate-900 mt-1">
                        {currentResult.simulated_shortages_count}
                        <span className={`text-xs font-bold ml-1.5 ${currentResult.simulated_shortages_count >= currentResult.baseline_shortages_count ? 'text-rose-600' : 'text-emerald-600'}`}>
                          ({currentResult.simulated_shortages_count - currentResult.baseline_shortages_count >= 0 ? '+' : ''}{currentResult.simulated_shortages_count - currentResult.baseline_shortages_count})
                        </span>
                      </h4>
                      <p className="text-[11px] text-slate-400 mt-1">Baseline: {currentResult.baseline_shortages_count} events</p>
                    </div>
                    <div className="bg-rose-50 p-2.5 rounded-xl text-rose-600">
                      <AlertTriangle className="w-5 h-5" />
                    </div>
                  </div>
                </div>

                <div className="bg-white p-5 rounded-2xl shadow-[0_1px_3px_rgba(0,0,0,0.04)] border border-slate-200/80">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Backorders & Deficit</p>
                      <h4 className="text-2xl font-black text-slate-900 mt-1">
                        {(currentResult.simulated_backorder_qty / 1000).toFixed(1)}k
                        <span className="text-xs font-normal text-slate-400 ml-1">units</span>
                      </h4>
                      <p className="text-[11px] text-slate-400 mt-1">Safety Deficit: {(currentResult.simulated_safety_deficit / 1000).toFixed(1)}k units</p>
                    </div>
                    <div className="bg-orange-50 p-2.5 rounded-xl text-orange-600">
                      <Package className="w-5 h-5" />
                    </div>
                  </div>
                </div>

                <div className="bg-white p-5 rounded-2xl shadow-[0_1px_3px_rgba(0,0,0,0.04)] border border-slate-200/80">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Financial Exposure</p>
                      <h4 className="text-2xl font-black text-slate-900 mt-1">
                        ${(currentResult.simulated_exposure_value / 1000).toFixed(1)}k
                      </h4>
                      <p className="text-[11px] text-slate-400 mt-1">Baseline: ${(currentResult.baseline_exposure_value / 1000).toFixed(1)}k</p>
                    </div>
                    <div className="bg-blue-50 p-2.5 rounded-xl text-blue-600">
                      <DollarSign className="w-5 h-5" />
                    </div>
                  </div>
                </div>
              </div>

              {/* Sub-Metrics Row */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white p-4 rounded-xl border border-slate-200/80 text-center shadow-2xs">
                  <p className="text-[10px] font-bold text-slate-400 uppercase">Affected SKUs</p>
                  <p className="text-lg font-black text-slate-900 mt-0.5">{currentResult.affected_skus_count}</p>
                </div>
                <div className="bg-white p-4 rounded-xl border border-slate-200/80 text-center shadow-2xs">
                  <p className="text-[10px] font-bold text-slate-400 uppercase">Affected Locations</p>
                  <p className="text-lg font-black text-slate-900 mt-0.5">{currentResult.affected_locations_count}</p>
                </div>
                <div className="bg-white p-4 rounded-xl border border-slate-200/80 text-center shadow-2xs">
                  <p className="text-[10px] font-bold text-slate-400 uppercase">Missing Unit Costs</p>
                  <p className="text-lg font-black text-slate-900 mt-0.5">{currentResult.missing_unit_cost_count}</p>
                </div>
              </div>

              {/* Baseline vs Simulated Comparison Chart */}
              <div className="bg-white p-6 rounded-2xl shadow-[0_1px_3px_rgba(0,0,0,0.04)] border border-slate-200/80">
                <div className="mb-4">
                  <h3 className="text-base font-bold text-slate-900 tracking-tight">Scenario Delta: Baseline vs. Simulated Projection</h3>
                  <p className="text-xs text-slate-400 mt-0.5">Direct comparison across core shortage metrics.</p>
                </div>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                      <XAxis dataKey="metric" stroke="#94a3b8" fontSize={11} tickLine={false} />
                      <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} />
                      <Tooltip
                        contentStyle={{ backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05)' }}
                      />
                      <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                      <Bar dataKey="Baseline" fill="#94a3b8" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="Simulated" fill="#2563eb" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                <div className="mt-4 p-3.5 bg-slate-50 rounded-xl border border-slate-200/80 text-xs text-slate-600 leading-relaxed">
                  <span className="font-bold text-slate-800">Projection Summary:</span> {currentResult.summary_notes}
                </div>
              </div>
            </>
          ) : (
            <div className="bg-white p-12 rounded-2xl shadow-sm border border-slate-200 text-center text-slate-500">
              Run a simulation to view projected impact analysis.
            </div>
          )}

          {/* Simulation History Table */}
          <div className="bg-white p-6 rounded-2xl shadow-[0_1px_3px_rgba(0,0,0,0.04)] border border-slate-200/80">
            <h3 className="text-sm font-bold text-slate-900 mb-3 flex items-center space-x-2">
              <History className="w-4 h-4 text-slate-500" />
              <span>Historical Simulation Runs</span>
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="border-b border-slate-200 text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                    <th className="py-2.5 px-3">Scenario Name</th>
                    <th className="py-2.5 px-3">Demand</th>
                    <th className="py-2.5 px-3">Capacity</th>
                    <th className="py-2.5 px-3">Delay</th>
                    <th className="py-2.5 px-3">Sim. Shortages</th>
                    <th className="py-2.5 px-3">Sim. Exposure</th>
                    <th className="py-2.5 px-3 text-right">Run Date</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {history.map((h) => (
                    <tr
                      key={h.simulation_id}
                      className={`hover:bg-slate-50 cursor-pointer transition-colors ${
                        currentResult?.simulation_id === h.simulation_id ? 'bg-blue-50/50 font-semibold' : ''
                      }`}
                      onClick={() => setCurrentResult(h)}
                    >
                      <td className="py-2.5 px-3 font-medium text-slate-900">{h.run_name}</td>
                      <td className="py-2.5 px-3 text-blue-600 font-bold">{h.demand_multiplier}x</td>
                      <td className="py-2.5 px-3 text-slate-600">{h.supplier_capacity_multiplier}x</td>
                      <td className="py-2.5 px-3 text-slate-600">+{h.lead_time_delay_days}d</td>
                      <td className="py-2.5 px-3 font-bold text-rose-600">{h.simulated_shortages_count}</td>
                      <td className="py-2.5 px-3 font-semibold text-slate-800">${h.simulated_exposure_value.toLocaleString()}</td>
                      <td className="py-2.5 px-3 text-right text-slate-400">{new Date(h.created_at).toLocaleDateString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
