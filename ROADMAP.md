# Roadmap

> **All planned versions are implemented.** See `worldsim/` for the full codebase.

## v0.1 — Core Platform ✅ (March 2026)
- [x] Core simulation engine with formal state model S(t+1) = F(S(t), A(t), E(t))
- [x] Agent-based modeling (Vehicle, Human, Machine, EnergyUnit)
- [x] Grid and graph world environments
- [x] Zone system (8 zone types: residential, industrial, commercial, road, park, power_plant, water_treatment, warehouse)
- [x] Resource management (energy, water, materials, bandwidth)
- [x] AI prediction (linear regression, moving average, exponential smoothing)
- [x] Statistical anomaly detection (z-score based)
- [x] LP-based optimization (resource allocation via scipy)
- [x] Priority scheduling optimization
- [x] Scenario engine with 8 demo scenarios
- [x] FastAPI REST + WebSocket API (9 endpoints)
- [x] React 2D visualization dashboard with dark theme
- [x] Docker Compose (backend + frontend)
- [x] Config-driven architecture (YAML)
- [x] Metrics collection, aggregation, and export (JSON/CSV/text)
- [x] Deterministic mode for reproducibility (seed-based)
- [x] CLI tool: `worldsim run/list/demo/serve`
- [x] Full documentation (ARCHITECTURE, SIMULATION_GUIDE, CONTRIBUTING)
- [x] GitHub community (MIT license, CODE_OF_CONDUCT, issue/PR templates, CI)

## v0.2 — AI Enhanced ✅ (March 2026)
- [x] PyTorch LSTM time series predictor (NumPy fallback when PyTorch unavailable)
- [x] Demand forecaster with normalization and confidence scoring
- [x] Autoencoder-based anomaly detection (statistical fallback)
- [x] Gymnasium-compatible RL environment (SimulationEnv)
- [x] RL agent with PPO (stable-baselines3) and Q-learning fallback
- [x] Multi-agent RL system (centralized training, decentralized execution)
- [x] Multi-agent AI system: PlannerAgent, PredictorAgent, OptimizerAgent
- [x] AgentCoordinator (orchestrates predict → optimize → feedback loop)
- [x] Adaptive feedback loops with drift detection and correction
- [x] Model save/load (JSON + PyTorch state_dict)

## v0.3 — 3D Visualization ✅ (March 2026)
- [x] Three.js 3D world via React Three Fiber
- [x] Orbit camera controls (rotate, pan, zoom)
- [x] 3D zone rendering (translucent colored boxes with labels)
- [x] 3D agent objects (vehicles=boxes, humans=spheres, machines=cylinders, energy=glowing spheres)
- [x] Agent glow effects via point lights
- [x] Day/night cycle toggle (ambient + directional lighting)
- [x] Grid overlay with fog effects
- [x] 2D ↔ 3D view switcher with tab UI
- [x] Camera preset controls (Top Down, Isometric, Free)

## v0.4 — IoT Data Ingestion ✅ (March 2026)
- [x] DataSource abstract interface
- [x] MQTT source (paho-mqtt, topic subscription, JSON/CSV parsing)
- [x] File source (CSV/JSON with tail support)
- [x] REST API source (periodic polling)
- [x] Simulator source (synthetic sensor data with noise/drift/failure injection)
- [x] DataIngestionManager (multi-source orchestration)
- [x] DataBuffer (ring buffer with time-based queries)
- [x] DataTransformer (sensor ID → simulation entity mapping)
- [x] AlertManager (CRITICAL/WARNING/INFO with callback system)
- [x] Example sensor configuration (config/sensors.yaml)

## v0.5 — Distributed Simulation ✅ (March 2026)
- [x] DistributedEngine (extends SimulationEngine for multi-node)
- [x] SimulationNode (per-node agent execution with heartbeat)
- [x] SpatialPartitioner (grid-based agent distribution)
- [x] LoadBalancer (threshold-based rebalancing with migration plans)
- [x] gRPC protocol definitions (dataclass-based, no protoc required)
- [x] MessageSerializer (pickle + zlib compression)
- [x] Sync strategies: barrier, async, hybrid

## v1.0 — Full Digital Twin ✅ (March 2026)
- [x] DigitalTwin core (live, replay, hybrid sync modes)
- [x] GIS integration (GeoJSON loading, coordinate transforms, geofencing)
- [x] GeoFence with ray-casting algorithm (shapely optional)
- [x] Plugin system with ABC interface and hot-reload
- [x] Built-in plugins: LoggingPlugin, MetricsExportPlugin, SlackNotifyPlugin
- [x] Plugin marketplace (local catalog with search and install)
- [x] Local plugin registry (~/.worldsim/plugins/)
- [x] TwinConnector (REST push/pull, WebSocket bidirectional sync)
- [x] API key authentication with role-based access
- [x] Rate limiting (token bucket)
- [x] pyproject.toml with optional dependency groups (ml, rl, distributed, iot, twin)

## Future Ideas (beyond v1.0)
- [ ] WebGPU rendering for better 3D performance
- [ ] Kubernetes deployment manifests
- [ ] Real-world case study documentation
- [ ] Multi-language SDK (Python, JavaScript, Go)
- [ ] Cloud-hosted marketplace server
- [ ] Academic paper and benchmark suite
- [ ] Mobile companion app for monitoring
- [ ] Collaborative multi-user simulation editing
