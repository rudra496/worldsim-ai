import React from 'react';

const ControlPanel = ({ isRunning, speed, onPlay, onPause, onStep, onReset, onSpeedChange, info }) => (
  <div className="control-panel">
    <div className="controls-left">
      <button className={`ctrl-btn ${isRunning ? 'active' : ''}`} onClick={isRunning ? onPause : onPlay}>
        {isRunning ? '⏸ Pause' : '▶ Play'}
      </button>
      <button className="ctrl-btn" onClick={onStep} disabled={isRunning}>⏭ Step</button>
      <button className="ctrl-btn" onClick={onReset}>⟳ Reset</button>
      <div className="speed-control">
        <label>Speed:</label>
        <input
          type="range" min="1" max="10" value={speed}
          onChange={(e) => onSpeedChange(Number(e.target.value))}
        />
        <span>{speed}x</span>
      </div>
    </div>
    <div className="controls-right">
      <span className="info-text">{info}</span>
    </div>
  </div>
);

export default ControlPanel;
