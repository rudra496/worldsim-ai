"""Scenario engine — define, configure, and run simulation scenarios."""

from .definitions import (
    SCENARIO_SMART_CITY,
    SCENARIO_FACTORY,
    SCENARIO_ENERGY,
    SCENARIO_EMERGENCY,
    SCENARIO_WEATHER,
    SCENARIO_POPULATION,
    SCENARIO_SUPPLY_CHAIN,
    SCENARIO_AGRICULTURE,
    get_scenario,
    list_scenarios,
)

__all__ = [
    "SCENARIO_SMART_CITY", "SCENARIO_FACTORY", "SCENARIO_ENERGY", "SCENARIO_EMERGENCY",
    "SCENARIO_WEATHER", "SCENARIO_POPULATION", "SCENARIO_SUPPLY_CHAIN", "SCENARIO_AGRICULTURE",
    "get_scenario", "list_scenarios",
]
