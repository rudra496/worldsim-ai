"""Simulation node: runs a subset of agents in a distributed setup."""

from __future__ import annotations

import enum
import logging
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from worldsim.distributed.protocol import (
    AgentUpdate,
    Heartbeat,
    MessageSerializer,
    SimState,
    SyncResponse,
)

logger = logging.getLogger(__name__)


class NodeStatus(enum.Enum):
    STARTING = "starting"
    RUNNING = "running"
    SYNCING = "syncing"
    DEGRADED = "degraded"
    STOPPING = "stopping"
    STOPPED = "stopped"


class SimulationNode:
    """Represents one node in the distributed simulation system.

    Manages a subset of agents, local state, heartbeat, and inter-node
    communication via a gRPC-like interface.
    """

    def __init__(
        self,
        node_id: str = "node-0",
        host: str = "localhost",
        port: int = 50051,
    ) -> None:
        self.node_id = node_id
        self.host = host
        self.port = port
        self.status = NodeStatus.STOPPED
        self.agent_ids: List[str] = []
        self._agent_states: Dict[str, Dict[str, Any]] = {}
        self._pending_incoming: Dict[str, List[AgentUpdate]] = {}
        self._tick = 0
        self._lock = threading.RLock()
        self._heartbeat_interval = 5.0
        self._heartbeat_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._remote_nodes: Dict[str, "SimulationNode"] = {}  # local references for testing
        self._metrics: Dict[str, float] = {}

    def start(self, agent_ids: Optional[List[str]] = None) -> None:
        self.agent_ids = list(agent_ids or [])
        self.status = NodeStatus.RUNNING
        self._stop_event.clear()
        self._tick = 0
        self._heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()
        logger.info("[%s] Started with %d agents", self.node_id, len(self.agent_ids))

    def stop(self) -> None:
        self.status = NodeStatus.STOPPING
        self._stop_event.set()
        if self._heartbeat_thread:
            self._heartbeat_thread.join(timeout=10)
        self.status = NodeStatus.STOPPED
        logger.info("[%s] Stopped", self.node_id)

    def update_agent(self, update: AgentUpdate) -> None:
        with self._lock:
            if update.removed:
                self._agent_states.pop(update.agent_id, None)
                if update.agent_id in self.agent_ids:
                    self.agent_ids.remove(update.agent_id)
            else:
                self._agent_states[update.agent_id] = {
                    "position": update.position,
                    "state": update.state,
                }
                if update.agent_id not in self.agent_ids:
                    self.agent_ids.append(update.agent_id)

    def get_state(self) -> SimState:
        with self._lock:
            updates = [
                AgentUpdate(
                    agent_id=aid,
                    position=st.get("position", []),
                    state=st.get("state", {}),
                )
                for aid, st in self._agent_states.items()
            ]
        return SimState(
            tick=self._tick,
            node_id=self.node_id,
            agent_updates=updates,
            metrics=dict(self._metrics),
        )

    def send_state(self, target_node_id: str, state: Optional[SimState] = None) -> SyncResponse:
        """Send local state to another node."""
        state = state or self.get_state()
        target = self._remote_nodes.get(target_node_id)
        if target is None:
            return SyncResponse(
                source_node=self.node_id, target_node=target_node_id,
                tick=self._tick, accepted=False,
                error=f"Node {target_node_id} not found",
            )
        return target.receive_state(self.node_id, state)

    def receive_state(self, source_node: str, state: SimState) -> SyncResponse:
        """Handle incoming state from another node."""
        with self._lock:
            for update in state.agent_updates:
                if update.agent_id in self.agent_ids:
                    self.update_agent(update)
        return SyncResponse(
            source_node=self.node_id, target_node=source_node,
            tick=self._tick, accepted=True,
        )

    def create_heartbeat(self) -> Heartbeat:
        with self._lock:
            return Heartbeat(
                node_id=self.node_id,
                timestamp=time.time(),
                agent_count=len(self.agent_ids),
                load=self._metrics.get("cpu_load", 0.0),
                status=self.status.value,
            )

    def _heartbeat_loop(self) -> None:
        while not self._stop_event.is_set():
            hb = self.create_heartbeat()
            for nid, node in self._remote_nodes.items():
                try:
                    node.receive_heartbeat(hb)
                except Exception:
                    logger.exception("[%s] Heartbeat to %s failed", self.node_id, nid)
            self._stop_event.wait(self._heartbeat_interval)

    def receive_heartbeat(self, heartbeat: Heartbeat) -> None:
        logger.debug("[%s] Heartbeat from %s: agents=%d load=%.2f",
                     self.node_id, heartbeat.node_id, heartbeat.agent_count, heartbeat.load)
        if heartbeat.status == "stopped":
            logger.warning("[%s] Node %s appears stopped", self.node_id, heartbeat.node_id)

    def register_remote_node(self, node: "SimulationNode") -> None:
        self._remote_nodes[node.node_id] = node

    def add_metric(self, name: str, value: float) -> None:
        self._metrics[name] = value

    @property
    def tick(self) -> int:
        return self._tick

    def advance_tick(self) -> int:
        self._tick += 1
        return self._tick
