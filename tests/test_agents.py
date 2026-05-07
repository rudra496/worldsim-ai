"""Tests for agent models and behaviors."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from worldsim.agents.models import (
    BaseAgent, VehicleAgent, HumanAgent, MachineAgent, EnergyUnitAgent,
    AgentRegistry, InteractionSystem, AgentState,
)
from worldsim.agents.behaviors import RuleBasedBehavior, ProbabilisticBehavior


class TestAgentState:
    def test_to_dict(self):
        s = AgentState(position=(3, 4), energy=80.0)
        d = s.to_dict()
        assert d["position"] == [3, 4]
        assert d["energy"] == 80.0
        assert d["status"] == "active"

    def test_defaults(self):
        s = AgentState()
        assert s.position == (0, 0)
        assert s.energy == 100.0
        assert s.status == "active"


class TestBaseAgent:
    def test_step_returns_state(self):
        agent = BaseAgent("a1", position=(5, 5))
        result = agent.step(tick=0, world_state={}, env_state={})
        assert "position" in result
        assert "action" in result
        assert "energy_consumption" in result

    def test_agent_history(self):
        agent = BaseAgent("a1", position=(0, 0))
        agent.step(tick=0, world_state={}, env_state={})
        agent.step(tick=1, world_state={}, env_state={})
        history = agent.get_history()
        assert len(history) == 2

    def test_perceive_returns_data(self):
        agent = BaseAgent("a1", position=(5, 5))
        neighbors = agent._perceive({"tick": 1, "agent_count": 5})
        assert len(neighbors) > 0
        assert neighbors[0]["tick"] == 1


class TestVehicleAgent:
    def test_vehicle_type(self):
        v = VehicleAgent("v1", position=(0, 0))
        assert v.agent_type == "vehicle"
        assert v.params["speed"] == 2.0

    def test_vehicle_step(self):
        v = VehicleAgent("v1", position=(10, 10))
        result = v.step(tick=0, world_state={}, env_state={})
        assert result["energy_consumption"] == 3.0


class TestHumanAgent:
    def test_human_type(self):
        h = HumanAgent("h1", position=(0, 0))
        assert h.agent_type == "human"
        assert h.params["speed"] == 1.0


class TestMachineAgent:
    def test_machine_type(self):
        m = MachineAgent("m1", position=(5, 5))
        assert m.agent_type == "machine"
        assert m.params["production_rate"] == 5.0

    def test_machine_production(self):
        m = MachineAgent("m1", position=(5, 5))
        result = m.step(tick=0, world_state={}, env_state={})
        assert result["production"] == 5.0


class TestEnergyUnitAgent:
    def test_energy_type(self):
        e = EnergyUnitAgent("e1", position=(0, 0))
        assert e.agent_type == "energy"
        assert e.params["production_rate"] == 20.0


class TestAgentRegistry:
    def test_register_and_get(self):
        reg = AgentRegistry()
        agent = BaseAgent("a1", position=(0, 0))
        reg.register(agent)
        assert reg.get("a1") is agent
        assert reg.count() == 1

    def test_unregister(self):
        reg = AgentRegistry()
        reg.register(BaseAgent("a1"))
        reg.unregister("a1")
        assert reg.get("a1") is None
        assert reg.count() == 0

    def test_get_by_type(self):
        reg = AgentRegistry()
        reg.register(VehicleAgent("v1"))
        reg.register(HumanAgent("h1"))
        reg.register(VehicleAgent("v2"))
        vehicles = reg.get_by_type("vehicle")
        assert len(vehicles) == 2

    def test_count_by_type(self):
        reg = AgentRegistry()
        reg.register(VehicleAgent("v1"))
        reg.register(HumanAgent("h1"))
        reg.register(MachineAgent("m1"))
        counts = reg.count_by_type()
        assert counts["vehicle"] == 1
        assert counts["human"] == 1
        assert counts["machine"] == 1


class TestInteractionSystem:
    def test_find_neighbors(self):
        agents = [
            BaseAgent("a1", position=(0, 0)),
            BaseAgent("a2", position=(0, 1)),
            BaseAgent("a3", position=(100, 100)),
        ]
        interact = InteractionSystem(interaction_range=5.0)
        neighbors = interact.find_neighbors(agents[0], agents)
        assert len(neighbors) == 1
        assert neighbors[0].id == "a2"

    def test_exchange_resources(self):
        a1 = BaseAgent("a1")
        a2 = BaseAgent("a2")
        interact = InteractionSystem()
        result = interact.exchange_resources(a1, a2, resource="energy", amount=10.0)
        assert result is True


class TestBehaviors:
    def test_rule_based_first_match(self):
        behavior = RuleBasedBehavior(rules=[
            (lambda s, n: s.get("urgent"), lambda s, n: {"action": "respond"}),
            (lambda s, n: True, lambda s, n: {"action": "idle"}),
        ])
        result = behavior.decide({"urgent": True}, [])
        assert result["action"] == "respond"

    def test_rule_based_fallback(self):
        behavior = RuleBasedBehavior(rules=[
            (lambda s, n: False, lambda s, n: {"action": "never"}),
            (lambda s, n: True, lambda s, n: {"action": "fallback"}),
        ])
        result = behavior.decide({}, [])
        assert result["action"] == "fallback"

    def test_probabilistic_behavior(self):
        behavior = ProbabilisticBehavior(
            actions={"move": 1.0, "stay": 0.0},
            seed=42,
        )
        for _ in range(5):
            result = behavior.decide({}, [])
            assert "action" in result


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
