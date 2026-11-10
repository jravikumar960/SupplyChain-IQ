import React, { useState, lazy, Suspense } from 'react';
import { Sidebar } from './components/Sidebar';
import { generateData } from './services/api';

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

  return (
    <div className="min-h-screen bg-slate-50 flex">
      <Sidebar
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        onRefreshData={handleRefreshData}
      />
      <main className="flex-1 ml-64 p-8 overflow-y-auto min-h-screen">
        <div className="max-w-7xl mx-auto">
          <Suspense fallback={
            <div className="flex items-center justify-center h-96 text-slate-500 font-medium">
              Loading module...
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
  );
}

export default App;
