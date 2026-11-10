import React, { useState, useEffect } from 'react';
import { runSimulation, fetchSimulationHistory } from '../services/api';
import { Sliders, Play, AlertTriangle, DollarSign, Activity, Package, MapPin, AlertCircle } from 'lucide-react';
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
    { metric: 'Shortage Count', Baseline: currentResult.baseline_shortages_count, Simulated: currentResult.simulated_shortages_count },
    { metric: 'Shortage Qty (Units)', Baseline: currentResult.baseline_total_shortage_qty, Simulated: currentResult.simulated_total_shortage_qty },
    { metric: 'Backorders (Units)', Baseline: currentResult.baseline_backorder_qty, Simulated: currentResult.simulated_backorder_qty },
    { metric: 'Safety Deficit (Units)', Baseline: currentResult.baseline_safety_deficit, Simulated: currentResult.simulated_safety_deficit },
    { metric: 'Financial Exposure ($k)', Baseline: Math.round(currentResult.baseline_exposure_value / 1000), Simulated: Math.round(currentResult.simulated_exposure_value / 1000) }
  ] : [];

  return (
    <div className="space-y-8 animate-fadeIn">
      <div className="flex justify-between items-center bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 flex items-center space-x-3">
            <Sliders className="w-7 h-7 text-blue-600" />
            <span>Scenario Analysis & What-If Simulation Engine</span>
          </h2>
          <p className="text-sm text-slate-500 mt-1">
            Genuine sequential inventory projection testing demand surges, supplier capacity reductions, and lead-time delays.
          </p>
        </div>
      </div>

      {errorMsg && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-xl flex items-center space-x-3">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Simulation Parameter Controls */}
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 lg:col-span-1">
          <h3 className="text-lg font-bold text-slate-900 mb-4 flex items-center space-x-2">
            <Activity className="w-5 h-5 text-blue-600" />
            <span>Simulation Parameters</span>
          </h3>

          <form onSubmit={handleRunSimulation} className="space-y-6">
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1">Scenario Name</label>
              <input
                type="text"
                value={runName}
                onChange={(e) => setRunName(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-xl text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              />
            </div>

            <div>
              <div className="flex justify-between text-sm font-semibold text-slate-700 mb-1">
                <span>Demand Multiplier</span>
                <span className="text-blue-600">{demandMultiplier}x (1.0–2.0)</span>
              </div>
              <input
                type="range"
                min="1.0"
                max="2.0"
                step="0.05"
                value={demandMultiplier}
                onChange={(e) => setDemandMultiplier(parseFloat(e.target.value))}
                className="w-full accent-blue-600"
              />
            </div>

            <div>
              <div className="flex justify-between text-sm font-semibold text-slate-700 mb-1">
                <span>Supplier Capacity Multiplier</span>
                <span className="text-blue-600">{capacityMultiplier}x (0.5–1.0)</span>
              </div>
              <input
                type="range"
                min="0.5"
                max="1.0"
                step="0.05"
                value={capacityMultiplier}
                onChange={(e) => setCapacityMultiplier(parseFloat(e.target.value))}
                className="w-full accent-blue-600"
              />
            </div>

            <div>
              <div className="flex justify-between text-sm font-semibold text-slate-700 mb-1">
                <span>Lead Time Delay (Days)</span>
                <span className="text-blue-600">+{delayDays} Days (0–21)</span>
              </div>
              <input
                type="range"
                min="0"
                max="21"
                step="1"
                value={delayDays}
                onChange={(e) => setDelayDays(parseInt(e.target.value))}
                className="w-full accent-blue-600"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-xl shadow-lg shadow-blue-600/30 flex items-center justify-center space-x-2 transition-all disabled:opacity-50"
            >
              <Play className="w-4 h-4" />
              <span>{loading ? 'Running Sequential Projection...' : 'Run Scenario Simulation'}</span>
            </button>
          </form>
        </div>

        {/* Results & Comparison Dashboard */}
        <div className="space-y-6 lg:col-span-2">
          {currentResult ? (
            <>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Shortage Count</p>
                      <h4 className="text-3xl font-extrabold text-slate-900 mt-2">
                        {currentResult.simulated_shortages_count}
                        <span className={`text-sm font-bold ml-2 ${currentResult.simulated_shortages_count >= currentResult.baseline_shortages_count ? 'text-red-600' : 'text-green-600'}`}>
                          ({currentResult.simulated_shortages_count - currentResult.baseline_shortages_count >= 0 ? '+' : ''}{currentResult.simulated_shortages_count - currentResult.baseline_shortages_count})
                        </span>
                      </h4>
                      <p className="text-xs text-slate-500 mt-1">Baseline: {currentResult.baseline_shortages_count}</p>
                    </div>
                    <div className="bg-red-50 p-3 rounded-2xl text-red-600">
                      <AlertTriangle className="w-8 h-8" />
                    </div>
                  </div>
                </div>

                <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Backorders & Deficit</p>
                      <h4 className="text-3xl font-extrabold text-slate-900 mt-2">
                        {currentResult.simulated_backorder_qty.toLocaleString()}
                        <span className="text-sm font-bold text-slate-500 ml-1">units</span>
                      </h4>
                      <p className="text-xs text-slate-500 mt-1">Safety Deficit: {currentResult.simulated_safety_deficit.toLocaleString()}</p>
                    </div>
                    <div className="bg-orange-50 p-3 rounded-2xl text-orange-600">
                      <Package className="w-8 h-8" />
                    </div>
                  </div>
                </div>

                <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Financial Exposure</p>
                      <h4 className="text-3xl font-extrabold text-slate-900 mt-2">
                        ${currentResult.simulated_exposure_value.toLocaleString()}
                      </h4>
                      <p className="text-xs text-slate-500 mt-1">Baseline: ${currentResult.baseline_exposure_value.toLocaleString()}</p>
                    </div>
                    <div className="bg-blue-50 p-3 rounded-2xl text-blue-600">
                      <DollarSign className="w-8 h-8" />
                    </div>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white p-4 rounded-xl border border-slate-200 text-center">
                  <p className="text-xs font-semibold text-slate-400">Affected SKUs</p>
                  <p className="text-xl font-bold text-slate-900 mt-1">{currentResult.affected_skus_count}</p>
                </div>
                <div className="bg-white p-4 rounded-xl border border-slate-200 text-center">
                  <p className="text-xs font-semibold text-slate-400">Affected Locations</p>
                  <p className="text-xl font-bold text-slate-900 mt-1">{currentResult.affected_locations_count}</p>
                </div>
                <div className="bg-white p-4 rounded-xl border border-slate-200 text-center">
                  <p className="text-xs font-semibold text-slate-400">Missing Unit Costs</p>
                  <p className="text-xl font-bold text-slate-900 mt-1">{currentResult.missing_unit_cost_count}</p>
                </div>
              </div>

              <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <h3 className="text-lg font-bold text-slate-900 mb-4">Sequential Projection: Baseline vs. Simulated Comparison</h3>
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                      <XAxis dataKey="metric" stroke="#64748b" />
                      <YAxis stroke="#64748b" />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="Baseline" fill="#94a3b8" radius={[6, 6, 0, 0]} />
                      <Bar dataKey="Simulated" fill="#2563eb" radius={[6, 6, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                <div className="mt-4 p-4 bg-slate-50 rounded-xl border border-slate-200 text-sm text-slate-700">
                  <strong>Projection Summary:</strong> {currentResult.summary_notes}
                </div>
              </div>
            </>
          ) : (
            <div className="bg-white p-12 rounded-2xl shadow-sm border border-slate-200 text-center text-slate-500">
              Run a simulation to view projected impact analysis.
            </div>
          )}

          {/* Simulation History Table */}
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
            <h3 className="text-lg font-bold text-slate-900 mb-4">Simulation History</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-slate-200 text-xs font-semibold text-slate-400 uppercase">
                    <th className="py-3 px-4">Scenario Name</th>
                    <th className="py-3 px-4">Demand</th>
                    <th className="py-3 px-4">Capacity</th>
                    <th className="py-3 px-4">Delay</th>
                    <th className="py-3 px-4">Sim. Shortages</th>
                    <th className="py-3 px-4">Sim. Exposure</th>
                    <th className="py-3 px-4">Date</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-sm">
                  {history.map((h) => (
                    <tr key={h.simulation_id} className="hover:bg-slate-50 cursor-pointer" onClick={() => setCurrentResult(h)}>
                      <td className="py-3 px-4 font-semibold text-slate-900">{h.run_name}</td>
                      <td className="py-3 px-4">{h.demand_multiplier}x</td>
                      <td className="py-3 px-4">{h.supplier_capacity_multiplier}x</td>
                      <td className="py-3 px-4">+{h.lead_time_delay_days}d</td>
                      <td className="py-3 px-4 font-bold text-red-600">{h.simulated_shortages_count}</td>
                      <td className="py-3 px-4">${h.simulated_exposure_value.toLocaleString()}</td>
                      <td className="py-3 px-4 text-slate-500">{new Date(h.created_at).toLocaleDateString()}</td>
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
