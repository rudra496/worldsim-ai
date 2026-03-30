"""World representations — grid-based and graph-based environments."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


class ZoneType(enum.Enum):
    RESIDENTIAL = "residential"
    INDUSTRIAL = "industrial"
    COMMERCIAL = "commercial"
    ROAD = "road"
    PARK = "park"
    POWER_PLANT = "power_plant"
    WATER_TREATMENT = "water_treatment"
    WAREHOUSE = "warehouse"


@dataclass
class Zone:
    """A zone in the environment with a type and properties."""
    zone_type: ZoneType
    bounds: Tuple[int, int, int, int]  # x1, y1, x2, y2
    population: float = 0.0
    capacity: float = 100.0
    energy_demand: float = 10.0
    production_output: float = 0.0

    @property
    def utilization(self) -> float:
        return min(1.0, self.population / self.capacity) if self.capacity > 0 else 0.0

    def contains(self, x: int, y: int) -> bool:
        return (self.bounds[0] <= x < self.bounds[2] and
                self.bounds[1] <= y < self.bounds[3])


class GridWorld:
    """
    2D grid-based world representation.

    Each cell has a type and can hold resources.

    Usage:
        world = GridWorld(width=100, height=100)
        world.add_zone(Zone(ZoneType.RESIDENTIAL, (0, 0, 20, 20)))
        state = world.step(tick=1, actions={})
    """

    def __init__(self, width: int = 50, height: int = 50):
        self.width = width
        self.height = height
        self.grid: np.ndarray = np.zeros((height, width), dtype=np.int8)  # 0=empty
        self.resource_grid: np.ndarray = np.zeros((height, width), dtype=np.float32)
        self.traffic_grid: np.ndarray = np.zeros((height, width), dtype=np.float32)
        self.zones: List[Zone] = []

    def add_zone(self, zone: Zone) -> None:
        self.zones.append(zone)
        x1, y1, x2, y2 = zone.bounds
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(self.width, x2), min(self.height, y2)
        zone_id = list(ZoneType).index(zone.zone_type) + 1
        self.grid[y1:y2, x1:x2] = zone_id

    def get_zone_at(self, x: int, y: int) -> Optional[Zone]:
        for zone in self.zones:
            if zone.contains(x, y):
                return zone
        return None

    def update_traffic(self, x: int, y: int, amount: float = 1.0) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            self.traffic_grid[y, x] += amount

    def step(self, tick: int, state: Dict[str, Any]) -> Dict[str, Any]:
        """Advance the environment by one tick."""
        # Decay traffic (simulate movement)
        self.traffic_grid *= 0.95

        # Compute environment metrics
        total_energy_demand = sum(z.energy_demand * z.utilization for z in self.zones)
        total_production = sum(z.production_output for z in self.zones)
        total_traffic = float(np.sum(self.traffic_grid))
        max_traffic = float(np.max(self.traffic_grid)) if self.traffic_grid.size > 0 else 0.0
        avg_traffic = float(np.mean(self.traffic_grid)) if self.traffic_grid.size > 0 else 0.0

        return {
            "width": self.width,
            "height": self.height,
            "zone_count": len(self.zones),
            "total_energy_demand": total_energy_demand,
            "total_production": total_production,
            "energy_balance": total_production - total_energy_demand,
            "total_traffic": total_traffic,
            "max_traffic": max_traffic,
            "avg_traffic": avg_traffic,
            "traffic_grid_shape": list(self.traffic_grid.shape),
        }

    def get_traffic_snapshot(self) -> List[List[float]]:
        return self.traffic_grid.tolist()

    def reset(self) -> None:
        self.traffic_grid[:] = 0


class GraphWorld:
    """
    Graph-based world — nodes and edges representing a network.

    Useful for modeling energy grids, transportation networks, logistics.
    """

    def __init__(self):
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: Dict[str, List[Tuple[str, float]]] = {}
        self._edge_cache: Dict[str, float] = {}

    def add_node(self, node_id: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        self.nodes[node_id] = attributes or {}
        if node_id not in self.edges:
            self.edges[node_id] = []

    def add_edge(self, node_a: str, node_b: str, weight: float = 1.0) -> None:
        self.edges.setdefault(node_a, []).append((node_b, weight))
        self.edges.setdefault(node_b, []).append((node_a, weight))
        self._edge_cache[f"{node_a}-{node_b}"] = weight
        self._edge_cache[f"{node_b}-{node_a}"] = weight

    def get_neighbors(self, node_id: str) -> List[Tuple[str, float]]:
        return self.edges.get(node_id, [])

    def step(self, tick: int, state: Dict[str, Any]) -> Dict[str, Any]:
        total_nodes = len(self.nodes)
        total_edges = len(self._edge_cache) // 2  # undirected
        total_weight = sum(self._edge_cache.values()) / 2

        return {
            "node_count": total_nodes,
            "edge_count": total_edges,
            "total_weight": total_weight,
            "avg_degree": (2 * total_edges / total_nodes) if total_nodes > 0 else 0.0,
        }
