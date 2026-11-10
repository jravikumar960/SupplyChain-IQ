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
  CheckCircle2
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Legend
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
      <div className="flex items-center justify-center h-96 text-slate-500 font-medium">
        Loading SupplyChain IQ analytics...
      </div>
    );
  }

  const COLORS = ['#ef4444', '#f59e0b', '#3b82f6', '#10b981', '#8b5cf6'];

  const severityData = charts ? Object.entries(charts.shortages_by_severity).map(([name, value]) => ({ name, value })) : [];
  const causeData = charts ? Object.entries(charts.shortages_by_root_cause).map(([name, value]) => ({ name, value })) : [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Executive Dashboard</h1>
        <p className="text-slate-500 text-sm">Real-time demand forecast, shortage exposure, and supply chain health.</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Total SKUs & Locations</p>
            <h3 className="text-2xl font-bold text-slate-900 mt-1">{summary?.total_skus} SKUs</h3>
            <p className="text-xs text-slate-500 mt-1">{summary?.total_locations} active facilities</p>
          </div>
          <div className="bg-blue-50 text-blue-600 p-3 rounded-xl">
            <Boxes className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Projected Shortages</p>
            <h3 className="text-2xl font-bold text-red-600 mt-1">{summary?.total_shortages}</h3>
            <p className="text-xs text-red-500 mt-1 font-medium">{summary?.critical_shortages} critical priority</p>
          </div>
          <div className="bg-red-50 text-red-600 p-3 rounded-xl">
            <AlertTriangle className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Supplier Capacity Utilization</p>
            <h3 className="text-2xl font-bold text-slate-900 mt-1">{summary?.supplier_capacity_utilization_pct}%</h3>
            <p className="text-xs text-emerald-600 mt-1 font-medium">{summary?.total_suppliers} active suppliers</p>
          </div>
          <div className="bg-emerald-50 text-emerald-600 p-3 rounded-xl">
            <Truck className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Mitigation Success Rate</p>
            <h3 className="text-2xl font-bold text-slate-900 mt-1">{summary?.mitigation_success_rate_pct}%</h3>
            <p className="text-xs text-blue-600 mt-1 font-medium">{summary?.exceptions_detected} anomalies detected</p>
          </div>
          <div className="bg-indigo-50 text-indigo-600 p-3 rounded-xl">
            <CheckCircle2 className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Weekly Demand Trend */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
          <h3 className="text-base font-bold text-slate-900 mb-4">Weekly Forecast Demand Trend</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={charts?.weekly_demand_trend || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="week" stroke="#64748b" fontSize={12} />
                <YAxis stroke="#64748b" fontSize={12} />
                <Tooltip />
                <Line type="monotone" dataKey="forecast_demand" stroke="#2563eb" strokeWidth={3} dot={{ fill: '#2563eb' }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Shortages by Severity */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
          <h3 className="text-base font-bold text-slate-900 mb-4">Shortages by Severity</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={severityData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="name" stroke="#64748b" fontSize={12} />
                <YAxis stroke="#64748b" fontSize={12} />
                <Tooltip />
                <Bar dataKey="value" fill="#ef4444" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Root Causes Distribution */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <h3 className="text-base font-bold text-slate-900 mb-4">Shortage Root Causes Analysis</h3>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={causeData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis type="number" stroke="#64748b" fontSize={12} />
              <YAxis dataKey="name" type="category" width={220} stroke="#64748b" fontSize={11} />
              <Tooltip />
              <Bar dataKey="value" fill="#3b82f6" radius={[0, 6, 6, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
