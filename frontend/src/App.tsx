import React, { useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { ExecutiveDashboard } from './pages/ExecutiveDashboard';
import { ShortageManagement } from './pages/ShortageManagement';
import { MitigationRecommendations } from './pages/MitigationRecommendations';
import { SupplierManagement } from './pages/SupplierManagement';
import { InventoryPlanning } from './pages/InventoryPlanning';
import { ExceptionCenter } from './pages/ExceptionCenter';
import { DataQualityEvaluation } from './pages/DataQualityEvaluation';
import { generateData } from './services/api';

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
          {currentTab === 'executive' && <ExecutiveDashboard />}
          {currentTab === 'shortages' && <ShortageManagement onSelectShortage={handleSelectShortage} />}
          {currentTab === 'mitigations' && <MitigationRecommendations selectedShortageId={selectedShortageId} />}
          {currentTab === 'suppliers' && <SupplierManagement />}
          {currentTab === 'inventory' && <InventoryPlanning />}
          {currentTab === 'exceptions' && <ExceptionCenter />}
          {currentTab === 'evaluation' && <DataQualityEvaluation />}
        </div>
      </main>
    </div>
  );
}

export default App;
