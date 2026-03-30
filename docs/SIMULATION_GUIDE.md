# Simulation Guide

## How Simulations Work

Every simulation follows the same cycle:

1. **Initialize** — Create engine, environment, agents
2. **Run** — For each tick: agents act → AI analyzes → state updates → metrics record
3. **Analyze** — Export results, compare scenarios

## Running a Simulation Programmatically

```python
from worldsim.scenarios.engine import ScenarioEngine

engine = ScenarioEngine()
result = engine.run_scenario("smart_city_traffic", ticks=200)
print(result["summary"])
```

## Running via API

```bash
# Start simulation
curl -X POST http://localhost:8000/simulations/start \
  -H "Content-Type: application/json" \
  -d '{"scenario": "smart_city_traffic", "ticks": 200}'

# Check status
curl http://localhost:8000/simulations/sim_1

# Get metrics
curl http://localhost:8000/simulations/sim_1/metrics
```

## Creating Custom Agents

```python
from worldsim.agents.models import BaseAgent

class DroneAgent(BaseAgent):
    def __init__(self, agent_id, position, **kwargs):
        super().__init__(agent_id, position, **kwargs)
        self.agent_type = "drone"
        self.params.setdefault("speed", 3.0)
        self.params.setdefault("battery", 100.0)
        self.params.setdefault("energy_cost", 2.0)

    def step(self, tick, world_state, env_state):
        # Custom logic here
        return super().step(tick, world_state, env_state)
```

## Creating Custom Scenarios

```python
from worldsim.scenarios.definitions import _ALL_SCENARIOS

_MY_SCENARIO = {
    "name": "my_custom",
    "display_name": "My Custom Scenario",
    "description": "...",
    "world_size": (30, 30),
    "duration": 500,
    "agents": {"vehicle": 10, "human": 20},
    "zones": [
        {"type": "residential", "bounds": [0, 0, 15, 15], "population": 100},
    ],
}

# Register it
from worldsim.scenarios import engine
engine.ScenarioEngine().register_scenario("my_custom", _MY_SCENARIO)
```

## Interpreting Results

### Key Metrics

| Metric | What it measures | Good range |
|--------|-----------------|------------|
| **Efficiency** | Production / energy ratio | 0.5 - 1.0 |
| **Throughput** | Agent activity per tick | Depends on scenario |
| **Resource Utilization** | Fraction of resources used | 0.3 - 0.8 |
| **Stability** | Low variance in system state | 0.7 - 1.0 |

### Export Formats

```python
from worldsim.utils.metrics import ResultsExporter

# JSON
json_str = ResultsExporter.to_json(results)

# CSV
csv_str = ResultsExporter.to_csv(results)

# Text report
report = ResultsExporter.summary_report(results)

# Save to file
ResultsExporter.save(results, "output/report.json")
```

## Deterministic Mode

Set `deterministic=True` and `seed=42` for reproducible experiments:

```python
result = engine.run_scenario("smart_city_traffic", override_config={
    "deterministic": True,
    "seed": 42,
})
```

## Experiment Comparison

```python
variations = [
    {"seed": 42, "agents": {"vehicle": 20}},
    {"seed": 42, "agents": {"vehicle": 40}},
    {"seed": 42, "agents": {"vehicle": 80}},
]
results = engine.run_comparison("smart_city_traffic", variations, ticks=100)
```
