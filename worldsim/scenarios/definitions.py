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

SCENARIO_WEATHER = {
    "name": "weather_system",
    "display_name": "🌤️ Weather System Simulation",
    "description": "Simulates weather patterns including temperature, precipitation, and wind across geographic zones with environmental feedback loops.",
    "world_size": (80, 80),
    "duration": 600,
    "dt": 1.0,
    "deterministic": False,
    "seed": 42,
    "enable_predictor": True,
    "enable_optimizer": False,
    "energy_budget": 1000,
    "agents": {
        "human": 50,
        "vehicle": 30,
        "energy": 10,
    },
    "zones": [
        {"type": "park", "bounds": [0, 0, 20, 20], "population": 0, "energy_demand": 1},
        {"type": "residential", "bounds": [20, 0, 40, 20], "population": 600, "capacity": 700, "energy_demand": 60},
        {"type": "commercial", "bounds": [40, 0, 60, 20], "population": 250, "capacity": 350, "energy_demand": 70},
        {"type": "residential", "bounds": [60, 0, 80, 20], "population": 450, "capacity": 550, "energy_demand": 50},
        {"type": "road", "bounds": [0, 20, 80, 30], "population": 0, "energy_demand": 5},
        {"type": "residential", "bounds": [0, 30, 20, 50], "population": 500, "capacity": 600, "energy_demand": 55},
        {"type": "industrial", "bounds": [20, 30, 40, 50], "population": 80, "capacity": 150, "energy_demand": 130, "production_output": 200},
        {"type": "park", "bounds": [40, 30, 60, 50], "population": 0, "energy_demand": 1},
        {"type": "residential", "bounds": [60, 30, 80, 50], "population": 400, "capacity": 500, "energy_demand": 45},
        {"type": "road", "bounds": [0, 50, 80, 60], "population": 0, "energy_demand": 5},
        {"type": "power_plant", "bounds": [0, 60, 25, 80], "population": 0, "energy_demand": 0, "production_output": 350},
        {"type": "commercial", "bounds": [25, 60, 55, 80], "population": 300, "capacity": 400, "energy_demand": 80},
        {"type": "power_plant", "bounds": [55, 60, 80, 80], "population": 0, "energy_demand": 0, "production_output": 300},
    ],
    "metrics": ["stability", "resource_utilization", "total_energy_consumption"],
}

SCENARIO_POPULATION = {
    "name": "population_dynamics",
    "display_name": "👥 Population Dynamics",
    "description": "Models population growth, migration, and resource competition across connected urban and rural zones over time.",
    "world_size": (70, 70),
    "duration": 500,
    "dt": 1.0,
    "deterministic": False,
    "seed": 42,
    "enable_predictor": True,
    "enable_optimizer": True,
    "energy_budget": 2500,
    "agents": {
        "human": 100,
        "vehicle": 25,
        "energy": 8,
    },
    "zones": [
        {"type": "residential", "bounds": [0, 0, 25, 25], "population": 1000, "capacity": 1500, "energy_demand": 80},
        {"type": "commercial", "bounds": [25, 0, 45, 25], "population": 400, "capacity": 500, "energy_demand": 100},
        {"type": "residential", "bounds": [45, 0, 70, 25], "population": 700, "capacity": 1000, "energy_demand": 65},
        {"type": "road", "bounds": [0, 25, 70, 30], "population": 0, "energy_demand": 8},
        {"type": "residential", "bounds": [0, 30, 20, 50], "population": 300, "capacity": 600, "energy_demand": 30},
        {"type": "park", "bounds": [20, 30, 50, 50], "population": 0, "energy_demand": 2},
        {"type": "residential", "bounds": [50, 30, 70, 50], "population": 200, "capacity": 400, "energy_demand": 25},
        {"type": "road", "bounds": [0, 50, 70, 55], "population": 0, "energy_demand": 8},
        {"type": "industrial", "bounds": [0, 55, 35, 70], "population": 150, "capacity": 250, "energy_demand": 150, "production_output": 250},
        {"type": "power_plant", "bounds": [35, 55, 70, 70], "population": 0, "energy_demand": 0, "production_output": 400},
    ],
    "metrics": ["stability", "efficiency", "resource_utilization", "total_energy_consumption"],
}

