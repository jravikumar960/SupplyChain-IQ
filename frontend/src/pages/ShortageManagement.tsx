import React, { useEffect, useState } from 'react';
import { fetchShortages } from '../services/api';
import { Shortage } from '../types';
import { AlertTriangle, Filter, Search, ChevronRight, ChevronLeft, ArrowRight, ShieldAlert } from 'lucide-react';

interface ShortageManagementProps {
  onSelectShortage: (shortageId: string) => void;
}

export const ShortageManagement: React.FC<ShortageManagementProps> = ({ onSelectShortage }) => {
  const [shortages, setShortages] = useState<Shortage[]>([]);
  const [loading, setLoading] = useState(true);
  const [severityFilter, setSeverityFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 20;

  useEffect(() => {
    setLoading(true);
    fetchShortages(severityFilter === 'ALL' ? undefined : severityFilter, statusFilter === 'ALL' ? undefined : statusFilter)
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

  const totalPages = Math.ceil(filteredShortages.length / pageSize) || 1;
  const paginatedShortages = filteredShortages.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  const severityCounts = {
    ALL: shortages.length,
    Critical: shortages.filter(s => s.severity === 'Critical').length,
    High: shortages.filter(s => s.severity === 'High').length,
    Medium: shortages.filter(s => s.severity === 'Medium').length,
    Low: shortages.filter(s => s.severity === 'Low').length,
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Page Title & Filter Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Shortage Management Workbench</h1>
            <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-rose-50 text-rose-700 border border-rose-200">
              {shortages.length} Detected
            </span>
          </div>
          <p className="text-slate-500 text-xs mt-1">Multi-criteria shortage detection, priority scoring, and direct mitigation dispatch.</p>
        </div>

        {/* Search & Severity Filter Bar */}
        <div className="flex items-center space-x-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search SKU, location, root cause..."
              value={searchTerm}
              onChange={e => {
                setSearchTerm(e.target.value);
                setCurrentPage(1);
              }}
              className="pl-9 pr-4 py-2 bg-white border border-slate-200 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-blue-600 shadow-2xs w-64 text-slate-800 transition-all"
            />
          </div>

          <select
            value={statusFilter}
            onChange={e => {
              setStatusFilter(e.target.value);
              setCurrentPage(1);
            }}
            className="bg-white border border-slate-200 rounded-xl px-3 py-2 text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-blue-600 text-slate-700 shadow-2xs"
          >
            <option value="ALL">All Statuses</option>
            <option value="Open">Open</option>
            <option value="Mitigated">Mitigated</option>
            <option value="Ignored">Ignored</option>
          </select>
        </div>
      </div>

      {/* Quick Severity Filter Pills */}
      <div className="flex items-center space-x-2 overflow-x-auto pb-1">
        {(['ALL', 'Critical', 'High', 'Medium', 'Low'] as const).map(sev => {
          const isActive = severityFilter === sev;
          const count = severityCounts[sev];
          return (
            <button
              key={sev}
              onClick={() => {
                setSeverityFilter(sev);
                setCurrentPage(1);
              }}
              className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center space-x-1.5 ${
                isActive
                  ? sev === 'Critical'
                    ? 'bg-rose-600 text-white shadow-sm shadow-rose-600/30'
                    : sev === 'High'
                      ? 'bg-orange-500 text-white shadow-sm shadow-orange-500/30'
                      : 'bg-blue-600 text-white shadow-sm shadow-blue-600/30'
                  : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200/80 shadow-2xs'
              }`}
            >
              <span>{sev === 'ALL' ? 'All Shortages' : sev}</span>
              <span className={`text-[10px] px-1.5 py-0.2 rounded-md ${
                isActive ? 'bg-white/20 text-white' : 'bg-slate-100 text-slate-500'
              }`}>
                {count}
              </span>
            </button>
          );
        })}
      </div>

      {/* Enterprise Data Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-[0_1px_3px_rgba(0,0,0,0.04)] overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50/80 border-b border-slate-200 text-slate-400 text-[11px] uppercase tracking-wider font-bold">
                <th className="py-3.5 px-5">Shortage ID</th>
                <th className="py-3.5 px-5">SKU ID</th>
                <th className="py-3.5 px-5">Location</th>
                <th className="py-3.5 px-5">Week</th>
                <th className="py-3.5 px-5">Demand</th>
                <th className="py-3.5 px-5">Shortage Qty</th>
                <th className="py-3.5 px-5">Severity</th>
                <th className="py-3.5 px-5">Root Cause</th>
                <th className="py-3.5 px-5">Priority</th>
                <th className="py-3.5 px-5 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-xs">
              {loading ? (
                <tr>
                  <td colSpan={10} className="text-center py-12 text-slate-400 font-medium">
                    <div className="flex flex-col items-center justify-center space-y-2">
                      <div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                      <span>Loading projected shortages...</span>
                    </div>
                  </td>
                </tr>
              ) : paginatedShortages.length === 0 ? (
                <tr>
                  <td colSpan={10} className="text-center py-12 text-slate-400 font-medium">
                    No projected shortages found matching active filter criteria.
                  </td>
                </tr>
              ) : (
                paginatedShortages.map((s) => (
                  <tr key={s.shortage_id} className="hover:bg-slate-50/90 transition-colors group">
                    <td className="py-3.5 px-5 font-mono font-medium text-slate-900">{s.shortage_id}</td>
                    <td className="py-3.5 px-5 font-mono font-bold text-blue-600">{s.sku_id}</td>
                    <td className="py-3.5 px-5 font-mono text-slate-600">{s.location_id}</td>
                    <td className="py-3.5 px-5 font-semibold text-slate-700">{s.week_start}</td>
                    <td className="py-3.5 px-5 text-slate-700">{s.demand_quantity.toLocaleString()}</td>
                    <td className="py-3.5 px-5 font-bold text-rose-600">{s.shortage_quantity.toLocaleString()}</td>
                    <td className="py-3.5 px-5">
                      <span className={`inline-flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-[11px] font-bold ${
                        s.severity === 'Critical' ? 'bg-rose-50 text-rose-700 border border-rose-200' :
                        s.severity === 'High' ? 'bg-orange-50 text-orange-700 border border-orange-200' :
                        s.severity === 'Medium' ? 'bg-amber-50 text-amber-700 border border-amber-200' :
                        'bg-blue-50 text-blue-700 border border-blue-200'
                      }`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${
                          s.severity === 'Critical' ? 'bg-rose-500' :
                          s.severity === 'High' ? 'bg-orange-500' :
                          s.severity === 'Medium' ? 'bg-amber-500' :
                          'bg-blue-500'
                        }`}></span>
                        <span>{s.severity}</span>
                      </span>
                    </td>
                    <td className="py-3.5 px-5 text-slate-600 max-w-xs truncate font-medium" title={s.root_cause}>
                      {s.root_cause}
                    </td>
                    <td className="py-3.5 px-5">
                      <div className="flex items-center space-x-2">
                        <span className="font-extrabold text-slate-900">{s.priority_score.toFixed(1)}</span>
                      </div>
                    </td>
                    <td className="py-3.5 px-5 text-right">
                      <button
                        onClick={() => onSelectShortage(s.shortage_id)}
                        className="inline-flex items-center space-x-1 bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded-lg text-xs font-semibold shadow-xs transition-colors"
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

        {/* Table Pagination Footer */}
        <div className="px-6 py-4 bg-slate-50/60 border-t border-slate-200 flex items-center justify-between text-xs text-slate-500">
          <div>
            Showing <span className="font-bold text-slate-700">{filteredShortages.length === 0 ? 0 : (currentPage - 1) * pageSize + 1}</span> to <span className="font-bold text-slate-700">{Math.min(currentPage * pageSize, filteredShortages.length)}</span> of <span className="font-bold text-slate-700">{filteredShortages.length}</span> shortages
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="p-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronLeft className="w-4 h-4 text-slate-600" />
            </button>
            <span className="font-bold text-slate-700 px-2">Page {currentPage} of {totalPages}</span>
            <button
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage >= totalPages}
              className="p-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronRight className="w-4 h-4 text-slate-600" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
