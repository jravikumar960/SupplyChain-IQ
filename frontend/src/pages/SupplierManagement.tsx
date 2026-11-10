import React, { useEffect, useState } from 'react';
import { fetchSuppliers } from '../services/api';
import { Supplier } from '../types';
import { Truck, ShieldCheck, AlertCircle } from 'lucide-react';

export const SupplierManagement: React.FC = () => {
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSuppliers().then(data => {
      setSuppliers(data);
      setLoading(false);
    });
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-950 tracking-tight">Supplier Management</h1>
        <p className="text-slate-600 text-sm">Monitor global supplier reliability, capacity utilization, and delivery performance.</p>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 text-xs uppercase tracking-wider font-semibold">
                <th className="py-4 px-6">Supplier ID</th>
                <th className="py-4 px-6">Supplier Name</th>
                <th className="py-4 px-6">Region</th>
                <th className="py-4 px-6">Reliability Score</th>
                <th className="py-4 px-6">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-sm">
              {loading ? (
                <tr>
                  <td colSpan={5} className="text-center py-8 text-slate-500">Loading suppliers...</td>
                </tr>
              ) : suppliers.map(sup => (
                <tr key={sup.supplier_id} className="hover:bg-slate-50/80">
                  <td className="py-4 px-6 font-mono font-medium text-slate-900">{sup.supplier_id}</td>
                  <td className="py-4 px-6 font-semibold text-slate-800">{sup.supplier_name}</td>
                  <td className="py-4 px-6 text-slate-600">{sup.region}</td>
                  <td className="py-4 px-6 font-semibold text-emerald-600">{(sup.reliability_score * 100).toFixed(0)}%</td>
                  <td className="py-4 px-6">
                    <span className="px-2.5 py-1 bg-emerald-100 text-emerald-700 rounded-full text-xs font-semibold">
                      Active
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
