<div align="center">

# 🌍 WorldSim AI

**AI-Powered Digital Twin Simulation Platform**

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61dafb.svg)](https://reactjs.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://docker.com)

*Model, predict, and optimize real-world systems — cities, factories, energy grids, logistics, and environments.*

</div>

---

## 🌟 Vision

WorldSim AI is a research-grade, production-structured simulation platform for building **digital twins** of complex real-world systems. It's 100% free, open-source (MIT), and runs fully locally — no paid APIs, no cloud dependencies.

Whether you're a **researcher** studying emergent behavior, an **engineer** optimizing factory throughput, or a **student** learning simulation science — WorldSim AI gives you the tools.

## ✨ Features

- 🧬 **Agent-Based Modeling** — Vehicles, humans, machines, energy units with customizable behaviors
- 🌐 **Environment Modeling** — Grid and graph worlds with zones (residential, industrial, commercial, roads)
- 📊 **Real-Time Visualization** — Live 2D canvas view with agent tracking, heatmaps, and metrics dashboard
- 🧠 **AI & Optimization** — Prediction models, anomaly detection, resource allocation (LP-based), scheduling
- 🔬 **Research Framework** — Config-driven experiments, reproducible results (deterministic mode), benchmarking
- 📡 **REST API + WebSocket** — FastAPI backend with real-time simulation streaming
- 🎮 **4 Demo Scenarios** — Smart city traffic, factory optimization, energy balancing, emergency failure
- 🐳 **One-Command Setup** — `docker-compose up` and you're running
- 🔌 **Plugin Architecture** — Extensible agents, environments, behaviors, and AI modules

## 🏗 Architecture

```mermaid
graph TB
    subgraph "Presentation"
        UI[React Dashboard]
        Canvas[2D Canvas]
        Charts[Metrics Charts]
    end

    subgraph "API Layer"
        REST[REST API]
        WS[WebSocket]
    end

    subgraph "Simulation Core"
        Engine[Simulation Engine<br/>S(t+1) = F(S(t), A(t), E(t))]
        Events[Event Bus]
        State[State Manager]
    end

    subgraph "Modeling"
        Agents[Agent System]
        Env[Environment]
        Scenarios[Scenario Engine]
    end

    subgraph "Intelligence"
        Predict[Predictor]
        Detect[Anomaly Detector]
        Optimize[Optimizer]
    end

    subgraph "Data"
        DB[(PostgreSQL)]
        Redis[(Redis)]
    end

    UI --> REST
    UI --> WS
    REST --> Engine
    WS --> Engine
    Engine --> Agents
    Engine --> Env
    Engine --> Events
    Engine --> State
    Scenarios --> Engine
    Predict --> Engine
    Detect --> Engine
    Optimize --> Engine
    Engine --> DB
    Engine --> Redis
```

**State Transition Model:** `S(t+1) = F(S(t), A(t), E(t))`
- **S** — System state (resources, metrics, configuration)
- **A** — Agent actions (movement, production, consumption)
- **E** — Environment factors (zones, traffic, energy grid)
- **F** — Transition function (combines all inputs into next state)

## 🚀 Quick Start (5 minutes)

### Option 1: Docker (recommended)

```bash
git clone https://github.com/rudra496/worldsim-ai.git
cd worldsim-ai
docker-compose up --build
# Open http://localhost:3000
```

### Option 2: Run locally

```bash
git clone https://github.com/rudra496/worldsim-ai.git
cd worldsim-ai

# Backend
pip install -r requirements.txt
python run_demo.py

# API server
uvicorn worldsim.api.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend && npm install && npm start
```

### Option 3: Just the demo (no frontend)

```bash
pip install numpy scipy
python run_demo.py
```

## 🎮 Demo Scenarios

| Scenario | Description | Agents |
|----------|-------------|--------|
| 🏙️ **Smart City Traffic** | Urban traffic flow with vehicles & pedestrians across zones | 105 |
| 🏭 **Factory Optimization** | Production line with machines, workers, and energy constraints | 68 |
| ⚡ **Energy Balancing** | Multi-source energy grid with varying demand patterns | 85 |
| 🚨 **Emergency Failure** | System resilience under power outages and machine breakdowns | 76 |

## 📁 Project Structure

```
worldsim-ai/
├── worldsim/                    # Python simulation engine
│   ├── core/                    # Engine, state management, event bus
│   │   ├── engine.py            # Simulation engine (S(t+1) = F(...))
│   │   ├── state.py             # State snapshots & diffs
│   │   └── events.py            # Pub/sub event system
│   ├── agents/                  # Agent-based modeling
│   │   ├── models.py            # Vehicle, Human, Machine, Energy agents
│   │   └── behaviors.py         # Rule-based & probabilistic behaviors
│   ├── environment/             # World representation
│   │   ├── world.py             # GridWorld & GraphWorld
│   │   └── resources.py         # Resource management
│   ├── ai/                      # AI & optimization layer
│   │   ├── predictor.py         # Prediction & anomaly detection
│   │   └── optimizer.py         # Resource allocation & scheduling
│   ├── scenarios/               # Scenario engine & definitions
│   │   ├── engine.py            # Run & compare scenarios
│   │   └── definitions.py       # 4 predefined scenarios
│   ├── api/                     # FastAPI backend
│   │   └── __init__.py          # REST + WebSocket endpoints
│   ├── data/                    # Synthetic data generation
│   │   └── generator.py         # Agent, world, time series generators
│   └── utils/                   # Config & metrics
│       ├── config.py            # YAML/JSON config manager
│       └── metrics.py           # Metrics collection & export
├── frontend/                    # React visualization
│   ├── src/
│   │   ├── components/          # Canvas, Charts, Controls
│   │   ├── services/            # API client
│   │   └── utils/               # Simulation helpers
│   └── Dockerfile
├── config/default.yaml          # Default configuration
├── tests/                       # Test suite
├── docs/                        # Documentation
├── experiments/                 # Experiment results
├── docker-compose.yml
├── Dockerfile
└── run_demo.py                  # Quick demo runner
```

## 🛠 Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Simulation | Python 3.11+, NumPy | Core engine, numerical computation |
| API | FastAPI, Uvicorn, WebSockets | REST API, real-time streaming |
| AI/ML | NumPy, SciPy | Prediction, LP optimization |
| Frontend | React 18, recharts, Canvas | Visualization dashboard |
| Database | PostgreSQL 15 | Persistent storage |
| Cache | Redis 7 | Session & result caching |
| Deployment | Docker, Nginx | Containerized deployment |

## 🔬 Research Features

- **Deterministic mode** — Same seed → same results (reproducible experiments)
- **State snapshots** — Checkpoint & restore simulation state
- **Metrics collection** — Efficiency, throughput, stability, resource utilization
- **Experiment comparison** — Run scenarios with different parameters, compare outcomes
- **Results export** — JSON, CSV, text reports
- **Formal model** — Well-defined state transition function

## 🗺 Roadmap

- [x] **v0.1** — Core engine + agent system + 2D visualization + API
- [ ] **v0.2** — Reinforcement learning agents, advanced prediction models
- [ ] **v0.3** — 3D visualization (Three.js/WebGL)
- [ ] **v0.4** — Real-time data ingestion (IoT, sensors)
- [ ] **v0.5** — Distributed simulation (multi-node)
- [ ] **v1.0** — Full digital twin platform with live data

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. We welcome:
- New agent types and behavior models
- New scenarios and demo configurations
- Visualization improvements
- Documentation fixes
- Bug reports and feature requests

## 📜 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
<b>WorldSim AI</b> — Build digital twins. Model the world. Open source forever. 🌍
</div>
