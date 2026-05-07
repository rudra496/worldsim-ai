"""Data source interfaces for sensor data ingestion."""

from __future__ import annotations

import abc
import csv
import io
import json
import logging
import os
import random
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterator, List, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

@dataclass
class SensorReading:
    """A single sensor reading."""
    source: str
    sensor_id: str
    timestamp: float
    value: Any
    metadata: Dict[str, Any] = field(default_factory=dict)


class DataSource(abc.ABC):
    """Abstract base class for all data sources."""

    def __init__(self, name: str = "unnamed") -> None:
        self.name = name
        self._connected = False

    @abc.abstractmethod
    def connect(self) -> None: ...

    @abc.abstractmethod
    def read(self) -> Iterator[SensorReading]: ...

    @abc.abstractmethod
    def disconnect(self) -> None: ...

    @property
    def connected(self) -> bool:
        return self._connected


# ---------------------------------------------------------------------------
# MQTT Source
# ---------------------------------------------------------------------------

class MQTTSource(DataSource):
    """MQTT client for real-time sensor data.

    Requires ``paho-mqtt``. Falls back to a no-op warning if unavailable.
    """

    def __init__(
        self,
        name: str = "mqtt",
        broker_host: str = "localhost",
        broker_port: int = 1883,
        topics: Optional[List[str]] = None,
        qos: int = 0,
        format: str = "json",  # json | csv | binary
        **kwargs: Any,
    ) -> None:
        super().__init__(name)
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.topics = topics or []
        self.qos = qos
        self.format = format
        self._callbacks: Dict[str, Callable[[SensorReading], None]] = {}
        self._buffer: List[SensorReading] = []
        self._lock = threading.Lock()
        self._mqtt_client: Any = None

        try:
            import paho.mqtt.client as mqtt  # type: ignore
            self._mqtt = mqtt
        except ImportError:
            self._mqtt = None
            logger.warning("paho-mqtt not installed; MQTTSource will be a no-op")

    def connect(self) -> None:
        if self._mqtt is None:
            logger.warning("[%s] paho-mqtt unavailable – skipping connect", self.name)
            return
        client = self._mqtt.Client(self._mqtt.CallbackAPIVersion.VERSION2)
        client.on_connect = self._on_connect
        client.on_message = self._on_message
        client.connect(self.broker_host, self.broker_port)
        client.loop_start()
        self._mqtt_client = client
        self._connected = True

    def _on_connect(self, client: Any, flags: Any, reason_code: Any, properties: Any) -> None:
        for topic in self.topics:
            client.subscribe(topic, self.qos)

    def _on_message(self, client: Any, msg: Any) -> None:
        reading = self._parse_message(msg.topic, msg.payload)
        if reading:
            with self._lock:
                self._buffer.append(reading)
            for cb in self._callbacks.values():
                try:
                    cb(reading)
                except Exception:
                    logger.exception("MQTT callback error")

    def _parse_message(self, topic: str, payload: bytes) -> Optional[SensorReading]:
        try:
            if self.format == "json":
                data = json.loads(payload)
                return SensorReading(
                    source=self.name, sensor_id=topic,
                    timestamp=time.time(), value=data.get("value"),
                    metadata={"topic": topic, **{k: v for k, v in data.items() if k != "value"}},
                )
            return SensorReading(source=self.name, sensor_id=topic,
                                 timestamp=time.time(), value=payload.decode())
        except Exception:
            logger.exception("Failed to parse MQTT message on %s", topic)
            return None

    def read(self) -> Iterator[SensorReading]:
        while True:
            with self._lock:
                if self._buffer:
                    yield self._buffer.pop(0)
            time.sleep(0.05)

    def subscribe(self, topic: str, callback: Callable[[SensorReading], None]) -> None:
        self._callbacks[topic] = callback
        if self._mqtt_client and self._connected:
            self._mqtt_client.subscribe(topic, self.qos)

    def publish(self, topic: str, data: Any) -> None:
        if self._mqtt_client and self._connected:
            payload = json.dumps(data) if isinstance(data, (dict, list)) else str(data)
            self._mqtt_client.publish(topic, payload, self.qos)

    def disconnect(self) -> None:
        if self._mqtt_client:
            self._mqtt_client.loop_stop()
            self._mqtt_client.disconnect()
        self._connected = False


# ---------------------------------------------------------------------------
# File Source
# ---------------------------------------------------------------------------

