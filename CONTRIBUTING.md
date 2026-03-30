# Contributing to WorldSim AI

Thanks for your interest! Here's how to get started.

## Setup

```bash
git clone https://github.com/rudra496/worldsim-ai.git
cd worldsim-ai

# Python
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Run demo
python run_demo.py

# Frontend
cd frontend && npm install && npm start
```

## Code Style

- Python: PEP 8, type hints on public APIs, docstrings on classes and public methods
- JavaScript: Standard style
- Keep lines under 100 characters
- No magic numbers — use config values

## PR Process

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Write code + tests
4. Ensure all tests pass: `python -m pytest tests/`
5. Open a Pull Request with a clear description

## Adding New Components

### New Agent Type
1. Create class inheriting `BaseAgent` in `worldsim/agents/models.py`
2. Implement `step()`, `_compute_energy_consumption()`, `_compute_production()`
3. Add to `AGENT_MAP` in `worldsim/scenarios/engine.py`

### New Behavior Model
1. Subclass `BehaviorModel` in `worldsim/agents/behaviors.py`
2. Implement `decide(state, neighbors)`

### New Scenario
1. Add config dict in `worldsim/scenarios/definitions.py`
2. Add to `_ALL_SCENARIOS`

### New AI Module
1. Create class with `step(tick, state, env_state, agent_states)` method
2. Return dict with action recommendations
3. Register via `engine.register_ai_module()`

## Issue Guidelines

- Bug reports: Include steps to reproduce, expected vs actual behavior
- Feature requests: Describe the use case, not just the solution
- Questions: Check docs first, then open an issue
