import React, { useRef, useEffect } from 'react';

const AGENT_COLORS = {
  vehicle: '#3b82f6',
  human: '#22c55e',
  machine: '#f59e0b',
  energy: '#ef4444',
  default: '#a78bfa',
};

const ZONE_COLORS = {
  residential: 'rgba(34, 197, 94, 0.12)',
  industrial: 'rgba(245, 158, 11, 0.12)',
  commercial: 'rgba(59, 130, 246, 0.12)',
  road: 'rgba(100, 116, 139, 0.25)',
  park: 'rgba(16, 185, 129, 0.12)',
  power_plant: 'rgba(239, 68, 68, 0.12)',
  water_treatment: 'rgba(56, 189, 248, 0.12)',
  warehouse: 'rgba(249, 115, 22, 0.12)',
};

const GRID_W = 50;
const GRID_H = 50;

const SimulationCanvas = ({ state }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);

    const w = rect.width;
    const h = rect.height;
    const cellW = w / GRID_W;
    const cellH = h / GRID_H;

    // Background
    ctx.fillStyle = '#0a0a1a';
    ctx.fillRect(0, 0, w, h);

    // Grid lines
    ctx.strokeStyle = '#1a1a3a';
    ctx.lineWidth = 0.5;
    for (let x = 0; x <= GRID_W; x++) {
      ctx.beginPath();
      ctx.moveTo(x * cellW, 0);
      ctx.lineTo(x * cellW, h);
      ctx.stroke();
    }
    for (let y = 0; y <= GRID_H; y++) {
      ctx.beginPath();
      ctx.moveTo(0, y * cellH);
      ctx.lineTo(w, y * cellH);
      ctx.stroke();
    }

    // Draw demo zones
    const demoZones = [
      { type: 'residential', x1: 0, y1: 0, x2: 15, y2: 15 },
      { type: 'commercial', x1: 15, y1: 0, x2: 35, y2: 15 },
      { type: 'industrial', x1: 35, y1: 0, x2: 50, y2: 15 },
      { type: 'road', x1: 0, y1: 15, x2: 50, y2: 22 },
      { type: 'park', x1: 0, y1: 35, x2: 25, y2: 50 },
      { type: 'power_plant', x1: 25, y1: 35, x2: 50, y2: 50 },
    ];

    demoZones.forEach((z) => {
      ctx.fillStyle = ZONE_COLORS[z.type] || 'rgba(100,100,100,0.1)';
      ctx.fillRect(z.x1 * cellW, z.y1 * cellH, (z.x2 - z.x1) * cellW, (z.y2 - z.y1) * cellH);
      // Zone label
      ctx.fillStyle = 'rgba(255,255,255,0.25)';
      ctx.font = '10px monospace';
      ctx.textAlign = 'center';
      ctx.fillText(
        z.type.replace('_', ' '),
        (z.x1 + z.x2) / 2 * cellW,
        (z.y1 + z.y2) / 2 * cellH + 4
      );
    });

    // Draw agents
    if (state?.agents) {
      state.agents.forEach((agent) => {
        const color = AGENT_COLORS[agent.type] || AGENT_COLORS.default;
        const cx = agent.x * cellW + cellW / 2;
        const cy = agent.y * cellH + cellH / 2;
        const r = Math.min(cellW, cellH) * 0.35;

        // Glow
        ctx.shadowBlur = 6;
        ctx.shadowColor = color;
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(cx, cy, r, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0;
      });
    }

    // Empty state message
    if (!state?.agents) {
      ctx.fillStyle = 'rgba(255,255,255,0.15)';
      ctx.font = '16px monospace';
      ctx.textAlign = 'center';
      ctx.fillText('Select a scenario and press Play', w / 2, h / 2);
      ctx.fillText('to start the simulation', w / 2, h / 2 + 24);
    }

  }, [state]);

  return (
    <div className="canvas-container">
      <canvas ref={canvasRef} className="simulation-canvas" />
      {state?.agents && (
        <div className="canvas-overlay">
          <span>{state.agents.length} agents</span>
        </div>
      )}
    </div>
  );
};

export default SimulationCanvas;
