import React, { useState, useEffect, useCallback, useRef } from 'react';
import SimulationCanvas from './components/SimulationCanvas';
import MetricsPanel from './components/MetricsPanel';
import ControlPanel from './components/ControlPanel';
import ScenarioSelector from './components/ScenarioSelector';
import { generateDemoState, generateDemoMetrics } from './utils/simulation';
import { startSimulation, stepSimulation, pauseSimulation, resumeSimulation, resetSimulation, getMetrics } from './services/api';

const App = () => {
  const [scenario, setScenario] = useState(null);
  const [simState, setSimState] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [speed, setSpeed] = useState(1);
  const [tick, setTick] = useState(0);
  const [simId, setSimId] = useState(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [demoMode, setDemoMode] = useState(true);
  const intervalRef = useRef(null);

  const tickInterval = Math.max(50, 1000 / speed);

  // Demo mode simulation loop
  useEffect(() => {
    if (isRunning && demoMode) {
      intervalRef.current = setInterval(() => {
        setTick((t) => {
          const newTick = t + 1;
          setSimState(generateDemoState(newTick));
          return newTick;
        });
      }, tickInterval);
      return () => clearInterval(intervalRef.current);
    } else {
      clearInterval(intervalRef.current);
    }
  }, [isRunning, speed, demoMode, tickInterval]);

  // Backend mode simulation loop
  useEffect(() => {
    if (isRunning && !demoMode && simId) {
      intervalRef.current = setInterval(async () => {
        try {
          const result = await stepSimulation(simId);
          setSimState(result);
          setTick(result.tick || tick + 1);
        } catch (e) {
          console.error('Step failed:', e);
          setIsRunning(false);
        }
      }, tickInterval);
      return () => clearInterval(intervalRef.current);
    } else {
      clearInterval(intervalRef.current);
    }
  }, [isRunning, speed, demoMode, simId, tickInterval]);

  const handleSelectScenario = useCallback(async (scenarioId) => {
    setScenario(scenarioId);
    setTick(0);
    setIsRunning(false);
    clearInterval(intervalRef.current);

    try {
      const result = await startSimulation(scenarioId);
      setSimId(result.id);
      setSimState(result);
      setDemoMode(false);
    } catch {
      // Backend not available — use demo mode
      setDemoMode(true);
      setSimState(generateDemoState(0));
    }
  }, []);

  const metrics = simState
    ? {
        throughput: 0.6 + Math.sin(tick * 0.1) * 0.2 + Math.random() * 0.1,
        efficiency: 0.7 + Math.cos(tick * 0.05) * 0.15,
        stability: 0.8 + Math.sin(tick * 0.03) * 0.1,
        tick,
        timeSeries: generateDemoMetrics(tick),
      }
    : null;

  const agentTypes = simState?.agents
    ? Object.entries(simState.agents.reduce((acc, a) => {
        acc[a.type] = (acc[a.type] || 0) + 1;
        return acc;
      }, {})).map(([type, count]) => ({ type, count }))
    : [];

  return (
    <div className="app">
      <header className="app-header">
        <h1>🌍 WorldSim AI</h1>
        <span className="tagline">Digital Twin Simulation Platform</span>
        {demoMode && <span className="demo-badge">DEMO MODE</span>}
      </header>

      <div className="app-layout">
        <aside className={`sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
          <ScenarioSelector
            selected={scenario}
            onSelect={handleSelectScenario}
            collapsed={sidebarCollapsed}
            onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
          />
        </aside>

        <main className="main-content">
          <ControlPanel
            isRunning={isRunning}
            speed={speed}
            onPlay={() => { if (!simState && !scenario) setSimState(generateDemoState(0)); setIsRunning(true); }}
            onPause={() => setIsRunning(false)}
            onStep={() => {
              const t = tick + 1;
              setTick(t);
              setSimState(generateDemoState(t));
            }}
            onReset={() => { setIsRunning(false); setTick(0); setSimState(simState ? generateDemoState(0) : null); }}
            onSpeedChange={setSpeed}
            info={scenario ? `Scenario: ${scenario} | ${demoMode ? 'Demo' : 'Backend'}` : 'No scenario selected'}
          />
          <SimulationCanvas state={simState} />
          <MetricsPanel metrics={metrics} agentTypes={agentTypes} />
        </main>
      </div>
    </div>
  );
};

export default App;
