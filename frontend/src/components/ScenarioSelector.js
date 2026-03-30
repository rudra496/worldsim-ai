import React from 'react';

const SCENARIOS = [
  {
    id: 'smart_city_traffic',
    icon: '🏙️',
    name: 'Smart City Traffic',
    description: 'Urban traffic flow with vehicles and pedestrians',
    agents: 105,
  },
  {
    id: 'factory_optimization',
    icon: '🏭',
    name: 'Factory Optimization',
    description: 'Production line with machines and energy constraints',
    agents: 68,
  },
  {
    id: 'energy_balancing',
    icon: '⚡',
    name: 'Energy Balancing',
    description: 'Multi-source energy grid with varying demand',
    agents: 85,
  },
  {
    id: 'emergency_failure',
    icon: '🚨',
    name: 'Emergency Failure',
    description: 'System resilience under failures and breakdowns',
    agents: 76,
  },
];

const ScenarioSelector = ({ selected, onSelect, collapsed, onToggle }) => {
  if (collapsed) {
    return (
      <aside className="sidebar collapsed">
        <button className="toggle-btn" onClick={onToggle}>▶</button>
      </aside>
    );
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h3>Scenarios</h3>
        <button className="toggle-btn" onClick={onToggle}>◀</button>
      </div>
      <div className="scenario-list">
        {SCENARIOS.map((s) => (
          <div
            key={s.id}
            className={`scenario-card ${selected === s.id ? 'active' : ''}`}
            onClick={() => onSelect(s.id)}
          >
            <div className="scenario-icon">{s.icon}</div>
            <div className="scenario-info">
              <div className="scenario-name">{s.name}</div>
              <div className="scenario-desc">{s.description}</div>
              <div className="scenario-agents">{s.agents} agents</div>
            </div>
          </div>
        ))}
      </div>
    </aside>
  );
};

export default ScenarioSelector;
