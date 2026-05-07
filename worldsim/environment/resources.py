"""Resource management — tracking production, consumption, and allocation."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class ResourceType(enum.Enum):
    ENERGY = "energy"
    WATER = "water"
    MATERIALS = "materials"
    BANDWIDTH = "bandwidth"


@dataclass
class ResourceBucket:
    """A bucket of a specific resource with production and consumption tracking."""
    resource_type: ResourceType
    capacity: float = 1000.0
    current: float = 500.0
    production_rate: float = 10.0
    consumption_rate: float = 5.0
    history: List[float] = field(default_factory=list)

    @property
    def utilization(self) -> float:
        return self.current / self.capacity if self.capacity > 0 else 0.0

    @property
    def net_flow(self) -> float:
        return self.production_rate - self.consumption_rate

    def step(self) -> Dict[str, float]:
        """Advance resource one tick."""
        self.current += self.net_flow
        self.current = max(0.0, min(self.capacity, self.current))
        self.history.append(self.current)
        if len(self.history) > 10000:
            self.history = self.history[-10000:]
        return {
            "current": self.current,
            "utilization": self.utilization,
            "net_flow": self.net_flow,
            "production": self.production_rate,
            "consumption": self.consumption_rate,
        }


class ResourceManager:
    """
    Manages all resources in the simulation.

    Usage:
        rm = ResourceManager()
        rm.add_resource(ResourceType.ENERGY, capacity=5000, current=3000)
        rm.step()
    """

    def __init__(self):
        self._resources: Dict[ResourceType, ResourceBucket] = {}

    def add_resource(
        self,
        resource_type: ResourceType,
        capacity: float = 1000.0,
        current: Optional[float] = None,
        production_rate: float = 10.0,
        consumption_rate: float = 5.0,
    ) -> None:
        self._resources[resource_type] = ResourceBucket(
            resource_type=resource_type,
            capacity=capacity,
            current=current if current is not None else capacity * 0.5,
            production_rate=production_rate,
            consumption_rate=consumption_rate,
        )

    def get(self, resource_type: ResourceType) -> Optional[ResourceBucket]:
        return self._resources.get(resource_type)

    def consume(self, resource_type: ResourceType, amount: float) -> bool:
        bucket = self._resources.get(resource_type)
        if bucket and bucket.current >= amount:
            bucket.current -= amount
            bucket.consumption_rate = amount
            return True
        return False

    def produce(self, resource_type: ResourceType, amount: float) -> float:
        bucket = self._resources.get(resource_type)
        if not bucket:
            return 0.0
        space = bucket.capacity - bucket.current
        added = min(amount, space)
        bucket.current += added
        bucket.production_rate = amount
        return added

    def step(self) -> Dict[str, Dict[str, float]]:
        result = {}
        for rtype, bucket in self._resources.items():
            result[rtype.value] = bucket.step()
        return result

    def get_all_state(self) -> Dict[str, Any]:
        return {
            rt.value: {"current": b.current, "capacity": b.capacity, "utilization": b.utilization}
            for rt, b in self._resources.items()
        }

    def get_summary(self) -> Dict[str, Any]:
        return {
            "resource_types": len(self._resources),
            "resources": self.get_all_state(),
        }
