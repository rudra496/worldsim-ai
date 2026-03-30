"""Agent models — base agent and specialized agent types."""

from __future__ import annotations

import logging
from abc import ABC
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np

from .behaviors import BehaviorModel, RuleBasedBehavior

logger = logging.getLogger(__name__)


@dataclass
class AgentState:
    """State of an agent at a given moment."""
    position: tuple = (0, 0)
    velocity: tuple = (0.0, 0.0)
    energy: float = 100.0
    health: float = 100.0
    load: float = 0.0
    status: str = "active"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "position": list(self.position),
            "velocity": list(self.velocity),
            "energy": self.energy,
            "health": self.health,
            "load": self.load,
            "status": self.status,
        }


class BaseAgent(ABC):
    """
    Base agent with position, state, behavior, and decision-making.

    Every agent implements step() which returns its state after the tick.
    """

    def __init__(
        self,
        agent_id: str,
        position: tuple = (0, 0),
        behavior: Optional[BehaviorModel] = None,
        params: Optional[Dict[str, Any]] = None,
    ):
        self.id = agent_id
        self.agent_type: str = "base"
        self.position = position
        self.state = AgentState(position=position)
        self.behavior = behavior or RuleBasedBehavior()
        self.params = params or {}
        self._history: List[Dict[str, Any]] = []

    def step(self, tick: int, world_state: Dict[str, Any], env_state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute one simulation step."""
        # 1. Perceive neighbors (simplified)
        neighbors = self._perceive(world_state)

        # 2. Decide action
        action = self.behavior.decide(world_state, neighbors)

        # 3. Act
        self._act(action, env_state)

        # 4. Record
        agent_state = self.state.to_dict()
        agent_state["action"] = action
        agent_state["energy_consumption"] = self._compute_energy_consumption()
        agent_state["production"] = self._compute_production()
        self._history.append({"tick": tick, **agent_state})

        return agent_state

    def _perceive(self, world_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get information about nearby agents/environment."""
        return []

    def _act(self, action: Dict[str, Any], env_state: Dict[str, Any]) -> None:
        """Execute the decided action."""
        act = action.get("action", "idle")
        if act == "move":
            direction = action.get("direction", (0, 0))
            speed = self.params.get("speed", 1.0)
            new_x = self.position[0] + direction[0] * speed
            new_y = self.position[1] + direction[1] * speed
            self.position = (new_x, new_y)
            self.state.position = self.position

    def _compute_energy_consumption(self) -> float:
        """Compute energy consumed this step."""
        return self.params.get("energy_cost", 1.0)

    def _compute_production(self) -> float:
        """Compute production output this step."""
        return self.params.get("production_rate", 0.0)

    def get_history(self) -> List[Dict[str, Any]]:
        return list(self._history)


class VehicleAgent(BaseAgent):
    """Vehicle agent — moves on roads, consumes energy."""

    def __init__(self, agent_id: str, position: tuple = (0, 0),
                 vehicle_type: str = "car", **kwargs):
        super().__init__(agent_id, position, **kwargs)
        self.agent_type = "vehicle"
        self.vehicle_type = vehicle_type
        self.params.setdefault("speed", 2.0)
        self.params.setdefault("energy_cost", 3.0)
        self.params.setdefault("capacity", 100.0)
        self.params.setdefault("fuel", 100.0)
        self.behavior = self.behavior or RuleBasedBehavior(
            rules=[
                (
                    lambda s, n: s.get("fuel", 100) < 10,
                    lambda s, n: {"action": "refuel"},
                ),
                (
                    lambda s, n: True,
                    lambda s, n: {"action": "move",
                                  "direction": (np.random.randint(-1, 2),
                                                np.random.randint(-1, 2))},
                ),
            ]
        )


class HumanAgent(BaseAgent):
    """Human agent — moves in pedestrian areas, has tasks."""

    def __init__(self, agent_id: str, position: tuple = (0, 0),
                 role: str = "citizen", **kwargs):
        super().__init__(agent_id, position, **kwargs)
        self.agent_type = "human"
        self.role = role
        self.params.setdefault("speed", 1.0)
        self.params.setdefault("energy_cost", 1.0)
        self.params.setdefault("productivity", 0.8)


class MachineAgent(BaseAgent):
    """Machine agent — stationary or slowly moving, produces/consumes."""

    def __init__(self, agent_id: str, position: tuple = (0, 0),
                 machine_type: str = "factory_unit", **kwargs):
        super().__init__(agent_id, position, **kwargs)
        self.agent_type = "machine"
        self.machine_type = machine_type
        self.params.setdefault("speed", 0.0)
        self.params.setdefault("energy_cost", 10.0)
        self.params.setdefault("production_rate", 5.0)
        self.params.setdefault("efficiency", 0.85)
        self.params.setdefault("failure_rate", 0.001)

    def step(self, tick: int, world_state: Dict[str, Any], env_state: Dict[str, Any]) -> Dict[str, Any]:
        # Check for failure
        if np.random.random() < self.params.get("failure_rate", 0.001):
            self.state.status = "failed"
            self.state.health = 0.0
            self.params["production_rate"] = 0.0
        result = super().step(tick, world_state, env_state)
        return result


class EnergyUnitAgent(BaseAgent):
    """Energy unit — generates, stores, or distributes energy."""

    def __init__(self, agent_id: str, position: tuple = (0, 0),
                 energy_type: str = "solar", **kwargs):
        super().__init__(agent_id, position, **kwargs)
        self.agent_type = "energy"
        self.energy_type = energy_type
        self.params.setdefault("speed", 0.0)
        self.params.setdefault("energy_cost", 0.0)
        self.params.setdefault("production_rate", 20.0)
        self.params.setdefault("capacity", 500.0)
        self.params.setdefault("output", 15.0)


class AgentRegistry:
    """Registry for tracking and managing all agents."""

    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> None:
        self._agents[agent.id] = agent

    def unregister(self, agent_id: str) -> None:
        self._agents.pop(agent_id, None)

    def get(self, agent_id: str) -> Optional[BaseAgent]:
        return self._agents.get(agent_id)

    def get_all(self) -> List[BaseAgent]:
        return list(self._agents.values())

    def get_by_type(self, agent_type: str) -> List[BaseAgent]:
        return [a for a in self._agents.values() if a.agent_type == agent_type]

    def count(self) -> int:
        return len(self._agents)

    def count_by_type(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for a in self._agents.values():
            counts[a.agent_type] = counts.get(a.agent_type, 0) + 1
        return counts

    def clear(self) -> None:
        self._agents.clear()


class InteractionSystem:
    """
    Manages interactions between agents and with the environment.

    Supports: proximity-based, resource exchange, signal broadcast.
    """

    def __init__(self, interaction_range: float = 5.0):
        self.interaction_range = interaction_range

    def find_neighbors(self, agent: BaseAgent, all_agents: List[BaseAgent]) -> List[BaseAgent]:
        """Find agents within interaction range."""
        neighbors = []
        ax, ay = agent.position
        for other in all_agents:
            if other.id == agent.id:
                continue
            ox, oy = other.position
            dist = ((ax - ox) ** 2 + (ay - oy) ** 2) ** 0.5
            if dist <= self.interaction_range:
                neighbors.append(other)
        return neighbors

    def exchange_resources(self, agent_a: BaseAgent, agent_b: BaseAgent,
                           resource: str = "energy", amount: float = 10.0) -> bool:
        """Exchange a resource between two agents."""
        a_has = agent_a.state.energy if resource == "energy" else agent_a.state.load
        if a_has >= amount:
            if resource == "energy":
                agent_a.state.energy -= amount
                agent_b.state.energy = min(100.0, agent_b.state.energy + amount)
            else:
                agent_a.state.load -= amount
                agent_b.state.load += amount
            return True
        return False
