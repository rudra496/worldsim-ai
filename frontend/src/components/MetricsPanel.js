import React, { useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';

const MetricsPanel = ({ metrics, timeSeries }) => {
  const cards = useMemo(() => {
    if (!metrics) return [];
    return [
      { label: 'Efficiency', value: metrics.efficiency?.toFixed(3) || '—', color: '#22c55e' },
      { label: 'Throughput', value: metrics.throughput?.toFixed(3) || '—', color: '#3b82f6' },
      { label: 'Stability', value: metrics.stability?.toFixed(3) || '—', color: '#f59e0b' },
      { label: 'Resource Util', value: metrics.resource_utilization?.toFixed(3) || '—', color: '#ef4444' },
    ];
  }, [metrics]);

  return (
    <div className="metrics-panel">
      <h3>📊 Metrics</h3>
      <div className="metric-cards">
        {cards.map((c) => (
          <div key={c.label} className="metric-card" style={{ borderTopColor: c.color }}>
            <div className="metric-label">{c.label}</div>
            <div className="metric-value">{c.value}</div>
          </div>
        ))}
      </div>
      {timeSeries && timeSeries.length > 0 && (
        <div className="chart-container">
          <h4>Energy & Efficiency Over Time</h4>
          <ResponsiveContainer width="100%" height={180}>
            <LineChart data={timeSeries}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="tick" stroke="#64748b" tick={{ fontSize: 11 }} />
              <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: 8 }}
                labelStyle={{ color: '#e2e8f0' }}
              />
              <Line type="monotone" dataKey="energy" stroke="#ef4444" dot={false} strokeWidth={2} name="Energy" />
              <Line type="monotone" dataKey="efficiency" stroke="#22c55e" dot={false} strokeWidth={2} name="Efficiency" />
              <Line type="monotone" dataKey="stability" stroke="#f59e0b" dot={false} strokeWidth={2} name="Stability" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};

export default MetricsPanel;