class FileSource(DataSource):
    """Reads sensor data from CSV/JSON files, with optional tailing."""

    def __init__(
        self,
        name: str = "file",
        path: str = "data/sensors.csv",
        format: str = "csv",
        poll_interval: float = 1.0,
        tail: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(name)
        self.path = path
        self.format = format
        self.poll_interval = poll_interval
        self.tail = tail
        self._file_pos = 0
        self._stop_event = threading.Event()

    def connect(self) -> None:
        if not os.path.exists(self.path):
            logger.warning("[%s] File not found: %s", self.name, self.path)
            self._connected = False
            return
        self._file_pos = 0
        self._stop_event.clear()
        self._connected = True

    def read(self) -> Iterator[SensorReading]:
        while not self._stop_event.is_set() and self._connected:
            readings = self._read_new_lines()
            for r in readings:
                yield r
            if self.tail:
                time.sleep(self.poll_interval)
            else:
                break

    def _read_new_lines(self) -> List[SensorReading]:
        try:
            with open(self.path, "r") as f:
                f.seek(self._file_pos)
                new_lines = f.readlines()
                self._file_pos = f.tell()
        except FileNotFoundError:
            self._connected = False
            return []

        if not new_lines:
            return []

        if self.format == "jsonl":
            return self._parse_jsonl(new_lines)
        elif self.format == "json":
            return self._parse_json(new_lines)
        else:
            return self._parse_csv(new_lines)

    def _parse_csv(self, lines: List[str]) -> List[SensorReading]:
        if not lines or not lines[0].strip():
            return []
        reader = csv.DictReader(io.StringIO("".join(lines)))
        out: List[SensorReading] = []
        for row in reader:
            out.append(SensorReading(
                source=self.name,
                sensor_id=row.get("sensor_id", "unknown"),
                timestamp=float(row.get("timestamp", time.time())),
                value=float(row.get("value", 0)),
                metadata={k: v for k, v in row.items() if k not in ("sensor_id", "timestamp", "value")},
            ))
        return out

    def _parse_json(self, lines: List[str]) -> List[SensorReading]:
        try:
            data = json.loads("".join(lines))
            if isinstance(data, list):
                return [SensorReading(
                    source=self.name,
                    sensor_id=d.get("sensor_id", "unknown"),
                    timestamp=float(d.get("timestamp", time.time())),
                    value=d.get("value", 0),
                    metadata={k: v for k, v in d.items() if k not in ("sensor_id", "timestamp", "value")},
                ) for d in data]
        except json.JSONDecodeError:
            pass
        return []

    def _parse_jsonl(self, lines: List[str]) -> List[SensorReading]:
        out: List[SensorReading] = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
                out.append(SensorReading(
                    source=self.name,
                    sensor_id=d.get("sensor_id", "unknown"),
                    timestamp=float(d.get("timestamp", time.time())),
                    value=d.get("value", 0),
                    metadata={k: v for k, v in d.items() if k not in ("sensor_id", "timestamp", "value")},
                ))
            except json.JSONDecodeError:
                pass
        return out

    def disconnect(self) -> None:
        self._stop_event.set()
        self._connected = False


# ---------------------------------------------------------------------------
# API Source
# ---------------------------------------------------------------------------

class APISource(DataSource):
    """Pulls data from REST endpoints periodically."""

    def __init__(
        self,
        name: str = "api",
        url: str = "",
        poll_interval: float = 5.0,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(name)
        self.url = url
        self.poll_interval = poll_interval
        self.headers = headers or {}
        self.params = params or {}
        self._stop_event = threading.Event()

        try:
            import urllib.request  # stdlib – always available
            self._urllib = True
        except ImportError:
            self._urllib = False

    def connect(self) -> None:
        self._stop_event.clear()
        self._connected = True

    def read(self) -> Iterator[SensorReading]:
        while not self._stop_event.is_set() and self._connected:
            readings = self._fetch()
            for r in readings:
                yield r
            time.sleep(self.poll_interval)

    def _fetch(self) -> List[SensorReading]:
        if not self._urllib:
            return []
        try:
            import urllib.request
            import urllib.parse
            url = self.url
            if self.params:
                url += "?" + urllib.parse.urlencode(self.params)
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
            if isinstance(data, list):
                return [self._to_reading(d) for d in data]
            elif isinstance(data, dict):
                return [self._to_reading(data)]
            return []
        except Exception:
            logger.exception("[%s] API fetch failed", self.name)
            return []

    def _to_reading(self, d: Any) -> SensorReading:
        if isinstance(d, dict):
            return SensorReading(
                source=self.name,
                sensor_id=d.get("sensor_id", d.get("id", "unknown")),
                timestamp=float(d.get("timestamp", time.time())),
                value=d.get("value", d),
                metadata={k: v for k, v in d.items() if k not in ("sensor_id", "timestamp", "value", "id")},
            )
        return SensorReading(source=self.name, sensor_id="unknown",
                             timestamp=time.time(), value=d)

    def disconnect(self) -> None:
        self._stop_event.set()
        self._connected = False


# ---------------------------------------------------------------------------
# Simulator Source
# ---------------------------------------------------------------------------

class SimulatorSource(DataSource):
    """Generates synthetic sensor data for testing."""

    def __init__(
        self,
        name: str = "simulator",
        sensor_ids: Optional[List[str]] = None,
        interval: float = 1.0,
        base_values: Optional[Dict[str, float]] = None,
        noise_std: float = 1.0,
        drift_rate: float = 0.0,
        failure_rate: float = 0.0,
        **kwargs: Any,
    ) -> None:
        super().__init__(name)
        self.sensor_ids = sensor_ids or ["sim_sensor_0"]
        self.interval = interval
        self.base_values = base_values or {s: 20.0 for s in self.sensor_ids}
        self.noise_std = noise_std
        self.drift_rate = drift_rate
        self.failure_rate = failure_rate
        self._stop_event = threading.Event()
        self._drift_offsets: Dict[str, float] = {s: 0.0 for s in self.sensor_ids}
        self._tick = 0

    def connect(self) -> None:
        self._stop_event.clear()
        self._drift_offsets = {s: 0.0 for s in self.sensor_ids}
        self._tick = 0
        self._connected = True

    def read(self) -> Iterator[SensorReading]:
        while not self._stop_event.is_set() and self._connected:
            for sid in self.sensor_ids:
                # Failure injection
                if random.random() < self.failure_rate:
                    yield SensorReading(
                        source=self.name, sensor_id=sid,
                        timestamp=time.time(), value=None,
                        metadata={"status": "failure"},
                    )
                    continue

                drift = self._drift_offsets.get(sid, 0.0) + self.drift_rate
                self._drift_offsets[sid] = drift
                base = self.base_values.get(sid, 0.0) + drift
                value = random.gauss(base, self.noise_std)

                yield SensorReading(
                    source=self.name, sensor_id=sid,
                    timestamp=time.time(), value=round(value, 4),
                    metadata={"tick": self._tick, "status": "ok"},
                )
            self._tick += 1
            time.sleep(self.interval)

    def disconnect(self) -> None:
        self._stop_event.set()
        self._connected = False
