"""Tests for distributed simulation."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from worldsim.distributed.partitioning import SpatialPartitioner, LoadBalancer, NodeLoad
from worldsim.distributed.protocol import MessageSerializer, SimState, SyncRequest, SyncResponse, AgentUpdate
from worldsim.distributed.node import SimulationNode
from worldsim.distributed.engine import DistributedEngine, SyncStrategy


class TestSpatialPartitioner:
    def test_assign_agents_to_nodes(self):
        sp = SpatialPartitioner(world_width=50, world_height=50)

        class FakeAgent:
            def __init__(self, aid, pos):
                self.agent_id = aid
                self.position = pos

        agents = [FakeAgent(f"a{i}", [i % 50, i // 50]) for i in range(100)]
        assignments = sp.assign_agents_to_nodes(agents, num_nodes=4)
        assert len(assignments) == 4
        total = sum(len(v) for v in assignments.values())
        assert total == 100


class TestLoadBalancer:
    def test_compute_rebalancing_plan(self):
        lb = LoadBalancer()
        nodes = [
            NodeLoad(node_id=0, agent_count=80, cpu_load=0.9),
            NodeLoad(node_id=1, agent_count=20, cpu_load=0.2),
            NodeLoad(node_id=2, agent_count=30, cpu_load=0.3),
        ]
        assignments = {0: [f"a{i}" for i in range(80)],
                       1: [f"b{i}" for i in range(20)],
                       2: [f"c{i}" for i in range(30)]}
        plan = lb.compute_rebalancing_plan(nodes, assignments)
        assert hasattr(plan, "migrations")


class TestMessageSerializer:
    def test_serialize_deserialize(self):
        ms = MessageSerializer()
        state = {"tick": 42, "agents": [{"id": "a1", "x": 5, "y": 10}], "metrics": {"eff": 0.8}}
        serialized = ms.serialize(state)
        assert isinstance(serialized, bytes)
        restored = ms.deserialize(serialized)
        assert restored["tick"] == 42
        assert restored["agents"][0]["id"] == "a1"


class TestProtocolMessages:
    def test_sim_state(self):
        state = SimState(tick=10, node_id="n0")
        assert state.tick == 10
        assert state.node_id == "n0"

    def test_sync_request(self):
        req = SyncRequest(source_node="n0", target_node="n1", tick=10)
        assert req.source_node == "n0"

    def test_sync_response(self):
        state = SimState(tick=10)
        resp = SyncResponse(source_node="n0", target_node="n1", tick=10, accepted=True, state=state)
        assert resp.accepted

    def test_agent_update(self):
        au = AgentUpdate(agent_id="a1", position=[5, 10], state={"energy": 80})
        assert au.agent_id == "a1"


class TestSimulationNode:
    def test_start_stop(self):
        node = SimulationNode(node_id="node-0")
        node.start(agent_ids=["a1", "a2"])
        assert node.status.value == "running"
        node.stop()
        assert node.status.value == "stopped"

    def test_update_agent(self):
        node = SimulationNode(node_id="node-0")
        node.start()
        update = AgentUpdate(agent_id="a1", position=[5, 10], state={"energy": 80})
        node.update_agent(update)
        state = node.get_state()
        assert len(state.agent_updates) == 1


class TestDistributedEngine:
    def test_create_engine(self):
        de = DistributedEngine(num_nodes=2, sync_strategy=SyncStrategy.BARRIER)
        assert len(de.nodes) == 2

    def test_add_agent_and_partition(self):
        de = DistributedEngine(num_nodes=2, world_width=100, world_height=100)
        de.add_agent("a1", [10, 20])
        de.add_agent("a2", [80, 90])
        assignments = de.partition_agents()
        total = sum(len(v) for v in assignments.values())
        assert total == 2

    def test_sync_strategies(self):
        for strategy in [SyncStrategy.BARRIER, SyncStrategy.ASYNC, SyncStrategy.HYBRID]:
            de = DistributedEngine(num_nodes=2, sync_strategy=strategy)
            de.add_agent("a1", [10, 10])
            de.start()
            de.tick()
            de.stop()


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
