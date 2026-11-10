import React, { useEffect, useState } from 'react';
import { fetchSuppliers } from '../services/api';
import { Supplier } from '../types';
import { Truck, Search, ShieldCheck, MapPin, Star, Building2, ChevronRight } from 'lucide-react';
import { StatusBadge } from '../components/StatusBadge';
import { KPICard } from '../components/KPICard';
import { LoadingSkeleton } from '../components/LoadingSkeleton';
import { EmptyState } from '../components/EmptyState';

export const SupplierManagement: React.FC = () => {
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchSuppliers().then(data => {
      setSuppliers(data);
      setLoading(false);
    });
  }, []);

  const filteredSuppliers = suppliers.filter(s =>
    s.supplier_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    s.supplier_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    s.region.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const avgReliability = suppliers.length ? (suppliers.reduce((acc, s) => acc + s.reliability_score, 0) / suppliers.length * 100).toFixed(1) : '0';

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Supplier Reliability & Capacity Network</h1>
            <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
              {suppliers.length} Verified Vendors
            </span>
          </div>
          <p className="text-slate-500 text-xs mt-1">Multi-tier vendor performance tracking, reliability indexing, and capacity constraints.</p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search vendor name, ID, region..."
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              className="pl-9 pr-4 py-2 bg-white border border-slate-200 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-blue-600 shadow-2xs w-64 text-slate-800 transition-all"
            />
          </div>
        </div>
      </div>

      {/* KPI Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        <KPICard
          title="Active Vendors"
          value={suppliers.length}
          subtitle="Global sourcing network"
          icon={Truck}
          iconColor="blue"
        />
        <KPICard
          title="Average Reliability"
          value={`${avgReliability}%`}
          subtitle="On-time fulfillment index"
          badge={{ text: 'Optimal Band', variant: 'positive' }}
          icon={ShieldCheck}
          iconColor="emerald"
        />
        <KPICard
          title="Capacity Utilization"
          value="78.4%"
          subtitle="Network-wide allocation"
          badge={{ text: 'Balanced', variant: 'info' }}
          icon={Building2}
          iconColor="indigo"
        />
      </div>

      {/* Supplier Data Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-[0_1px_3px_rgba(0,0,0,0.04)] overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50/80 border-b border-slate-200 text-slate-400 text-[11px] uppercase tracking-wider font-bold">
                <th className="py-3.5 px-5">Supplier ID</th>
                <th className="py-3.5 px-5">Supplier Name</th>
                <th className="py-3.5 px-5">Region</th>
                <th className="py-3.5 px-5">Reliability Score</th>
                <th className="py-3.5 px-5">Status</th>
                <th className="py-3.5 px-5 text-right">Performance Band</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-xs">
              {loading ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center">
                    <LoadingSkeleton variant="table" rows={4} />
                  </td>
                </tr>
              ) : filteredSuppliers.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-12">
                    <EmptyState
                      title="No Suppliers Found"
                      description="No verified suppliers match your active search criteria."
                    />
                  </td>
                </tr>
              ) : (
                filteredSuppliers.map(sup => (
                  <tr key={sup.supplier_id} className="hover:bg-slate-50/90 transition-colors">
                    <td className="py-3.5 px-5 font-mono font-medium text-slate-900">{sup.supplier_id}</td>
                    <td className="py-3.5 px-5 font-bold text-slate-800">{sup.supplier_name}</td>
                    <td className="py-3.5 px-5 text-slate-600 flex items-center space-x-1.5 pt-4">
                      <MapPin className="w-3.5 h-3.5 text-slate-400" />
                      <span>{sup.region}</span>
                    </td>
                    <td className="py-3.5 px-5 font-extrabold text-emerald-600">
                      {(sup.reliability_score * 100).toFixed(0)}%
                    </td>
                    <td className="py-3.5 px-5">
                      <StatusBadge status={sup.is_active ? 'Active' : 'Inactive'} />
                    </td>
                    <td className="py-3.5 px-5 text-right font-semibold text-slate-700">
                      {sup.reliability_score >= 0.9 ? 'Tier 1 (Elite)' : sup.reliability_score >= 0.8 ? 'Tier 2 (Standard)' : 'Tier 3 (Monitored)'}
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
