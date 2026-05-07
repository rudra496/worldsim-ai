"""Tests for environment — world, resources."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from worldsim.environment.world import GridWorld, GraphWorld, Zone, ZoneType
from worldsim.environment.resources import ResourceManager, ResourceType, ResourceBucket


class TestGridWorld:
    def test_create_world(self):
        world = GridWorld(width=20, height=20)
        assert world.width == 20
        assert world.height == 20

    def test_add_zone(self):
        world = GridWorld(width=20, height=20)
        zone = Zone(ZoneType.RESIDENTIAL, (0, 0, 10, 10), population=100)
        world.add_zone(zone)
        assert len(world.zones) == 1

    def test_step(self):
        world = GridWorld(width=20, height=20)
        world.add_zone(Zone(ZoneType.RESIDENTIAL, (0, 0, 10, 10)))
        state = world.step(tick=1, state={})
        assert state["zone_count"] == 1
        assert state["width"] == 20

    def test_zone_types(self):
        world = GridWorld(width=50, height=50)
        for zt in ZoneType:
            world.add_zone(Zone(zt, (0, 0, 10, 10)))
        assert len(world.zones) == len(ZoneType)


class TestGraphWorld:
    def test_create_graph(self):
        gw = GraphWorld()
        gw.add_node("A", {"type": "residential"})
        gw.add_node("B", {"type": "commercial"})
        gw.add_edge("A", "B", weight=5)
        state = gw.step(tick=0, state={})
        assert state["node_count"] == 2
        assert state["edge_count"] == 1

    def test_get_neighbors(self):
        gw = GraphWorld()
        gw.add_node("A")
        gw.add_node("B")
        gw.add_edge("A", "B", weight=3)
        neighbors = gw.get_neighbors("A")
        assert len(neighbors) == 1
        assert neighbors[0][0] == "B"


class TestZone:
    def test_contains(self):
        zone = Zone(ZoneType.RESIDENTIAL, (0, 0, 10, 10))
        assert zone.contains(5, 5)
        assert not zone.contains(15, 5)

    def test_zone_type(self):
        zone = Zone(ZoneType.INDUSTRIAL, (0, 0, 10, 10))
        assert zone.zone_type == ZoneType.INDUSTRIAL


class TestResourceManager:
    def test_add_resource(self):
        rm = ResourceManager()
        rm.add_resource(ResourceType.ENERGY, capacity=1000, production_rate=50)
        bucket = rm.get(ResourceType.ENERGY)
        assert bucket is not None
        assert bucket.capacity == 1000

    def test_produce_and_consume(self):
        rm = ResourceManager()
        rm.add_resource(ResourceType.ENERGY, capacity=1000, current=0, production_rate=50)
        rm.produce(ResourceType.ENERGY, 100)
        bucket = rm.get(ResourceType.ENERGY)
        assert bucket.current == 100
        rm.consume(ResourceType.ENERGY, 30)
        assert bucket.current == 70

    def test_step(self):
        rm = ResourceManager()
        rm.add_resource(ResourceType.ENERGY, capacity=1000,
                        current=500, production_rate=10, consumption_rate=5)
        rm.step()
        bucket = rm.get(ResourceType.ENERGY)
        assert bucket.current > 500

    def test_get_summary(self):
        rm = ResourceManager()
        rm.add_resource(ResourceType.ENERGY, capacity=1000, current=500)
        summary = rm.get_summary()
        assert isinstance(summary, dict)


class TestResourceBucket:
    def test_utilization(self):
        bucket = ResourceBucket(ResourceType.ENERGY, capacity=100, current=50)
        assert bucket.utilization == 0.5

    def test_net_flow(self):
        bucket = ResourceBucket(ResourceType.ENERGY, production_rate=10, consumption_rate=5)
        assert bucket.net_flow == 5.0

    def test_step(self):
        bucket = ResourceBucket(ResourceType.ENERGY, capacity=100, current=50,
                                production_rate=10, consumption_rate=3)
        result = bucket.step()
        assert isinstance(result, dict)


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
