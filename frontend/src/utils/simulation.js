export const AGENT_COLORS = {
  vehicle: '#3b82f6',
  human: '#22c55e',
  machine: '#f59e0b',
  energy: '#ef4444',
  default: '#a78bfa',
};

export const ZONE_COLORS = {
  residential: 'rgba(34, 197, 94, 0.15)',
  industrial: 'rgba(245, 158, 11, 0.15)',
  commercial: 'rgba(59, 130, 246, 0.15)',
  road: 'rgba(107, 114, 128, 0.3)',
  park: 'rgba(16, 185, 129, 0.15)',
  power_plant: 'rgba(239, 68, 68, 0.15)',
  water_treatment: 'rgba(59, 130, 246, 0.15)',
  warehouse: 'rgba(249, 115, 22, 0.15)',
};

export const gridToCanvas = (x, y, cellSize, offsetX = 0, offsetY = 0) => ({
  cx: x * cellSize + offsetX,
  cy: y * cellSize + offsetY,
});

export const getAgentColor = (type) => AGENT_COLORS[type] || AGENT_COLORS.default;

// Generate demo state when backend isn't available
export const generateDemoState = (tick, gridW = 50, gridH = 50) => {
  const rng = (seed) => {
    let s = seed;
    return () => { s = (s * 16807) % 2147483647; return s / 2147483647; };
  };
  const rand = rng(tick * 137 + 42);

  const types = ['vehicle', 'human', 'machine', 'energy'];
  const weights = [0.3, 0.4, 0.15, 0.15];

  const numAgents = 40;
  const agents = Array.from({ length: numAgents }, (_, i) => {
    let r = rand(), cumulative = 0, type = 'human';
    for (let j = 0; j < types.length; j++) {
      cumulative += weights[j];
      if (r <= cumulative) { type = types[j]; break; }
    }
    return {
      id: i,
      type,
      x: Math.floor(rand() * gridW),
      y: Math.floor(rand() * gridH),
      color: getAgentColor(type),
      health: 0.3 + rand() * 0.7,
      energy: 0.2 + rand() * 0.8,
    };
  });

  return { agents, gridWidth: gridW, gridHeight: gridH, tick };
};

export const generateDemoMetrics = (currentTick) => {
  const points = [];
  for (let i = Math.max(0, currentTick - 50); i <= currentTick; i++) {
    const t = i / 100;
    points.push({
      tick: i,
      energy: 500 + 200 * Math.sin(t * Math.PI * 2) + (Math.random() - 0.5) * 50,
      efficiency: 0.7 + 0.15 * Math.cos(t * Math.PI * 1.5) + (Math.random() - 0.5) * 0.05,
      throughput: 4 + 2 * Math.sin(t * Math.PI * 3) + (Math.random() - 0.5),
      stability: 0.85 + 0.1 * Math.sin(t * Math.PI) + (Math.random() - 0.5) * 0.03,
    });
  }
  return points;
};
