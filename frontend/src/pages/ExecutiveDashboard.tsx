import React, { useEffect, useState } from 'react';
import {
  fetchSummary,
  fetchCharts
} from '../services/api';
import {
  DashboardSummary,
  DashboardCharts
} from '../types';
import {
  Boxes,
  MapPin,
  Truck,
  AlertTriangle,
  TrendingUp,
  ShieldAlert,
  Activity,
  CheckCircle2,
  DollarSign,
  ArrowUpRight,
  ArrowDownRight,
  Layers,
  Sparkles
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Cell,
  LineChart,
  Line,
  Legend,
  Area,
  AreaChart
} from 'recharts';

export const ExecutiveDashboard: React.FC = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [charts, setCharts] = useState<DashboardCharts | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([fetchSummary(), fetchCharts()])
      .then(([summaryData, chartsData]) => {
        setSummary(summaryData);
        setCharts(chartsData);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to load dashboard data", err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-96 space-y-3">
        <div className="w-8 h-8 border-3 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
        <p className="text-slate-500 font-medium text-xs">Loading SupplyChain IQ analytics...</p>
      </div>
    );
  }

  const SEVERITY_COLORS: Record<string, string> = {
    Critical: '#ef4444',
    High: '#f97316',
    Medium: '#eab308',
    Low: '#3b82f6'
  };

  const severityData = charts ? Object.entries(charts.shortages_by_severity).map(([name, value]) => ({ name, value })) : [];
  const causeData = charts ? Object.entries(charts.shortages_by_root_cause).map(([name, value]) => ({ name, value })) : [];

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Page Title & Operational Status Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Executive Operations Overview</h1>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-50 text-blue-700 border border-blue-200">FY26·W01–W12</span>
          </div>
          <p className="text-slate-500 text-xs mt-1">Multi-echelon demand forecasts, shortage exposure, and automated mitigation performance.</p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="bg-white border border-slate-200/80 rounded-xl px-3.5 py-1.5 shadow-2xs flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span className="text-xs font-semibold text-slate-700">All 10 Facilities Live</span>
          </div>
        </div>
      </div>

      {/* Primary KPI Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* Total Forecast Demand */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-[0_1px_3px_rgba(0,0,0,0.04)] hover:shadow-md transition-shadow relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Total Forecast Demand</span>
            <div className="bg-blue-50 text-blue-600 p-2.5 rounded-xl">
              <Boxes className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-2">
            <h3 className="text-2xl font-black text-slate-900 tracking-tight">
              {summary?.total_forecast_demand ? (summary.total_forecast_demand / 1000).toFixed(1) : 0}k
              <span className="text-xs font-semibold text-slate-400 ml-1.5 font-normal">units</span>
            </h3>
            <div className="flex items-center space-x-1.5 mt-2">
              <span className="inline-flex items-center text-[11px] font-semibold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-md">
                {summary?.total_skus} SKUs
              </span>
              <span className="text-[11px] text-slate-400">• Across {summary?.total_locations} locations</span>
            </div>
          </div>
        </div>

        {/* Projected Shortages & Exposure */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-[0_1px_3px_rgba(0,0,0,0.04)] hover:shadow-md transition-shadow relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Shortage Incidents</span>
            <div className="bg-rose-50 text-rose-600 p-2.5 rounded-xl">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-2">
            <div className="flex items-baseline space-x-2">
              <h3 className="text-2xl font-black text-rose-600 tracking-tight">{summary?.total_shortages}</h3>
              <span className="text-xs font-bold text-rose-500 bg-rose-50 px-2 py-0.5 rounded-md">
                {summary?.critical_shortages} Critical
              </span>
            </div>
            <p className="text-[11px] text-slate-400 mt-2">
              Total Deficit Exposure: <span className="font-semibold text-slate-700">{summary?.total_shortage_exposure ? (summary.total_shortage_exposure / 1000).toFixed(1) : 0}k units</span>
            </p>
          </div>
        </div>

        {/* Supplier Capacity Utilization */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-[0_1px_3px_rgba(0,0,0,0.04)] hover:shadow-md transition-shadow relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Supplier Capacity</span>
            <div className="bg-emerald-50 text-emerald-600 p-2.5 rounded-xl">
              <Truck className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-2">
            <div className="flex items-baseline space-x-2">
              <h3 className="text-2xl font-black text-slate-900 tracking-tight">{summary?.supplier_capacity_utilization_pct}%</h3>
              <span className="inline-flex items-center text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-md">
                Optimal Band
              </span>
            </div>
            <p className="text-[11px] text-slate-400 mt-2">
              Active Network: <span className="font-semibold text-slate-700">{summary?.total_suppliers} verified suppliers</span>
            </p>
          </div>
        </div>

        {/* Mitigation Success Rate */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-[0_1px_3px_rgba(0,0,0,0.04)] hover:shadow-md transition-shadow relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Mitigation Success Rate</span>
            <div className="bg-indigo-50 text-indigo-600 p-2.5 rounded-xl">
              <CheckCircle2 className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-2">
            <div className="flex items-baseline space-x-2">
              <h3 className="text-2xl font-black text-slate-900 tracking-tight">{summary?.mitigation_success_rate_pct}%</h3>
              <span className="inline-flex items-center text-[11px] font-semibold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded-md">
                Automated
              </span>
            </div>
            <p className="text-[11px] text-slate-400 mt-2">
              Governance: <span className="font-semibold text-slate-700">{summary?.exceptions_detected} data issues flagged</span>
            </p>
          </div>
        </div>
      </div>

      {/* Visual Analytics Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Weekly Demand Trend (2 cols) */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-[0_1px_3px_rgba(0,0,0,0.04)] lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-slate-900 tracking-tight">Weekly Forecast Demand Trajectory</h3>
              <p className="text-xs text-slate-400 mt-0.5">Sequential 12-week forward demand curve across all distribution nodes.</p>
            </div>
            <div className="flex items-center space-x-2 text-xs">
              <span className="inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-slate-50 text-slate-600 font-medium border border-slate-200/60">
                <span className="w-2 h-2 rounded-full bg-blue-600"></span>
                <span>Forecast Quantity</span>
              </span>
            </div>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={charts?.weekly_demand_trend || []} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorDemand" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#2563eb" stopOpacity={0.15}/>
                    <stop offset="95%" stopColor="#2563eb" stopOpacity={0.0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="week" stroke="#94a3b8" fontSize={11} tickLine={false} />
                <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} tickFormatter={(val) => `${(val / 1000).toFixed(0)}k`} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05)' }}
                  formatter={(val: any) => [`${Number(val).toLocaleString()} units`, 'Forecast Demand']}
                />
                <Area type="monotone" dataKey="forecast_demand" stroke="#2563eb" strokeWidth={2.5} fillOpacity={1} fill="url(#colorDemand)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Shortages by Severity (1 col) */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-[0_1px_3px_rgba(0,0,0,0.04)] lg:col-span-1">
          <div className="mb-4">
            <h3 className="text-base font-bold text-slate-900 tracking-tight">Shortages by Severity</h3>
            <p className="text-xs text-slate-400 mt-0.5">Projected stockouts classified by business impact.</p>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={severityData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="name" stroke="#94a3b8" fontSize={11} tickLine={false} />
                <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05)' }}
                />
                <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                  {severityData.map((entry, idx) => (
                    <Cell key={`cell-${idx}`} fill={SEVERITY_COLORS[entry.name] || '#3b82f6'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Root Causes Distribution & Key Insights */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-[0_1px_3px_rgba(0,0,0,0.04)]">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-bold text-slate-900 tracking-tight">Shortage Root Cause Distribution</h3>
            <p className="text-xs text-slate-400 mt-0.5">Attribution breakdown isolating supplier delays, capacity deficits, and inventory discrepancies.</p>
          </div>
        </div>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={causeData} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
              <XAxis type="number" stroke="#94a3b8" fontSize={11} tickLine={false} />
              <YAxis dataKey="name" type="category" width={220} stroke="#64748b" fontSize={11} tickLine={false} />
              <Tooltip
                contentStyle={{ backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05)' }}
                formatter={(val: any) => [`${val} shortages`, 'Frequency']}
              />
              <Bar dataKey="value" fill="#3b82f6" radius={[0, 6, 6, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
