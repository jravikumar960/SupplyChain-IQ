const API_BASE = '/api';

export async function fetchSummary() {
  const res = await fetch(`${API_BASE}/dashboard/summary`);
  return res.json();
}

export async function fetchCharts() {
  const res = await fetch(`${API_BASE}/dashboard/charts`);
  return res.json();
}

export async function fetchShortages(severity?: string, status?: string) {
  let url = `${API_BASE}/shortages`;
  const params = new URLSearchParams();
  if (severity && severity !== 'ALL') params.append('severity', severity);
  if (status && status !== 'ALL') params.append('status', status);
  if (params.toString()) url += `?${params.toString()}`;
  const res = await fetch(url);
  return res.json();
}

export async function fetchShortageMitigations(shortageId: string) {
  const res = await fetch(`${API_BASE}/shortages/${shortageId}/mitigations`);
  return res.json();
}

export async function approveMitigation(mitigationId: string) {
  const res = await fetch(`${API_BASE}/mitigations/${mitigationId}/approve`, { method: 'POST' });
  return res.json();
}

export async function rejectMitigation(mitigationId: string) {
  const res = await fetch(`${API_BASE}/mitigations/${mitigationId}/reject`, { method: 'POST' });
  return res.json();
}

export async function fetchSuppliers() {
  const res = await fetch(`${API_BASE}/suppliers`);
  return res.json();
}

export async function fetchInventory() {
  const res = await fetch(`${API_BASE}/inventory`);
  return res.json();
}

export async function fetchExceptions() {
  const res = await fetch(`${API_BASE}/exceptions`);
  return res.json();
}

export async function fetchAuditLogs() {
  const res = await fetch(`${API_BASE}/audit-logs`);
  return res.json();
}

export async function fetchEvaluationMetrics() {
  const res = await fetch(`${API_BASE}/evaluation/metrics`);
  return res.json();
}

export async function runEngine() {
  const res = await fetch(`${API_BASE}/engine/run`, { method: 'POST' });
  return res.json();
}

export async function generateData() {
  const res = await fetch(`${API_BASE}/data/generate`, { method: 'POST' });
  return res.json();
}

export async function runSimulation(runName: string, demandMultiplier: number, capacityMultiplier: number, delayDays: number) {
  const params = new URLSearchParams({
    run_name: runName,
    demand_multiplier: demandMultiplier.toString(),
    supplier_capacity_multiplier: capacityMultiplier.toString(),
    lead_time_delay_days: delayDays.toString(),
  });
  const res = await fetch(`${API_BASE}/simulation/run?${params.toString()}`, { method: 'POST' });
  return res.json();
}

export async function fetchSimulationHistory() {
  const res = await fetch(`${API_BASE}/simulation/history`);
  return res.json();
}
