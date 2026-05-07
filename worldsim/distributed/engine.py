"""Distributed simulation engine — extends base engine for multi-node."""

from __future__ import annotations

import enum
import logging
import threading
import time
from typing import Any, Dict, List, Optional

from worldsim.distributed.node import NodeStatus, SimulationNode
from worldsim.distributed.partitioning import LoadBalancer, NodeLoad, SpatialPartitioner
from worldsim.distributed.protocol import AgentUpdate, MessageSerializer, SimState

logger = logging.getLogger(__name__)


class SyncStrategy(enum.Enum):
    BARRIER = "barrier"
    ASYNC = "async"
    HYBRID = "hybrid"


class DistributedEngine:
    """Manages a distributed simulation across multiple nodes.

    Features:
    - Spatial partitioning of agents
    - Inter-node synchronization (barrier, async, hybrid)
    - Graceful degradation on node failure
    - Load balancing
    """

    def __init__(
        self,
        num_nodes: int = 2,
        sync_strategy: SyncStrategy = SyncStrategy.BARRIER,
        world_width: float = 1000.0,
        world_height: float = 1000.0,
    ) -> None:
        self.sync_strategy = sync_strategy
        self._tick = 0
        self._running = False
        self._lock = threading.Lock()

        # Create nodes
        self.nodes: List[SimulationNode] = []
        for i in range(num_nodes):
            node = SimulationNode(node_id=f"node-{i}")
            self.nodes.append(node)

        # Wire nodes to each other
        for node in self.nodes:
            for other in self.nodes:
                if other.node_id != node.node_id:
                    node.register_remote_node(other)

        self.partitioner = SpatialPartitioner(world_width, world_height)
        self.load_balancer = LoadBalancer()
        self.serializer = MessageSerializer()

        # Agent store: agent_id -> {"position": [...], "state": {...}}
        self._agents: Dict[str, Dict[str, Any]] = {}

    def add_agent(self, agent_id: str, position: List[float], state: Optional[Dict[str, Any]] = None) -> None:
        self._agents[agent_id] = {
            "position": list(position),
            "state": state or {},
        }

    def _agent_obj(self, agent_id: str, data: Dict[str, Any]) -> Any:
        """Create a simple object with agent_id and position for partitioner."""
        class _A:
            pass
        a = _A()
        a.agent_id = agent_id
        a.position = data["position"]
        return a

    def partition_agents(self) -> Dict[int, List[str]]:
        """Partition all agents across nodes based on spatial position."""
        obj_list = [self._agent_obj(aid, d) for aid, d in self._agents.items()]
        assignments = self.partitioner.assign_agents_to_nodes(obj_list, len(self.nodes))

        for node in self.nodes:
            node.agent_ids = assignments.get(int(node.node_id.split("-")[1]), [])

        return assignments

    def start(self) -> None:
        self.partition_agents()
        for node in self.nodes:
            node.start(agent_ids=node.agent_ids)
        self._running = True
        self._tick = 0
        logger.info("DistributedEngine started with %d nodes", len(self.nodes))

    def stop(self) -> None:
        self._running = False
        for node in self.nodes:
            node.stop()
        logger.info("DistributedEngine stopped at tick %d", self._tick)

    def tick(self) -> int:
        """Advance one simulation tick with inter-node sync."""
        if not self._running:
            return self._tick

        self._tick += 1

        # Update each node's agents
        for node in self.nodes:
            for aid in node.agent_ids:
                if aid in self._agents:
                    data = self._agents[aid]
                    node.update_agent(AgentUpdate(
                        agent_id=aid, position=data["position"], state=data["state"],
                    ))
            node.advance_tick()

        # Sync
        if self.sync_strategy == SyncStrategy.BARRIER:
            self._barrier_sync()
        elif self.sync_strategy == SyncStrategy.HYBRID:
            self._hybrid_sync()
        # ASYNC: no sync

        return self._tick

    def _barrier_sync(self) -> None:
        """All-to-all barrier synchronization."""
        states = [node.get_state() for node in self.nodes if node.status == NodeStatus.RUNNING]
        for node in self.nodes:
            if node.status != NodeStatus.RUNNING:
                continue
            for state in states:
                if state.node_id != node.node_id:
                    node.receive_state(state.node_id, state)

    def _hybrid_sync(self) -> None:
        """Hybrid sync: barrier for nearby nodes, async for distant ones."""
        states = [node.get_state() for node in self.nodes if node.status == NodeStatus.RUNNING]
        node_ids = [n.node_id for n in self.nodes if n.status == NodeStatus.RUNNING]
        for node in self.nodes:
            if node.status != NodeStatus.RUNNING:
                continue
            idx = node_ids.index(node.node_id)
            for i, state in enumerate(states):
                if state.node_id == node.node_id:
                    continue
                # Sync with adjacent nodes (barrier), skip distant ones (async)
                if abs(i - idx) <= 1:
                    node.receive_state(state.node_id, state)

    def redistribute_agents(self, failed_node_id: str) -> None:
        """Redistribute agents from a failed node to healthy nodes."""
        failed = next((n for n in self.nodes if n.node_id == failed_node_id), None)
        if not failed:
            return

        failed.stop()
        orphan_agents = list(failed.agent_ids)
        healthy = [n for n in self.nodes if n.status == NodeStatus.RUNNING]

        if not healthy:
            logger.error("No healthy nodes to redistribute to")
            return

        per_node = len(orphan_agents) // len(healthy)
        for i, node in enumerate(healthy):
            start = i * per_node
            end = start + per_node if i < len(healthy) - 1 else len(orphan_agents)
            for aid in orphan_agents[start:end]:
                node.agent_ids.append(aid)

        failed.agent_ids.clear()
        logger.info("Redistributed %d agents from %s", len(orphan_agents), failed_node_id)

    def get_global_state(self) -> SimState:
        """Aggregate state from all running nodes."""
        all_updates: List[AgentUpdate] = []
        all_metrics: Dict[str, float] = {}
        for node in self.nodes:
            if node.status == NodeStatus.RUNNING:
                state = node.get_state()
                all_updates.extend(state.agent_updates)
                for k, v in state.metrics.items():
                    all_metrics[f"{node.node_id}.{k}"] = v
        return SimState(
            tick=self._tick,
            node_id="coordinator",
            agent_updates=all_updates,
            metrics=all_metrics,
        )

    @property
    def current_tick(self) -> int:
        return self._tick
