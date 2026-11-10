import React, { useEffect, useState } from 'react';
import { fetchInventory } from '../services/api';
import { Boxes, Search, Layers, ShieldCheck, AlertTriangle } from 'lucide-react';
import { StatusBadge } from '../components/StatusBadge';
import { KPICard } from '../components/KPICard';
import { LoadingSkeleton } from '../components/LoadingSkeleton';
import { EmptyState } from '../components/EmptyState';

export const InventoryPlanning: React.FC = () => {
  const [inventory, setInventory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchInventory().then(data => {
      setInventory(data);
      setLoading(false);
    });
  }, []);

  const filteredInventory = inventory.filter(inv =>
    inv.sku_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    inv.location_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    inv.inventory_id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalOnHand = inventory.reduce((acc, inv) => acc + (inv.on_hand_quantity || 0), 0);
  const totalReserved = inventory.reduce((acc, inv) => acc + (inv.reserved_quantity || 0), 0);
  const totalSafetyStock = inventory.reduce((acc, inv) => acc + (inv.safety_stock || 0), 0);

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Inventory & Demand Planning Workbench</h1>
            <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
              {inventory.length} SKUs Monitored
            </span>
          </div>
          <p className="text-slate-500 text-xs mt-1">Multi-echelon stock levels, safety stock buffers, and allocation tracking.</p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search SKU ID, location, inventory ID..."
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              className="pl-9 pr-4 py-2 bg-white border border-slate-200 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-blue-600 shadow-2xs w-72 text-slate-800 transition-all"
            />
          </div>
        </div>
      </div>

      {/* KPI Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        <KPICard
          title="Total On-Hand Stock"
          value={`${(totalOnHand / 1000).toFixed(1)}k`}
          subtitle="Units across all nodes"
          icon={Boxes}
          iconColor="blue"
        />
        <KPICard
          title="Reserved Quantity"
          value={`${(totalReserved / 1000).toFixed(1)}k`}
          subtitle="Allocated to active orders"
          icon={Layers}
          iconColor="indigo"
        />
        <KPICard
          title="Safety Stock Buffers"
          value={`${(totalSafetyStock / 1000).toFixed(1)}k`}
          subtitle="Minimum safety threshold"
          badge={{ text: 'Protected', variant: 'positive' }}
          icon={ShieldCheck}
          iconColor="emerald"
        />
      </div>

      {/* Inventory Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-[0_1px_3px_rgba(0,0,0,0.04)] overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50/80 border-b border-slate-200 text-slate-400 text-[11px] uppercase tracking-wider font-bold">
                <th className="py-3.5 px-5">Inventory ID</th>
                <th className="py-3.5 px-5">SKU ID</th>
                <th className="py-3.5 px-5">Location ID</th>
                <th className="py-3.5 px-5">On-Hand Qty</th>
                <th className="py-3.5 px-5">Reserved Qty</th>
                <th className="py-3.5 px-5">Safety Stock</th>
                <th className="py-3.5 px-5 text-right">Buffer Health</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-xs">
              {loading ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center">
                    <LoadingSkeleton variant="table" rows={5} />
                  </td>
                </tr>
              ) : filteredInventory.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-12">
                    <EmptyState
                      title="No Inventory Records Found"
                      description="No inventory matches your active search query."
                    />
                  </td>
                </tr>
              ) : (
                filteredInventory.slice(0, 100).map(inv => {
                  const isHealthy = inv.on_hand_quantity >= inv.safety_stock;
                  return (
                    <tr key={inv.inventory_id} className="hover:bg-slate-50/90 transition-colors">
                      <td className="py-3.5 px-5 font-mono font-medium text-slate-900">{inv.inventory_id}</td>
                      <td className="py-3.5 px-5 font-mono font-bold text-blue-600">{inv.sku_id}</td>
                      <td className="py-3.5 px-5 font-mono text-slate-600">{inv.location_id}</td>
                      <td className="py-3.5 px-5 font-bold text-slate-900">{inv.on_hand_quantity.toLocaleString()}</td>
                      <td className="py-3.5 px-5 text-slate-600">{inv.reserved_quantity.toLocaleString()}</td>
                      <td className="py-3.5 px-5 text-slate-600">{inv.safety_stock.toLocaleString()}</td>
                      <td className="py-3.5 px-5 text-right">
                        <StatusBadge status={isHealthy ? 'Feasible' : 'Critical'} />
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
