const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const handleResponse = async (res) => {
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `API error ${res.status}`);
  }
  return res.json();
};

export const startSimulation = async (scenarioId) => {
  const res = await fetch(`${API_BASE}/simulations/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scenario: scenarioId }),
  });
  return handleResponse(res);
};

export const getStatus = async (simId) => {
  const res = await fetch(`${API_BASE}/simulations/${simId}`);
  return handleResponse(res);
};

export const getResults = async (simId) => {
  const res = await fetch(`${API_BASE}/simulations/${simId}/results`);
  return handleResponse(res);
};

export const getMetrics = async (simId) => {
  const res = await fetch(`${API_BASE}/simulations/${simId}/metrics`);
  return handleResponse(res);
};

export const listSimulations = async () => {
  const res = await fetch(`${API_BASE}/simulations`);
  return handleResponse(res);
};
