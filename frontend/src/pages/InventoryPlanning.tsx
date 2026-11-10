import React, { useEffect, useState } from 'react';
import { fetchInventory } from '../services/api';
import { Boxes } from 'lucide-react';

export const InventoryPlanning: React.FC = () => {
  const [inventory, setInventory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchInventory().then(data => {
      setInventory(data);
      setLoading(false);
    });
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-950 tracking-tight">Inventory & Demand Planning</h1>
        <p className="text-slate-600 text-sm">Track on-hand stock, safety stock buffers, and inventory reserves across facilities.</p>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 text-xs uppercase tracking-wider font-semibold">
                <th className="py-4 px-6">Inventory ID</th>
                <th className="py-4 px-6">SKU ID</th>
                <th className="py-4 px-6">Location ID</th>
                <th className="py-4 px-6">On-Hand Qty</th>
                <th className="py-4 px-6">Reserved Qty</th>
                <th className="py-4 px-6">Safety Stock</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-sm">
              {loading ? (
                <tr>
                  <td colSpan={6} className="text-center py-8 text-slate-500">Loading inventory...</td>
                </tr>
              ) : inventory.slice(0, 50).map(inv => (
                <tr key={inv.inventory_id} className="hover:bg-slate-50/80">
                  <td className="py-4 px-6 font-mono font-medium text-slate-900">{inv.inventory_id}</td>
                  <td className="py-4 px-6 font-mono text-blue-600">{inv.sku_id}</td>
                  <td className="py-4 px-6 font-mono text-slate-600">{inv.location_id}</td>
                  <td className="py-4 px-6 font-semibold text-slate-900">{inv.on_hand_quantity}</td>
                  <td className="py-4 px-6 text-slate-600">{inv.reserved_quantity}</td>
                  <td className="py-4 px-6 text-slate-600">{inv.safety_stock}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
