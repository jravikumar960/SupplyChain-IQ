import React, { useState } from 'react';
import {
  Search,
  Bell,
  RefreshCw,
  Database,
  CheckCircle2,
  Command,
  Sparkles,
  ExternalLink,
  ChevronRight
} from 'lucide-react';
import { runEngine, generateData } from '../services/api';

interface HeaderProps {
  currentPath: string;
  onRefreshData?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ currentPath, onRefreshData }) => {
  const [isSearching, setIsSearching] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [isRunningEngine, setIsRunningEngine] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [notificationOpen, setNotificationOpen] = useState(false);

  const formatBreadcrumb = (path: string) => {
    if (path === '/' || !path) return 'Executive Dashboard';
    const cleaned = path.replace('/', '');
    return cleaned
      .split('-')
      .map(w => w.charAt(0).toUpperCase() + w.slice(1))
      .join(' ');
  };

  const handleRunEngine = async () => {
    try {
      setIsRunningEngine(true);
      await runEngine();
      if (onRefreshData) onRefreshData();
    } catch (err) {
      console.error('Failed to run engine:', err);
    } finally {
      setIsRunningEngine(false);
    }
  };

  const handleGenerateData = async () => {
    try {
      setIsGenerating(true);
      await generateData();
      if (onRefreshData) onRefreshData();
    } catch (err) {
      console.error('Failed to generate data:', err);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <header className="h-16 bg-white border-b border-slate-200/90 sticky top-0 z-30 px-6 flex items-center justify-between shadow-xs">
      {/* Left: Breadcrumbs & Context */}
      <div className="flex items-center space-x-3">
        <div className="flex items-center space-x-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">
          <span>SupplyChain IQ</span>
          <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
          <span className="text-slate-900 font-bold">{formatBreadcrumb(currentPath)}</span>
        </div>
        <div className="hidden md:flex items-center space-x-1.5 ml-4 px-2.5 py-1 bg-emerald-50 border border-emerald-200/60 rounded-full text-xs font-medium text-emerald-700">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span>Engine Deterministic (Phases 1-4)</span>
        </div>
      </div>

      {/* Center/Right: Search, Actions, Notifications */}
      <div className="flex items-center space-x-3">
        {/* Search Bar */}
        <div className="relative hidden lg:block w-72">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
            <Search className="w-4 h-4" />
          </div>
          <input
            type="text"
            placeholder="Search SKUs, suppliers, locations... (Ctrl+K)"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-10 py-1.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
          />
          <div className="absolute inset-y-0 right-0 pr-2.5 flex items-center pointer-events-none">
            <kbd className="px-1.5 py-0.5 text-[10px] font-semibold text-slate-400 bg-white border border-slate-200 rounded shadow-xs">
              ⌘K
            </kbd>
          </div>
        </div>

        {/* Regenerate Data */}
        <button
          onClick={handleGenerateData}
          disabled={isGenerating}
          title="Reset & Regenerate Database"
          className="p-2 text-slate-600 hover:text-slate-900 bg-slate-50 hover:bg-slate-100 border border-slate-200/80 rounded-xl transition-colors flex items-center space-x-1 text-xs font-medium disabled:opacity-50"
        >
          <Database className={`w-4 h-4 text-slate-500 ${isGenerating ? 'animate-spin' : ''}`} />
          <span className="hidden sm:inline">Seed Data</span>
        </button>

        {/* Run Engine */}
        <button
          onClick={handleRunEngine}
          disabled={isRunningEngine}
          className="inline-flex items-center space-x-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-semibold shadow-xs hover:shadow transition-all disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isRunningEngine ? 'animate-spin' : ''}`} />
          <span>Run Optimization</span>
        </button>

        {/* Notifications */}
        <div className="relative">
          <button
            onClick={() => setNotificationOpen(!notificationOpen)}
            className="p-2 text-slate-600 hover:text-slate-900 bg-slate-50 hover:bg-slate-100 border border-slate-200/80 rounded-xl transition-colors relative"
          >
            <Bell className="w-4 h-4 text-slate-500" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-rose-500" />
          </button>

          {notificationOpen && (
            <div className="absolute right-0 mt-2 w-80 bg-white rounded-2xl border border-slate-200 shadow-xl py-3 z-50">
              <div className="px-4 pb-2 border-b border-slate-100 flex items-center justify-between">
                <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider">System Notifications</h4>
                <span className="text-[10px] font-semibold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full">3 New</span>
              </div>
              <div className="divide-y divide-slate-50 max-h-72 overflow-y-auto">
                <div className="px-4 py-3 hover:bg-slate-50/80 transition-colors cursor-pointer">
                  <div className="flex items-start space-x-3">
                    <div className="w-2 h-2 mt-1.5 rounded-full bg-rose-500 shrink-0" />
                    <div>
                      <p className="text-xs font-semibold text-slate-900">Critical Shortage Detected</p>
                      <p className="text-[11px] text-slate-500">SHORT-SKU-000093-LOC-000006-2026-W12 requires immediate review.</p>
                      <span className="text-[10px] text-slate-400 mt-1 block">10 mins ago</span>
                    </div>
                  </div>
                </div>
                <div className="px-4 py-3 hover:bg-slate-50/80 transition-colors cursor-pointer">
                  <div className="flex items-start space-x-3">
                    <div className="w-2 h-2 mt-1.5 rounded-full bg-emerald-500 shrink-0" />
                    <div>
                      <p className="text-xs font-semibold text-slate-900">Mitigation Approved</p>
                      <p className="text-[11px] text-slate-500">Supplier PO for SKU-000012 successfully generated.</p>
                      <span className="text-[10px] text-slate-400 mt-1 block">1 hour ago</span>
                    </div>
                  </div>
                </div>
                <div className="px-4 py-3 hover:bg-slate-50/80 transition-colors cursor-pointer">
                  <div className="flex items-start space-x-3">
                    <div className="w-2 h-2 mt-1.5 rounded-full bg-blue-500 shrink-0" />
                    <div>
                      <p className="text-xs font-semibold text-slate-900">Scenario Simulation Complete</p>
                      <p className="text-[11px] text-slate-500">Q2 Demand Spike +25% simulation run finished successfully.</p>
                      <span className="text-[10px] text-slate-400 mt-1 block">3 hours ago</span>
                    </div>
                  </div>
                </div>
              </div>
              <div className="px-4 pt-2 border-t border-slate-100 text-center">
                <button
                  onClick={() => setNotificationOpen(false)}
                  className="text-xs font-semibold text-blue-600 hover:text-blue-700"
                >
                  Close notifications
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
