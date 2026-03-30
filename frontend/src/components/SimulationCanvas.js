import React, { useRef, useEffect } from 'react';

const SimulationCanvas = ({ state, cellSize = 12 }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !state) return;

    const ctx = canvas.getContext('2d');
    const { gridWidth, gridHeight, agents, resources } = state;

    canvas.width = gridWidth * cellSize;
    canvas.height = gridHeight * cellSize;

    // Background
    ctx.fillStyle = '#0a0a1a';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Grid lines
    ctx.strokeStyle = '#1a1a3a';
    ctx.lineWidth = 0.5;
    for (let x = 0; x <= gridWidth; x++) {
      ctx.beginPath();
      ctx.moveTo(x * cellSize, 0);
      ctx.lineTo(x * cellSize, canvas.height);
      ctx.stroke();
    }
    for (let y = 0; y <= gridHeight; y++) {
      ctx.beginPath();
      ctx.moveTo(0, y * cellSize);
      ctx.lineTo(canvas.width, y * cellSize);
      ctx.stroke();
    }

    // Resources
    (resources || []).forEach((r) => {
      const cx = r.x * cellSize + cellSize / 2;
      const cy = r.y * cellSize + cellSize / 2;
      const radius = Math.max(1, (cellSize / 3) * r.amount);
      ctx.globalAlpha = 0.3 + r.amount * 0.4;
      ctx.fillStyle = r.color;
      ctx.fillRect(r.x * cellSize + 1, r.y * cellSize + 1, cellSize - 2, cellSize - 2);
    });
    ctx.globalAlpha = 1;

    // Agents
    (agents || []).forEach((a) => {
      const cx = a.x * cellSize + cellSize / 2;
      const cy = a.y * cellSize + cellSize / 2;
      const radius = Math.max(2, cellSize / 2.5);

      // Glow
      const gradient = ctx.createRadialGradient(cx, cy, 0, cx, cy, radius * 2);
      gradient.addColorStop(0, a.color + '60');
      gradient.addColorStop(1, 'transparent');
      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(cx, cy, radius * 2, 0, Math.PI * 2);
      ctx.fill();

      // Agent body
      ctx.fillStyle = a.color;
      ctx.beginPath();
      ctx.arc(cx, cy, radius, 0, Math.PI * 2);
      ctx.fill();

      // Health bar
      ctx.fillStyle = '#333';
      ctx.fillRect(cx - radius, cy - radius - 4, radius * 2, 2);
      ctx.fillStyle = a.health > 0.5 ? '#22c55e' : '#ef4444';
      ctx.fillRect(cx - radius, cy - radius - 4, radius * 2 * a.health, 2);
    });
  }, [state, cellSize]);

  if (!state) {
    return (
      <div className="canvas-placeholder">
        <span>🌍</span>
        <p>Select a scenario to begin</p>
      </div>
    );
  }

  return (
    <div className="canvas-wrapper">
      <canvas ref={canvasRef} />
      <div className="canvas-overlay">
        Tick: {state.tick} | Agents: {state.agents?.length || 0}
      </div>
    </div>
  );
};

export default SimulationCanvas;