SCENARIO_SUPPLY_CHAIN = {
    "name": "supply_chain",
    "display_name": "🔗 Supply Chain Logistics",
    "description": "Simulates a multi-node supply chain with factories, warehouses, distribution centers, and retail endpoints with delivery routing.",
    "world_size": (60, 60),
    "duration": 400,
    "dt": 1.0,
    "deterministic": True,
    "seed": 42,
    "enable_predictor": True,
    "enable_optimizer": True,
    "energy_budget": 3000,
    "agents": {
        "vehicle": 50,
        "machine": 20,
        "human": 30,
        "energy": 10,
    },
    "zones": [
        {"type": "industrial", "bounds": [0, 0, 20, 15], "population": 40, "capacity": 80, "energy_demand": 200, "production_output": 300},
        {"type": "industrial", "bounds": [40, 0, 60, 15], "population": 30, "capacity": 60, "energy_demand": 160, "production_output": 250},
        {"type": "warehouse", "bounds": [0, 15, 20, 30], "population": 15, "capacity": 40, "energy_demand": 40},
        {"type": "warehouse", "bounds": [40, 15, 60, 30], "population": 10, "capacity": 30, "energy_demand": 35},
        {"type": "road", "bounds": [0, 30, 60, 35], "population": 0, "energy_demand": 10},
        {"type": "commercial", "bounds": [0, 35, 20, 50], "population": 200, "capacity": 300, "energy_demand": 70},
        {"type": "commercial", "bounds": [20, 35, 40, 50], "population": 250, "capacity": 350, "energy_demand": 80},
        {"type": "commercial", "bounds": [40, 35, 60, 50], "population": 180, "capacity": 280, "energy_demand": 65},
        {"type": "power_plant", "bounds": [0, 50, 30, 60], "population": 0, "energy_demand": 0, "production_output": 500},
        {"type": "power_plant", "bounds": [30, 50, 60, 60], "population": 0, "energy_demand": 0, "production_output": 400},
    ],
    "metrics": ["efficiency", "throughput", "resource_utilization", "total_production"],
}

SCENARIO_AGRICULTURE = {
    "name": "smart_agriculture",
    "display_name": "🌾 Smart Agriculture",
    "description": "Simulates precision agriculture with crop zones, irrigation systems, weather dependency, and automated harvesting logistics.",
    "world_size": (60, 60),
    "duration": 500,
    "dt": 1.0,
    "deterministic": False,
    "seed": 42,
    "enable_predictor": True,
    "enable_optimizer": True,
    "energy_budget": 1500,
    "agents": {
        "human": 20,
        "vehicle": 15,
        "machine": 25,
        "energy": 5,
    },
    "zones": [
        {"type": "park", "bounds": [0, 0, 20, 20], "population": 0, "energy_demand": 3},
        {"type": "park", "bounds": [20, 0, 40, 20], "population": 0, "energy_demand": 3},
        {"type": "residential", "bounds": [40, 0, 60, 15], "population": 200, "capacity": 300, "energy_demand": 40},
        {"type": "road", "bounds": [40, 15, 60, 20], "population": 0, "energy_demand": 3},
        {"type": "park", "bounds": [0, 20, 20, 40], "population": 0, "energy_demand": 3},
        {"type": "industrial", "bounds": [20, 20, 40, 40], "population": 30, "capacity": 50, "energy_demand": 100, "production_output": 180},
        {"type": "road", "bounds": [0, 40, 60, 45], "population": 0, "energy_demand": 5},
        {"type": "warehouse", "bounds": [0, 45, 20, 60], "population": 10, "capacity": 30, "energy_demand": 25},
        {"type": "power_plant", "bounds": [20, 45, 40, 60], "population": 0, "energy_demand": 0, "production_output": 250},
        {"type": "commercial", "bounds": [40, 45, 60, 60], "population": 100, "capacity": 150, "energy_demand": 50},
    ],
    "metrics": ["efficiency", "total_production", "resource_utilization", "stability"],
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
    "weather_system": SCENARIO_WEATHER,
    "population_dynamics": SCENARIO_POPULATION,
    "supply_chain": SCENARIO_SUPPLY_CHAIN,
    "smart_agriculture": SCENARIO_AGRICULTURE,
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
