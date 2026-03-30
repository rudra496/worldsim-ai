import React from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const MetricsPanel = ({ metrics, agentTypes }) => {
  const cards = [
    { label: 'Throughput', value: metrics?.throughput ? `${(metrics.throughput * 100).toFixed(1)}%` : '—', color: '#22c55e' },
    { label: 'Efficiency', value: metrics?.efficiency ? `${(metrics.efficiency * 100).toFixed(1)}%` : '—', color: '#3b82f6' },
    { label: 'Stability', value: metrics?.stability ? `${(metrics.stability * 100).toFixed(1)}%` : '—', color: '#f59e0b' },
    { label: 'Tick', value: metrics?.tick ?? '—', color: '#8b5cf6' },
  ];

  return (
    <div className="metrics-panel">
      <div className="metrics-cards">
        {cards.map((c) => (
          <div key={c.label} className="metric-card">
            <span className="metric-label">{c.label}</span>
            <span className="metric-value" style={{ color: c.color }}>{c.value}</span>
          </div>
        ))}
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <h4>Resource Utilization</h4>
          <ResponsiveContainer width="100%" height={160}>
            <LineChart data={metrics?.timeSeries || []}>
              <XAxis dataKey="tick" stroke="#555" tick={{ fontSize: 10 }} />
              <YAxis stroke="#555" tick={{ fontSize: 10 }} />
              <Tooltip contentStyle={{ background: '#1a1a2e', border: '1px solid #333', borderRadius: 8 }} />
              <Line type="monotone" dataKey="resources" stroke="#22c55e" dot={false} strokeWidth={2} />
              <Line type="monotone" dataKey="agents" stroke="#3b82f6" dot={false} strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h4>Agent Distribution</h4>
          <ResponsiveContainer width="100%" height={160}>
            <BarChart data={agentTypes || []}>
              <XAxis dataKey="type" stroke="#555" tick={{ fontSize: 10 }} />
              <YAxis stroke="#555" tick={{ fontSize: 10 }} />
              <Tooltip contentStyle={{ background: '#1a1a2e', border: '1px solid #333', borderRadius: 8 }} />
              <Bar dataKey="count" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default MetricsPanel;
