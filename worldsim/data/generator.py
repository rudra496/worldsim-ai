"""Synthetic data generation and validation for simulations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np


class DataValidator:
    """Validates simulation data against expected schemas."""

    @staticmethod
    def validate_agent_data(data: Dict[str, Any]) -> List[str]:
        """Validate agent configuration data."""
        errors = []
        if "id" not in data:
            errors.append("Missing 'id' field")
        if "agent_type" not in data:
            errors.append("Missing 'agent_type' field")
        if "position" in data:
            pos = data["position"]
            if not isinstance(pos, (list, tuple)) or len(pos) != 2:
                errors.append("'position' must be a 2-element list/tuple")
        return errors

    @staticmethod
    def validate_scenario(data: Dict[str, Any]) -> List[str]:
        """Validate scenario configuration."""
        errors = []
        required = ["name", "duration", "world_size"]
        for field in required:
            if field not in data:
                errors.append(f"Missing '{field}' field")
        return errors

    @staticmethod
    def validate_world_config(data: Dict[str, Any]) -> List[str]:
        errors = []
        if "width" in data and data["width"] <= 0:
            errors.append("'width' must be positive")
        if "height" in data and data["height"] <= 0:
            errors.append("'height' must be positive")
        return errors


class SyntheticDataGenerator:
    """
    Generates realistic synthetic data for simulations.

    Can create agent populations, environment configs, and scenario data.
    """

    def __init__(self, seed: Optional[int] = None):
        self._rng = np.random.default_rng(seed)

    def generate_agents(
        self,
        count: int,
        world_size: tuple = (50, 50),
        agent_types: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Generate a population of agents with random positions and types."""
        agent_types = agent_types or ["vehicle", "human", "machine", "energy"]
        agents = []
        type_weights = [0.3, 0.4, 0.15, 0.15] if len(agent_types) == 4 else None

        for i in range(count):
            atype = self._rng.choice(agent_types, p=type_weights) if type_weights else agent_types[i % len(agent_types)]
            pos = (
                int(self._rng.integers(0, world_size[0])),
                int(self._rng.integers(0, world_size[1])),
            )
            agent = {
                "id": f"{atype}_{i:04d}",
                "agent_type": atype,
                "position": list(pos),
                "energy": float(self._rng.uniform(50, 100)),
                "speed": float(self._rng.uniform(0.5, 3.0)),
                "production_rate": float(self._rng.uniform(0, 20)),
                "energy_cost": float(self._rng.uniform(0.5, 15)),
            }
            agents.append(agent)
        return agents

    def generate_world_config(self, width: int = 50, height: int = 50) -> Dict[str, Any]:
        """Generate a world configuration with zones."""
        zones = [
            {"type": "residential", "bounds": [0, 0, width // 3, height // 3],
             "population": float(self._rng.integers(100, 500))},
            {"type": "commercial", "bounds": [width // 3, 0, 2 * width // 3, height // 3],
             "population": float(self._rng.integers(50, 200))},
            {"type": "industrial", "bounds": [2 * width // 3, 0, width, height // 3],
             "population": float(self._rng.integers(20, 100))},
            {"type": "road", "bounds": [0, height // 3, width, 2 * height // 3],
             "population": 0},
            {"type": "park", "bounds": [0, 2 * height // 3, width // 2, height],
             "population": 0},
            {"type": "power_plant", "bounds": [width // 2, 2 * height // 3, width, height],
             "population": 0},
        ]
        return {"width": width, "height": height, "zones": zones}

    def generate_time_series(self, length: int, base: float = 100.0,
                              noise: float = 10.0, trend: float = 0.0) -> List[float]:
        """Generate a time series with noise and optional trend."""
        t = np.arange(length)
        trend_line = base + trend * t
        noise_vals = self._rng.normal(0, noise, length)
        return (trend_line + noise_vals).tolist()

    def generate_traffic_matrix(self, size: int = 50, density: float = 0.3) -> List[List[float]]:
        """Generate a traffic density matrix."""
        matrix = self._rng.random((size, size))
        mask = self._rng.random((size, size)) < density
        return (matrix * mask).tolist()

    @staticmethod
    def load_config(path: str) -> Dict[str, Any]:
        """Load a JSON config file."""
        p = Path(path)
        if p.suffix == ".json":
            return json.loads(p.read_text())
        raise ValueError(f"Unsupported config format: {p.suffix}")
