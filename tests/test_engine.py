"""Tests for the simulation engine."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from worldsim.core.engine import SimulationEngine, SimulationConfig
from worldsim.core.state import StateManager, StateSnapshot
from worldsim.core.events import EventBus, Event, EventType
from worldsim.agents.models import VehicleAgent, HumanAgent, MachineAgent
from worldsim.environment.world import GridWorld, Zone, ZoneType
from worldsim.scenarios.engine import ScenarioEngine


def test_state_manager():
    sm = StateManager()
    sm.set("test", 42)
    assert sm.get("test") == 42
    snap = sm.snapshot(tick=0)
    assert snap.data["test"] == 42
    print("✓ StateManager")


def test_event_bus():
    bus = EventBus()
    received = []
    bus.subscribe(EventType.TICK, lambda e: received.append(e.tick))
    bus.publish(Event(type=EventType.TICK, tick=1))
    bus.publish(Event(type=EventType.TICK, tick=2))
    assert len(received) == 2
    assert received == [1, 2]
    print("✓ EventBus")


def test_simulation_engine_basic():
    config = SimulationConfig(max_ticks=10, seed=42)
    engine = SimulationEngine(config=config)
    world = GridWorld(width=10, height=10)
    engine.register_environment(world)

    agents = [
        VehicleAgent("v1", position=(5, 5)),
        HumanAgent("h1", position=(3, 3)),
        MachineAgent("m1", position=(7, 7)),
    ]
    engine.register_agents(agents)

    results = engine.run(ticks=10)
    assert len(results) == 10
    assert results[0]["tick"] == 0
    assert results[9]["tick"] == 9
    assert "metrics" in results[0]
    print("✓ SimulationEngine basic run")


def test_deterministic_mode():
    results_a = []
    for _ in range(2):
        config = SimulationConfig(max_ticks=5, seed=42, deterministic=True)
        engine = SimulationEngine(config=config)
        world = GridWorld(width=10, height=10)
        engine.register_environment(world)
        engine.register_agents([VehicleAgent(f"v{i}", position=(i, i)) for i in range(3)])
        engine.run()
        results_a.append(engine.get_results())

    # Same seed should produce same agent counts (state is deterministic)
    assert results_a[0][0]["metrics"]["agent_count"] == results_a[1][0]["metrics"]["agent_count"]
    print("✓ Deterministic mode")


def test_scenario_engine():
    se = ScenarioEngine()
    result = se.run_scenario("smart_city_traffic", ticks=20)
    assert result["scenario"] == "smart_city_traffic"
    assert result["summary"]["ticks"] == 20
    assert "avg_efficiency" in result["summary"]
    print("✓ ScenarioEngine")


def test_grid_world():
    world = GridWorld(width=20, height=20)
    world.add_zone(Zone(ZoneType.RESIDENTIAL, (0, 0, 10, 10), population=100))
    env_state = world.step(tick=1, state={})
    assert env_state["zone_count"] == 1
    assert env_state["width"] == 20
    print("✓ GridWorld")


def test_all_scenarios():
    se = ScenarioEngine()
    for name in se.list_available():
        result = se.run_scenario(name, ticks=10)
        assert result["summary"]["ticks"] == 10
        print(f"  ✓ Scenario: {name}")


if __name__ == "__main__":
    print("Running WorldSim AI tests...\n")
    test_state_manager()
    test_event_bus()
    test_simulation_engine_basic()
    test_deterministic_mode()
    test_grid_world()
    test_scenario_engine()
    test_all_scenarios()
    print(f"\n✅ All tests passed!")
