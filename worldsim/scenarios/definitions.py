"""Predefined scenario configurations."""

from __future__ import annotations

from typing import Any, Dict, List, Optional


SCENARIO_SMART_CITY = {
    "name": "smart_city_traffic",
    "display_name": "🏙️ Smart City Traffic Simulation",
    "description": "Simulates urban traffic with vehicles and pedestrians across a city with residential, commercial, and industrial zones.",
    "world_size": (60, 60),
    "duration": 300,
    "dt": 1.0,
    "deterministic": True,
    "seed": 42,
    "enable_predictor": True,
    "enable_optimizer": True,
    "energy_budget": 2000,
    "agents": {
        "vehicle": 40,
        "human": 60,
        "energy": 5,
    },
    "zones": [
        {"type": "residential", "bounds": [0, 0, 20, 20], "population": 500, "capacity": 600, "energy_demand": 50},
        {"type": "commercial", "bounds": [20, 0, 40, 20], "population": 300, "capacity": 400, "energy_demand": 80},
        {"type": "industrial", "bounds": [40, 0, 60, 20], "population": 100, "capacity": 200, "energy_demand": 120, "production_output": 150},
        {"type": "road", "bounds": [0, 20, 60, 35], "population": 0, "energy_demand": 5},
        {"type": "park", "bounds": [0, 35, 30, 50], "population": 0, "energy_demand": 2},
        {"type": "power_plant", "bounds": [30, 35, 60, 50], "population": 0, "energy_demand": 0, "production_output": 300},
        {"type": "residential", "bounds": [0, 50, 30, 60], "population": 400, "capacity": 500, "energy_demand": 40},
        {"type": "commercial", "bounds": [30, 50, 60, 60], "population": 200, "capacity": 300, "energy_demand": 60},
    ],
    "metrics": ["efficiency", "throughput", "resource_utilization", "stability", "total_energy_consumption"],
}

SCENARIO_FACTORY = {
    "name": "factory_optimization",
    "display_name": "🏭 Factory Production Optimization",
    "description": "Optimizes production in a factory with machines, workers, and energy supply constraints.",
    "world_size": (40, 40),
    "duration": 500,
    "dt": 1.0,
    "deterministic": True,
    "seed": 42,
    "enable_predictor": True,
    "enable_optimizer": True,
    "energy_budget": 5000,
    "agents": {
        "machine": 30,
        "human": 20,
        "vehicle": 10,
        "energy": 8,
    },
    "zones": [
        {"type": "industrial", "bounds": [0, 0, 40, 25], "population": 50, "capacity": 100, "energy_demand": 200, "production_output": 250},
        {"type": "warehouse", "bounds": [0, 25, 20, 40], "population": 10, "capacity": 50, "energy_demand": 30},
        {"type": "power_plant", "bounds": [20, 25, 40, 40], "population": 5, "capacity": 20, "energy_demand": 0, "production_output": 400},
    ],
    "metrics": ["efficiency", "total_production", "resource_utilization", "stability"],
}

SCENARIO_ENERGY = {
    "name": "energy_balancing",
    "display_name": "⚡ Energy Consumption Balancing",
    "description": "Balances energy production and consumption across a grid with varying demand patterns.",
    "world_size": (50, 50),
    "duration": 400,
    "dt": 1.0,
    "deterministic": True,
    "seed": 42,
    "enable_predictor": True,
    "enable_optimizer": True,
    "energy_budget": 3000,
    "agents": {
        "energy": 15,
        "vehicle": 20,
        "human": 40,
        "machine": 10,
    },
    "zones": [
        {"type": "power_plant", "bounds": [0, 0, 15, 15], "population": 0, "energy_demand": 0, "production_output": 500},
        {"type": "power_plant", "bounds": [35, 35, 50, 50], "population": 0, "energy_demand": 0, "production_output": 400},
        {"type": "residential", "bounds": [15, 0, 35, 15], "population": 800, "capacity": 1000, "energy_demand": 100},
        {"type": "residential", "bounds": [0, 15, 15, 35], "population": 600, "capacity": 800, "energy_demand": 80},
        {"type": "commercial", "bounds": [15, 15, 35, 35], "population": 300, "capacity": 400, "energy_demand": 150},
        {"type": "industrial", "bounds": [35, 15, 50, 35], "population": 100, "capacity": 200, "energy_demand": 250, "production_output": 300},
        {"type": "road", "bounds": [0, 35, 50, 40], "population": 0, "energy_demand": 10},
        {"type": "park", "bounds": [15, 40, 35, 50], "population": 0, "energy_demand": 2},
    ],
    "metrics": ["efficiency", "energy_balance", "resource_utilization", "stability", "total_energy_consumption"],
}

SCENARIO_EMERGENCY = {
    "name": "emergency_failure",
    "display_name": "🚨 Emergency Failure Simulation",
    "description": "Simulates system failures (power outages, machine breakdowns) and tests system resilience and recovery.",
    "world_size": (50, 50),
    "duration": 400,
    "dt": 1.0,
    "deterministic": True,
    "seed": 42,
    "enable_predictor": True,
    "enable_optimizer": True,
    "energy_budget": 2000,
    "agents": {
        "machine": 25,
        "vehicle": 15,
        "human": 30,
        "energy": 6,
    },
    "zones": [
        {"type": "industrial", "bounds": [0, 0, 25, 25], "population": 40, "capacity": 80, "energy_demand": 180, "production_output": 200},
        {"type": "power_plant", "bounds": [25, 0, 50, 15], "population": 0, "energy_demand": 0, "production_output": 350},
        {"type": "residential", "bounds": [0, 25, 25, 40], "population": 500, "capacity": 600, "energy_demand": 60},
        {"type": "commercial", "bounds": [25, 25, 50, 40], "population": 200, "capacity": 300, "energy_demand": 90},
        {"type": "road", "bounds": [0, 40, 50, 45], "population": 0, "energy_demand": 5},
        {"type": "water_treatment", "bounds": [25, 40, 50, 50], "population": 10, "capacity": 30, "energy_demand": 40},
    ],
    "metrics": ["efficiency", "stability", "resource_utilization", "total_production", "total_energy_consumption"],
}

_ALL_SCENARIOS = {
    "smart_city_traffic": SCENARIO_SMART_CITY,
    "factory_optimization": SCENARIO_FACTORY,
    "energy_balancing": SCENARIO_ENERGY,
    "emergency_failure": SCENARIO_EMERGENCY,
}


def get_scenario(name: str) -> Optional[Dict[str, Any]]:
    """Get a scenario config by name."""
    return _ALL_SCENARIOS.get(name)


def list_scenarios() -> List[str]:
    """List all available scenario names."""
    return list(_ALL_SCENARIOS.keys())


def list_scenario_info() -> List[Dict[str, str]]:
    """Get info about all scenarios."""
    return [
        {"name": k, "display_name": v["display_name"], "description": v["description"]}
        for k, v in _ALL_SCENARIOS.items()
    ]
