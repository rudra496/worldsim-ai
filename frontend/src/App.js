import React, { useState, useEffect, useCallback, useRef } from 'react';
import SimulationCanvas from './components/SimulationCanvas';
import MetricsPanel from './components/MetricsPanel';
import ControlPanel from './components/ControlPanel';
import ScenarioSelector from './components/ScenarioSelector';
import { generateDemoState, generateDemoMetrics } from './utils/simulation';
import { startSimulation, getStatus } from './services/api';

const POLL_INTERVAL = 2000;

const App = () => {
  const [scenario, setScenario] = useState(null);
  const [simState, setSimState] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [speed, setSpeed] = useState(1);
  const [tick, setTick] = useState(0);
  const [simId, setSimId] = useState(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [demoMode, setDemoMode] = useState(true);
  const [backendConnected, setBackendConnected] = useState(false);
  const [backendStatus, setBackendStatus] = useState('checking...');
  const intervalRef = useRef(null);
  const pollRef = useRef(null);

  const tickInterval = Math.max(50, 1000 / speed);

  // Check backend health
  useEffect(() => {
    const check = async () => {
      try {
        const res = await fetch(process.env.REACT_APP_API_URL || 'http://localhost:8000');
        if (res.ok) {
          setBackendConnected(true);
          setBackendStatus('connected');
        }
      } catch {
        setBackendConnected(false);
        setBackendStatus('offline — demo mode');
      }
    };
    check();
    const id = setInterval(check, 10000);
    return () => clearInterval(id);
  }, []);

  // Demo mode loop
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
    }
    return () => clearInterval(intervalRef.current);
  }, [isRunning, speed, demoMode, tickInterval]);

  // Backend poll loop
  useEffect(() => {
    if (isRunning && !demoMode && simId) {
      pollRef.current = setInterval(async () => {
        try {
          const status = await getStatus(simId);
          if (status.status === 'completed') {
            setIsRunning(false);
            setBackendStatus('simulation complete');
          }
          setTick(status.ticks_completed || tick);
          setSimState({
            agentCount: status.summary?.ticks || 0,
            metrics: status.summary,
          });
        } catch (e) {
          console.error('Poll failed:', e);
        }
      }, POLL_INTERVAL);
      return () => clearInterval(pollRef.current);
    }
    return () => clearInterval(pollRef.current);
  }, [isRunning, demoMode, simId, tick]);

  const handleSelectScenario = useCallback(async (scenarioId) => {
    setScenario(scenarioId);
    setTick(0);
    setIsRunning(false);
    clearInterval(intervalRef.current);
    clearInterval(pollRef.current);

    if (backendConnected) {
      try {
        const result = await startSimulation(scenarioId);
        setSimId(result.sim_id);
        setDemoMode(false);
        setSimState({ agentCount: 0, metrics: {} });
        setIsRunning(true);
        setBackendStatus('simulation running...');
        return;
      } catch (e) {
        console.warn('Backend start failed, falling back to demo:', e);
      }
    }

    setDemoMode(true);
    setSimState(generateDemoState(0));
  }, [backendConnected]);

  const metrics = simState?.metrics || (demoMode ? {
    throughput: 0.6 + Math.sin(tick * 0.1) * 0.2 + Math.random() * 0.1,
    efficiency: 0.7 + Math.cos(tick * 0.05) * 0.15,
    stability: 0.8 + Math.sin(tick * 0.03) * 0.1,
    resource_utilization: 0.4 + Math.sin(tick * 0.07) * 0.2,
    tick,
  } : null);

  const timeSeries = generateDemoMetrics(tick);

  const handlePlay = () => {
    if (!simState && !scenario) {
      setSimState(generateDemoState(0));
      setDemoMode(true);
    }
    setIsRunning(true);
  };

  const handleStep = () => {
    const t = tick + 1;
    setTick(t);
    setSimState(generateDemoState(t));
  };

  const handleReset = () => {
    setIsRunning(false);
    setTick(0);
    setSimId(null);
    setSimState(generateDemoState(0));
    setDemoMode(true);
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-left">
          <h1>🌍 WorldSim AI</h1>
          <span className="tagline">Digital Twin Simulation Platform</span>
        </div>
        <div className="header-right">
          <span className={`status-badge ${backendConnected ? 'connected' : 'offline'}`}>
            {backendStatus}
          </span>
          {demoMode && isRunning && <span className="demo-badge">DEMO</span>}
        </div>
      </header>

      <div className="app-layout">
        {!sidebarCollapsed && (
          <aside className="sidebar">
            <div className="sidebar-header">
              <h3>📂 Scenarios</h3>
              <button className="icon-btn" onClick={() => setSidebarCollapsed(true)} title="Collapse">◀</button>
            </div>
            <ScenarioSelector selected={scenario} onSelect={handleSelectScenario} />
          </aside>
        )}
        {sidebarCollapsed && (
          <button className="expand-btn" onClick={() => setSidebarCollapsed(false)} title="Expand sidebar">📂</button>
        )}

        <main className="main-content">
          <ControlPanel
            isRunning={isRunning}
            speed={speed}
            onPlay={handlePlay}
            onPause={() => setIsRunning(false)}
            onStep={handleStep}
            onReset={handleReset}
            onSpeedChange={setSpeed}
            info={scenario ? `${scenario} • ${demoMode ? 'Demo' : 'Backend'} • Tick ${tick}` : 'Select a scenario to begin'}
          />
          <div className="content-grid">
            <SimulationCanvas state={simState} />
            <MetricsPanel metrics={metrics} timeSeries={timeSeries} />
          </div>
        </main>
      </div>
    </div>
  );
};

export default App;
