"""Digital Twin core — combines simulation, ingestion, and multi-agent system."""

from __future__ import annotations

import enum
import logging
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from worldsim.distributed.engine import DistributedEngine, SyncStrategy
from worldsim.io.alerting import AlertManager
from worldsim.io.ingestion import DataIngestionManager
from worldsim.twin.plugins import PluginManager

logger = logging.getLogger(__name__)


class SyncMode(enum.Enum):
    LIVE = "live"        # Real-time sync with real-world data
    REPLAY = "replay"    # Historical data replay
    HYBRID = "hybrid"    # Mix of live and simulated


@dataclass
class TwinState:
    tick: int = 0
    mode: SyncMode = SyncMode.LIVE
    agents: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    sensor_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class DigitalTwin:
    """Full digital twin platform combining simulation, ingestion, and multi-agent system.

    Synchronization modes:
    - **live**: real-time data from IoT sensors drives the simulation
    - **replay**: historical sensor data is replayed
    - **hybrid**: live sensors + simulated agents
    """

    def __init__(
        self,
        twin_id: Optional[str] = None,
        name: str = "digital-twin",
        sync_mode: SyncMode = SyncMode.LIVE,
        num_nodes: int = 1,
        world_width: float = 1000.0,
        world_height: float = 1000.0,
    ) -> None:
        self.twin_id = twin_id or str(uuid.uuid4())
        self.name = name
        self.sync_mode = sync_mode
        self.metadata: Dict[str, Any] = {
            "created": time.time(),
            "name": name,
            "sync_mode": sync_mode.value,
        }

        # Sub-systems
        self.engine = DistributedEngine(
            num_nodes=num_nodes,
            world_width=world_width,
            world_height=world_height,
        )
        self.ingestion = DataIngestionManager()
        self.alert_manager = AlertManager()
        self.plugin_manager = PluginManager()

        self._running = False
        self._tick = 0
        self._lock = threading.Lock()
        self._tick_thread: Optional[threading.Thread] = None
        self._tick_interval = 0.05  # 20 ticks/sec default

    def connect_live_source(self, source_name: str) -> None:
        """Start a registered ingestion source."""
        source = self.ingestion.sources.get(source_name)
        if source and not self._running:
            source.connect()
        logger.info("Connected live source: %s", source_name)

    def disconnect_live_source(self, source_name: str) -> None:
        source = self.ingestion.sources.get(source_name)
        if source:
            source.disconnect()

    def get_twin_state(self) -> TwinState:
        with self._lock:
            engine_state = self.engine.get_global_state()
            return TwinState(
                tick=self._tick,
                mode=self.sync_mode,
                agents={u.agent_id: {"position": u.position, "state": u.state}
                        for u in engine_state.agent_updates},
                sensor_data={},
                metadata=dict(self.metadata),
            )

    def start(self) -> None:
        """Start the digital twin: ingestion + simulation loop."""
        self.ingestion.start_all()
        self.engine.start()
        self.plugin_manager.execute_hook("on_scenario_start", {"twin_id": self.twin_id})
        self._running = True
        self._tick_thread = threading.Thread(target=self._tick_loop, daemon=True)
        self._tick_thread.start()
        logger.info("DigitalTwin %s started (mode=%s)", self.twin_id, self.sync_mode.value)

    def stop(self) -> None:
        self._running = False
        if self._tick_thread:
            self._tick_thread.join(timeout=5)
        self.ingestion.stop_all()
        self.engine.stop()
        self.plugin_manager.execute_hook("on_scenario_end", {"twin_id": self.twin_id})
        logger.info("DigitalTwin %s stopped at tick %d", self.twin_id, self._tick)

    def reset(self) -> None:
        self.stop()
        self._tick = 0
        self.ingestion.buffer.clear()
        logger.info("DigitalTwin %s reset", self.twin_id)

    def _tick_loop(self) -> None:
        while self._running:
            self.plugin_manager.execute_hook("on_tick_start", {"tick": self._tick, "twin_id": self.twin_id})
            with self._lock:
                self.engine.tick()
                self._tick += 1
            self.plugin_manager.execute_hook("on_tick_end", {"tick": self._tick, "twin_id": self.twin_id})
            time.sleep(self._tick_interval)

    @property
    def current_tick(self) -> int:
        return self._tick
