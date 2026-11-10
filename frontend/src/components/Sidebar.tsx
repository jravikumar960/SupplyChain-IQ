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
  Cpu,
  Sliders,
  ChevronRight,
  ShieldAlert
} from 'lucide-react';

interface SidebarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
  onRefreshData: () => void;
  refreshing?: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentTab, setCurrentTab, onRefreshData, refreshing = false }) => {
  const sections = [
    {
      group: 'CORE OPERATIONS',
      items: [
        { id: 'executive', label: 'Executive Dashboard', icon: LayoutDashboard },
        { id: 'shortages', label: 'Shortage Management', icon: AlertTriangle, badge: 'Active' },
        { id: 'mitigations', label: 'Mitigation Engine', icon: ShieldCheck },
      ]
    },
    {
      group: 'SUPPLY NETWORK',
      items: [
        { id: 'inventory', label: 'Inventory & Demand', icon: Boxes },
        { id: 'suppliers', label: 'Supplier Reliability', icon: Truck },
      ]
    },
    {
      group: 'OPTIMIZATION ENGINE',
      items: [
        { id: 'simulation', label: 'Scenario Simulation', icon: Sliders, badge: 'What-If' },
      ]
    },
    {
      group: 'AUDIT & GOVERNANCE',
      items: [
        { id: 'exceptions', label: 'Exception Center', icon: AlertOctagon },
        { id: 'evaluation', label: 'Model Evaluation', icon: BarChart3 },
      ]
    }
  ];

  return (
    <aside className="w-64 bg-slate-950 text-slate-100 flex flex-col h-screen fixed left-0 top-0 border-r border-slate-800/80 z-30 select-none">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800/80 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="bg-gradient-to-tr from-blue-700 to-indigo-600 p-2.5 rounded-xl text-white shadow-lg shadow-blue-500/20">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-1.5">
              <h1 className="font-extrabold text-base tracking-tight text-white">SupplyChain IQ</h1>
              <span className="text-[10px] font-bold bg-blue-500/20 text-blue-400 px-1.5 py-0.5 rounded border border-blue-500/30">PRO</span>
            </div>
            <p className="text-[11px] text-slate-400 font-medium">Enterprise Decision Cloud</p>
          </div>
        </div>
      </div>

      {/* Navigation Groups */}
      <nav className="flex-1 px-3 py-4 space-y-5 overflow-y-auto dark-scrollbar">
        {sections.map((sec, sIdx) => (
          <div key={sIdx} className="space-y-1">
            <div className="px-3 text-[10px] font-bold uppercase tracking-wider text-slate-400">
              {sec.group}
            </div>
            {sec.items.map((item) => {
              const Icon = item.icon;
              const isActive = currentTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setCurrentTab(item.id)}
                  className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl font-medium text-xs transition-all group ${
                    isActive
                      ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30 font-semibold'
                      : 'text-slate-300 hover:bg-slate-900/90 hover:text-white'
                  }`}
                >
                  <div className="flex items-center space-x-2.5">
                    <Icon className={`w-4 h-4 transition-transform group-hover:scale-110 ${
                      isActive ? 'text-white' : 'text-slate-400 group-hover:text-slate-200'
                    }`} />
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span className={`text-[10px] px-1.5 py-0.5 rounded-md font-bold ${
                      isActive
                        ? 'bg-blue-700 text-blue-100'
                        : item.badge === 'Active'
                          ? 'bg-red-500/20 text-red-300 border border-red-500/30'
                          : 'bg-slate-800 text-slate-300'
                    }`}>
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        ))}
      </nav>

      {/* Footer & Controls */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-950/80 space-y-3">
        <button
          onClick={onRefreshData}
          disabled={refreshing}
          className="w-full flex items-center justify-center space-x-2 bg-slate-900 hover:bg-slate-800 text-slate-200 hover:text-white py-2 px-3 rounded-xl text-xs font-semibold transition-all border border-slate-800 disabled:opacity-50 shadow-sm"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin text-blue-400' : 'text-slate-400'}`} />
          <span>{refreshing ? 'Executing Engine...' : 'Run Optimization Engine'}</span>
        </button>

        {/* User Card */}
        <div className="flex items-center space-x-3 pt-2 border-t border-slate-800/60 px-1">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-white text-xs font-bold ring-2 ring-slate-800 shadow">
            SC
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-semibold text-slate-200 truncate">Supply Chain Controller</p>
            <p className="text-[10px] text-emerald-400 flex items-center space-x-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>100% Deterministic</span>
            </p>
          </div>
        </div>
      </div>
    </aside>
  );
};
