import React, { useEffect, useState } from 'react';
import { fetchShortages } from '../services/api';
import { Shortage } from '../types';
import { AlertTriangle, Filter, Search, ChevronRight } from 'lucide-react';

interface ShortageManagementProps {
  onSelectShortage: (shortageId: string) => void;
}

export const ShortageManagement: React.FC<ShortageManagementProps> = ({ onSelectShortage }) => {
  const [shortages, setShortages] = useState<Shortage[]>([]);
  const [loading, setLoading] = useState(true);
  const [severityFilter, setSeverityFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    setLoading(true);
    fetchShortages(severityFilter, statusFilter)
      .then(data => {
        setShortages(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to load shortages", err);
        setLoading(false);
      });
  }, [severityFilter, statusFilter]);

  const filteredShortages = shortages.filter(s =>
    s.sku_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    s.location_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    s.root_cause.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-950 tracking-tight">Shortage Management</h1>
          <p className="text-slate-600 text-sm">Filter, inspect, and manage projected inventory shortages across locations.</p>
        </div>
        <div className="flex items-center space-x-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
            <input
              type="text"
              placeholder="Search SKU, location..."
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              className="pl-9 pr-4 py-2 bg-white border border-slate-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
            />
          </div>
          <select
            value={severityFilter}
            onChange={e => setSeverityFilter(e.target.value)}
            className="bg-white border border-slate-300 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-600 text-slate-800"
          >
            <option value="ALL">All Severities</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>
        </div>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 text-xs uppercase tracking-wider font-semibold">
                <th className="py-4 px-6">Shortage ID</th>
                <th className="py-4 px-6">SKU ID</th>
                <th className="py-4 px-6">Location</th>
                <th className="py-4 px-6">Week</th>
                <th className="py-4 px-6">Demand</th>
                <th className="py-4 px-6">Shortage Qty</th>
                <th className="py-4 px-6">Severity</th>
                <th className="py-4 px-6">Root Cause</th>
                <th className="py-4 px-6">Priority</th>
                <th className="py-4 px-6 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-sm">
              {loading ? (
                <tr>
                  <td colSpan={10} className="text-center py-8 text-slate-500">Loading shortages...</td>
                </tr>
              ) : filteredShortages.length === 0 ? (
                <tr>
                  <td colSpan={10} className="text-center py-8 text-slate-500">No shortages found matching criteria.</td>
                </tr>
              ) : (
                filteredShortages.slice(0, 50).map((s) => (
                  <tr key={s.shortage_id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-4 px-6 font-mono font-medium text-slate-900">{s.shortage_id}</td>
                    <td className="py-4 px-6 font-mono text-blue-600">{s.sku_id}</td>
                    <td className="py-4 px-6 font-mono text-slate-600">{s.location_id}</td>
                    <td className="py-4 px-6 font-medium text-slate-700">{s.week_start}</td>
                    <td className="py-4 px-6 text-slate-700">{s.demand_quantity}</td>
                    <td className="py-4 px-6 font-semibold text-red-600">{s.shortage_quantity}</td>
                    <td className="py-4 px-6">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
                        s.severity === 'Critical' ? 'bg-red-100 text-red-700' :
                        s.severity === 'High' ? 'bg-orange-100 text-orange-700' :
                        'bg-amber-100 text-amber-700'
                      }`}>
                        {s.severity}
                      </span>
                    </td>
                    <td className="py-4 px-6 text-slate-600 max-w-xs truncate" title={s.root_cause}>{s.root_cause}</td>
                    <td className="py-4 px-6 font-semibold text-slate-900">{s.priority_score}</td>
                    <td className="py-4 px-6 text-right">
                      <button
                        onClick={() => onSelectShortage(s.shortage_id)}
                        className="inline-flex items-center space-x-1 bg-blue-50 hover:bg-blue-100 text-blue-600 px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors"
                      >
                        <span>Mitigate</span>
                        <ChevronRight className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
