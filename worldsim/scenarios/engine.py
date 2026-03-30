"""Scenario engine — run, compare, and manage simulation scenarios."""

from __future__ import annotations

import logging
from copy import deepcopy
from typing import Any, Dict, List, Optional

import numpy as np

from worldsim.core.engine import SimulationEngine, SimulationConfig
from worldsim.core.state import StateManager
from worldsim.agents.models import (
    BaseAgent, VehicleAgent, HumanAgent, MachineAgent, EnergyUnitAgent,
    AgentRegistry, InteractionSystem,
)
from worldsim.environment.world import GridWorld, Zone, ZoneType
from worldsim.environment.resources import ResourceManager, ResourceType
from worldsim.ai.predictor import SimplePredictor, AnomalyDetector
from worldsim.ai.optimizer import ResourceAllocator

logger = logging.getLogger(__name__)

AGENT_MAP = {
    "vehicle": VehicleAgent,
    "human": HumanAgent,
    "machine": MachineAgent,
    "energy": EnergyUnitAgent,
}


class ScenarioEngine:
    """
    Configure and run simulation scenarios.

    Usage:
        se = ScenarioEngine()
        results = se.run_scenario("smart_city")
    """

    def __init__(self):
        self._scenarios: Dict[str, Dict[str, Any]] = {}
        self._results: Dict[str, List[Dict]] = {}

    def register_scenario(self, name: str, config: Dict[str, Any]) -> None:
        self._scenarios[name] = config

    def run_scenario(self, name: str, ticks: Optional[int] = None,
                     override_config: Optional[Dict] = None) -> Dict[str, Any]:
        """Run a named scenario and return results + summary."""
        from .definitions import get_scenario
        config = get_scenario(name)
        if config is None:
            raise ValueError(f"Unknown scenario: {name}. Available: {list(self._scenarios.keys())}")

        if override_config:
            config = {**config, **override_config}

        engine = self._build_engine(config)
        actual_ticks = ticks or config.get("duration", 200)
        results = engine.run(ticks=actual_ticks)
        summary = engine.get_summary()

        self._results[name] = results
        return {"scenario": name, "config": config, "results": results, "summary": summary}

    def run_comparison(self, scenario_name: str, param_variations: List[Dict[str, Any]],
                       ticks: Optional[int] = None) -> List[Dict[str, Any]]:
        """Run a scenario multiple times with different parameters."""
        from .definitions import get_scenario
        base_config = get_scenario(scenario_name)
        if base_config is None:
            raise ValueError(f"Unknown scenario: {scenario_name}")

        comparison_results = []
        for i, variation in enumerate(param_variations):
            merged = {**deepcopy(base_config), **variation}
            engine = self._build_engine(merged)
            actual_ticks = ticks or merged.get("duration", 200)
            results = engine.run(ticks=actual_ticks)
            summary = engine.get_summary()
            comparison_results.append({
                "run_id": i,
                "params": variation,
                "summary": summary,
                "results": results,
            })
            logger.info(f"Comparison run {i+1}/{len(param_variations)} complete")

        return comparison_results

    def _build_engine(self, config: Dict[str, Any]) -> SimulationEngine:
        """Build a complete simulation engine from scenario config."""
        # Engine config
        sim_config = SimulationConfig(
            dt=config.get("dt", 1.0),
            max_ticks=config.get("duration", 200),
            deterministic=config.get("deterministic", True),
            seed=config.get("seed", 42),
        )
        engine = SimulationEngine(config=sim_config)

        # World
        world_size = config.get("world_size", (50, 50))
        world = GridWorld(width=world_size[0], height=world_size[1])
        for zone_config in config.get("zones", []):
            zone = Zone(
                zone_type=ZoneType(zone_config["type"]),
                bounds=tuple(zone_config["bounds"]),
                population=zone_config.get("population", 0),
                capacity=zone_config.get("capacity", 100),
                energy_demand=zone_config.get("energy_demand", 10),
                production_output=zone_config.get("production_output", 0),
            )
            world.add_zone(zone)
        engine.register_environment(world)

        # Agents
        agent_configs = config.get("agents", {})
        agents = []
        for agent_type, count in agent_configs.items():
            agent_cls = AGENT_MAP.get(agent_type, BaseAgent)
            for i in range(count):
                pos = (
                    int(np.random.randint(0, world_size[0])),
                    int(np.random.randint(0, world_size[1])),
                )
                agent = agent_cls(agent_id=f"{agent_type}_{i:04d}", position=pos)
                agents.append(agent)
        engine.register_agents(agents)

        # AI modules
        if config.get("enable_predictor", True):
            engine.register_ai_module(SimplePredictor())
        if config.get("enable_optimizer", True):
            engine.register_ai_module(ResourceAllocator(
                total_budget=config.get("energy_budget", 1000)
            ))

        # Initial state
        engine.state.set("world_size", world_size)
        engine.state.set("scenario_name", config.get("name", "unknown"))

        return engine

    def get_results(self, scenario_name: str) -> Optional[List[Dict]]:
        return self._results.get(scenario_name)

    def list_available(self) -> List[str]:
        from .definitions import list_scenarios
        return list_scenarios()
