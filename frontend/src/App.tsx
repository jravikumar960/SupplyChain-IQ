import React, { useState, lazy, Suspense } from 'react';
import { Sidebar } from './components/Sidebar';
import { generateData } from './services/api';
import { Search, Bell, ChevronRight, Sliders, ShieldCheck, RefreshCw } from 'lucide-react';

const ExecutiveDashboard = lazy(() => import('./pages/ExecutiveDashboard').then(m => ({ default: m.ExecutiveDashboard })));
const ShortageManagement = lazy(() => import('./pages/ShortageManagement').then(m => ({ default: m.ShortageManagement })));
const MitigationRecommendations = lazy(() => import('./pages/MitigationRecommendations').then(m => ({ default: m.MitigationRecommendations })));
const SupplierManagement = lazy(() => import('./pages/SupplierManagement').then(m => ({ default: m.SupplierManagement })));
const InventoryPlanning = lazy(() => import('./pages/InventoryPlanning').then(m => ({ default: m.InventoryPlanning })));
const ScenarioSimulation = lazy(() => import('./pages/ScenarioSimulation').then(m => ({ default: m.ScenarioSimulation })));
const ExceptionCenter = lazy(() => import('./pages/ExceptionCenter').then(m => ({ default: m.ExceptionCenter })));
const DataQualityEvaluation = lazy(() => import('./pages/DataQualityEvaluation').then(m => ({ default: m.DataQualityEvaluation })));

export function App() {
  const [currentTab, setCurrentTab] = useState('executive');
  const [selectedShortageId, setSelectedShortageId] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const tabLabels: Record<string, { group: string; name: string }> = {
    executive: { group: 'Operations', name: 'Executive Dashboard' },
    shortages: { group: 'Operations', name: 'Shortage Management' },
    mitigations: { group: 'Decision Engine', name: 'Mitigation Recommendations' },
    suppliers: { group: 'Supply Network', name: 'Supplier Management' },
    inventory: { group: 'Supply Network', name: 'Inventory & Demand Planning' },
    simulation: { group: 'What-If Analysis', name: 'Scenario Simulation' },
    exceptions: { group: 'Governance', name: 'Exception Center' },
    evaluation: { group: 'Governance', name: 'Data Quality & Model Evaluation' },
  };

  const handleRefreshData = async () => {
    if (confirm("Regenerate synthetic dataset and run optimization engine?")) {
      setRefreshing(true);
      try {
        await generateData();
        window.location.reload();
      } catch (err) {
        alert("Failed to regenerate data");
        setRefreshing(false);
      }
    }
  };

  const handleSelectShortage = (shortageId: string) => {
    setSelectedShortageId(shortageId);
    setCurrentTab('mitigations');
  };

  const currentMeta = tabLabels[currentTab] || { group: 'Operations', name: 'Dashboard' };

  return (
    <div className="min-h-screen bg-slate-900 flex font-sans">
      <Sidebar
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        onRefreshData={handleRefreshData}
        refreshing={refreshing}
      />

      <div className="flex-1 ml-64 flex flex-col min-h-screen bg-slate-50/90 overflow-hidden">
        {/* Enterprise Top Navigation Bar */}
        <header className="h-16 bg-white border-b border-slate-200/80 px-8 flex items-center justify-between sticky top-0 z-20 shadow-[0_1px_2px_rgba(0,0,0,0.03)]">
          {/* Breadcrumb Navigation */}
          <div className="flex items-center space-x-2 text-xs">
            <span className="font-semibold text-slate-400">SupplyChain IQ</span>
            <ChevronRight className="w-3.5 h-3.5 text-slate-300" />
            <span className="font-medium text-slate-500">{currentMeta.group}</span>
            <ChevronRight className="w-3.5 h-3.5 text-slate-300" />
            <span className="font-bold text-slate-800">{currentMeta.name}</span>
          </div>

          {/* Quick Actions & Search */}
          <div className="flex items-center space-x-4">
            <div className="relative hidden md:block">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Search SKUs, POs, locations..."
                className="pl-8 pr-12 py-1.5 bg-slate-100/80 border border-slate-200 rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-blue-600 focus:bg-white text-slate-800 w-64 transition-all"
                readOnly
                onClick={() => {
                  if (currentTab !== 'shortages') setCurrentTab('shortages');
                }}
              />
              <kbd className="absolute right-2.5 top-2 text-[10px] bg-white border border-slate-200 text-slate-400 px-1 rounded font-mono shadow-xs">
                ⌘K
              </kbd>
            </div>

            {/* Deterministic Engine Status */}
            <div className="hidden lg:flex items-center space-x-1.5 px-3 py-1 bg-emerald-50 border border-emerald-200/80 rounded-full text-[11px] font-semibold text-emerald-700">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span>Engine: Synchronized</span>
            </div>

            {/* Notification Bell */}
            <button
              onClick={() => setCurrentTab('exceptions')}
              className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors relative"
              title="View Anomaly Exceptions"
            >
              <Bell className="w-4 h-4" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full ring-2 ring-white"></span>
            </button>

            {/* User Profile Avatar */}
            <div className="flex items-center space-x-2 pl-2 border-l border-slate-200">
              <div className="w-7 h-7 rounded-full bg-blue-600 text-white font-bold text-xs flex items-center justify-center shadow-xs">
                SC
              </div>
              <span className="text-xs font-semibold text-slate-700 hidden sm:inline-block">Controller</span>
            </div>
          </div>
        </header>

        {/* Main Content Area */}
        <main className="flex-1 p-8 overflow-y-auto">
          <div className="max-w-7xl mx-auto pb-12">
            <Suspense fallback={
              <div className="flex flex-col items-center justify-center h-96 space-y-3">
                <div className="w-8 h-8 border-3 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                <p className="text-slate-500 font-medium text-xs">Loading analytics module...</p>
              </div>
            }>
              {currentTab === 'executive' && <ExecutiveDashboard />}
              {currentTab === 'shortages' && <ShortageManagement onSelectShortage={handleSelectShortage} />}
              {currentTab === 'mitigations' && <MitigationRecommendations selectedShortageId={selectedShortageId} />}
              {currentTab === 'suppliers' && <SupplierManagement />}
              {currentTab === 'inventory' && <InventoryPlanning />}
              {currentTab === 'simulation' && <ScenarioSimulation />}
              {currentTab === 'exceptions' && <ExceptionCenter />}
              {currentTab === 'evaluation' && <DataQualityEvaluation />}
            </Suspense>
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
