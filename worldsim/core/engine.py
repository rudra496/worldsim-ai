"""
Simulation Engine — the heart of WorldSim AI.

Implements: S(t+1) = F(S(t), A(t), E(t))
- S = system state (StateManager)
- A = agent actions (AgentRegistry)
- E = environment factors (Environment)
- F = transition function (this engine)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import numpy as np

from .state import StateManager
from .events import EventBus, Event, EventType

logger = logging.getLogger(__name__)


class SimulationConfig:
    """Configuration for the simulation engine."""

    def __init__(
        self,
        dt: float = 1.0,
        max_ticks: int = 1000,
        deterministic: bool = True,
        seed: Optional[int] = 42,
    ):
        self.dt = dt
        self.max_ticks = max_ticks
        self.deterministic = deterministic
        self.seed = seed

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SimulationConfig:
        return cls(
            dt=data.get("dt", 1.0),
            max_ticks=data.get("max_ticks", 1000),
            deterministic=data.get("deterministic", True),
            seed=data.get("seed", 42),
        )


class SimulationEngine:
    """
    Core simulation engine supporting discrete-time and event-driven modes.

    Usage:
        engine = SimulationEngine(config=SimulationConfig())
        engine.register_environment(my_world)
        engine.register_agents(agent_list)
        results = engine.run()
    """

    def __init__(self, config: Optional[SimulationConfig] = None):
        self.config = config or SimulationConfig()
        self.state = StateManager()
        self.event_bus = EventBus()
        self._tick = 0
        self._running = False
        self._agents: List[Any] = []
        self._environment: Optional[Any] = None
        self._ai_modules: List[Any] = []
        self._results: List[Dict[str, Any]] = []
        self._rng = np.random.default_rng(self.config.seed)

    @property
    def tick(self) -> int:
        return self._tick

    @property
    def is_running(self) -> bool:
        return self._running

    def register_environment(self, env: Any) -> None:
        """Register an environment model."""
        self._environment = env
        self.event_bus.publish(Event(type=EventType.TICK, tick=0,
                                      data={"action": "environment_registered"}))

    def register_agents(self, agents: List[Any]) -> None:
        """Register agents for simulation."""
        self._agents = agents
        for agent in agents:
            self.event_bus.publish(Event(
                type=EventType.AGENT_CREATED,
                tick=self._tick,
                data={"agent_id": getattr(agent, "id", str(id(agent))),
                      "agent_type": getattr(agent, "agent_type", "unknown")},
            ))

    def register_ai_module(self, module: Any) -> None:
        """Register an AI/optimization module."""
        self._ai_modules.append(module)

    def step(self) -> Dict[str, Any]:
        """
        Execute one simulation step: S(t+1) = F(S(t), A(t), E(t)).

        Returns:
            Step result dict with tick, agent_states, environment_state, metrics.
        """
        # 1. Environment step — compute E(t)
        env_state = {}
        if self._environment:
            env_state = self._environment.step(self._tick, self.state.get_all())

        # 2. Agent step — compute A(t)
        agent_states = {}
        for agent in self._agents:
            try:
                agent_state = agent.step(self._tick, self.state.get_all(), env_state)
                agent_states[getattr(agent, "id", str(id(agent)))] = agent_state
            except Exception as e:
                logger.warning(f"Agent {getattr(agent, 'id', '?')} failed at tick {self._tick}: {e}")

        # 3. AI modules
        ai_actions = {}
        for ai_module in self._ai_modules:
            try:
                action = ai_module.step(self._tick, self.state.get_all(), env_state, agent_states)
                if action:
                    ai_actions[type(ai_module).__name__] = action
            except Exception as e:
                logger.warning(f"AI module {type(ai_module).__name__} failed: {e}")

        # 4. Compute new state: S(t+1) = F(S(t), A(t), E(t))
        new_state = self._transition_function(self.state.get_all(), agent_states, env_state, ai_actions)
        self.state.update(new_state)

        # 5. Collect metrics
        metrics = self._compute_metrics()

        # 6. Snapshot
        self.state.snapshot(tick=self._tick, agent_states=agent_states,
                           environment_state=env_state, metrics=metrics)

        # 7. Publish tick event
        self.event_bus.publish(Event(type=EventType.TICK, tick=self._tick))

        # 8. Record result
        result = {
            "tick": self._tick,
            "state": dict(new_state),
            "agent_states": agent_states,
            "environment_state": env_state,
            "ai_actions": ai_actions,
            "metrics": metrics,
        }
        self._results.append(result)

        self._tick += 1
        return result

    def _transition_function(
        self,
        state: Dict[str, Any],
        agent_states: Dict[str, Any],
        env_state: Dict[str, Any],
        ai_actions: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Core transition function F: combines current state with
        agent actions, environment changes, and AI decisions to
        produce the next state.
        """
        new_state = dict(state)
        new_state["tick"] = self._tick
        new_state["agent_count"] = len(agent_states)
        new_state["total_agents"] = len(self._agents)

        # Merge environment state
        for k, v in env_state.items():
            new_state[f"env_{k}"] = v

        # Merge AI actions
        for k, v in ai_actions.items():
            new_state[f"ai_{k}"] = v

        # Update resource counters from agent states
        total_energy = sum(
            a.get("energy_consumption", 0) for a in agent_states.values()
        )
        total_production = sum(
            a.get("production", 0) for a in agent_states.values()
        )
        new_state["total_energy_consumption"] = total_energy
        new_state["total_production"] = total_production
        new_state["avg_energy_per_agent"] = (
            total_energy / len(agent_states) if agent_states else 0
        )

        return new_state

    def _compute_metrics(self) -> Dict[str, float]:
        """Compute simulation metrics for the current step."""
        state = self.state.get_all()
        agent_count = state.get("agent_count", 0)
        total_energy = state.get("total_energy_consumption", 0)
        total_production = state.get("total_production", 0)

        # Efficiency: production / energy ratio
        efficiency = total_production / total_energy if total_energy > 0 else 0.0

        # Throughput: production output relative to agent count
        throughput = total_production / agent_count if agent_count > 0 else 0.0

        # Resource utilization: fraction of resources used
        resource_util = min(1.0, total_energy / 1000.0) if agent_count > 0 else 0.0

        # Stability: inverse of variance in recent energy consumption
        recent = self._results[-10:] if self._results else []
        if len(recent) > 1:
            energies = [r.get("metrics", {}).get("total_energy_consumption", 0) for r in recent]
            variance = float(np.var(energies))
            stability = 1.0 / (1.0 + variance)
        else:
            stability = 1.0

        return {
            "tick": float(self._tick),
            "efficiency": round(efficiency, 4),
            "throughput": round(throughput, 4),
            "resource_utilization": round(resource_util, 4),
            "stability": round(stability, 4),
            "total_energy_consumption": float(total_energy),
            "total_production": float(total_production),
            "agent_count": float(agent_count),
        }

    def run(self, ticks: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Run the full simulation.

        Args:
            ticks: Number of ticks to run (overrides config.max_ticks).

        Returns:
            List of step results.
        """
        self._running = True
        max_t = ticks or self.config.max_ticks
        self.event_bus.publish(Event(type=EventType.SIMULATION_START, tick=self._tick))

        logger.info(f"Simulation starting: {max_t} ticks, "
                     f"deterministic={self.config.deterministic}")

        try:
            while self._tick < max_t and self._running:
                self.step()
                if self._tick % 100 == 0:
                    logger.debug(f"Tick {self._tick}/{max_t}")
        finally:
            self._running = False
            self.event_bus.publish(Event(type=EventType.SIMULATION_END, tick=self._tick))

        logger.info(f"Simulation complete: {self._tick} ticks, "
                     f"{len(self._results)} results recorded")
        return self._results

    def reset(self) -> None:
        """Reset the simulation to initial state."""
        self._running = False
        self._tick = 0
        self.state = StateManager()
        self._agents = []
        self._environment = None
        self._ai_modules.clear()
        self._results.clear()
        self.event_bus.clear_log()
        self._rng = np.random.default_rng(self.config.seed)
        self.event_bus.publish(Event(type=EventType.SIMULATION_RESET, tick=0))
        logger.info("Simulation reset")

    def get_results(self) -> List[Dict[str, Any]]:
        """Get all recorded results."""
        return list(self._results)

    def get_summary(self) -> Dict[str, Any]:
        """Get simulation summary statistics."""
        if not self._results:
            return {"ticks": 0, "status": "no results"}
        metrics = [r["metrics"] for r in self._results]
        return {
            "ticks": self._tick,
            "status": "completed" if not self._running else "running",
            "final_metrics": metrics[-1] if metrics else {},
            "avg_efficiency": float(np.mean([m["efficiency"] for m in metrics])),
            "avg_throughput": float(np.mean([m["throughput"] for m in metrics])),
            "avg_stability": float(np.mean([m["stability"] for m in metrics])),
            "peak_energy": float(max(m["total_energy_consumption"] for m in metrics)),
        }

    def random(self, *args, **kwargs):
        """Get a random value from the engine's RNG (for deterministic mode)."""
        return self._rng.random(*args, **kwargs)

    def random_int(self, low: int, high: int, size: int = 1):
        """Get random integers from the engine's RNG."""
        return self._rng.integers(low, high, size=size)
