import React from 'react';
import { Play, Pause, SkipForward, RotateCcw, Gauge } from 'lucide-react';

const ControlPanel = ({ isRunning, speed, onPlay, onPause, onStep, onReset, onSpeedChange, info }) => (
  <div className="control-panel">
    <div className="control-buttons">
      {!isRunning ? (
        <button className="btn btn-primary" onClick={onPlay} title="Play"><Play size={18} /> Play</button>
      ) : (
        <button className="btn btn-warning" onClick={onPause} title="Pause"><Pause size={18} /> Pause</button>
      )}
      <button className="btn btn-secondary" onClick={onStep} title="Step" disabled={isRunning}>
        <SkipForward size={18} /> Step
      </button>
      <button className="btn btn-danger" onClick={onReset} title="Reset"><RotateCcw size={18} /> Reset</button>
    </div>
    <div className="speed-control">
      <Gauge size={16} />
      <input
        type="range" min="1" max="10" value={speed}
        onChange={(e) => onSpeedChange(Number(e.target.value))}
      />
      <span>{speed}x</span>
    </div>
    {info && <div className="sim-info">{info}</div>}
  </div>
);

export default ControlPanel;
