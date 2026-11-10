import React from 'react';
import {
  LayoutDashboard,
  AlertTriangle,
  ShieldCheck,
  Truck,
  Boxes,
  AlertOctagon,
  BarChart3,
  RefreshCw,
  Cpu
} from 'lucide-react';

interface SidebarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
  onRefreshData: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentTab, setCurrentTab, onRefreshData }) => {
  const navItems = [
    { id: 'executive', label: 'Executive Dashboard', icon: LayoutDashboard },
    { id: 'shortages', label: 'Shortage Management', icon: AlertTriangle },
    { id: 'mitigations', label: 'Mitigation Recommendations', icon: ShieldCheck },
    { id: 'suppliers', label: 'Supplier Management', icon: Truck },
    { id: 'inventory', label: 'Inventory & Demand', icon: Boxes },
    { id: 'exceptions', label: 'Exception Center', icon: AlertOctagon },
    { id: 'evaluation', label: 'Data Quality & Eval', icon: BarChart3 },
  ];

  return (
    <aside className="w-64 bg-slate-900 text-slate-100 flex flex-col h-screen fixed left-0 top-0 border-r border-slate-800">
      <div className="p-6 border-b border-slate-800 flex items-center space-x-3">
        <div className="bg-blue-600 p-2 rounded-lg text-white">
          <Cpu className="w-6 h-6" />
        </div>
        <div>
          <h1 className="font-bold text-lg tracking-wide">SupplyChain IQ</h1>
          <p className="text-xs text-slate-400">Demand & Inventory Optimization</p>
        </div>
      </div>

      <nav className="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setCurrentTab(item.id)}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl font-medium text-sm transition-all ${
                isActive
                  ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30'
                  : 'text-slate-300 hover:bg-slate-800 hover:text-white'
              }`}
            >
              <Icon className="w-5 h-5" />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="p-4 border-t border-slate-800">
        <button
          onClick={onRefreshData}
          className="w-full flex items-center justify-center space-x-2 bg-slate-800 hover:bg-slate-700 text-slate-200 py-2.5 px-4 rounded-xl text-sm font-medium transition-colors border border-slate-700"
        >
          <RefreshCw className="w-4 h-4" />
          <span>Regenerate & Run Engine</span>
        </button>
        <div className="mt-3 text-center text-xs text-slate-500">
          Hackathon MVP v1.0 • 100% Deterministic
        </div>
      </div>
    </aside>
  );
};
