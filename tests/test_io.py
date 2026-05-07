"""Tests for IO modules — ingestion, alerting, sources."""

import os
import sys
import tempfile
import json
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from worldsim.io.ingestion import DataBuffer, DataTransformer, DataIngestionManager
from worldsim.io.alerting import AlertManager, AlertLevel
from worldsim.io.sources import SimulatorSource, FileSource, SensorReading
from worldsim.io.ingestion import TransformConfig


class TestDataBuffer:
    def test_put_and_get_latest(self):
        buf = DataBuffer(max_size=100)
        buf.put(SensorReading("src", "s1", time.time(), 42.0))
        buf.put(SensorReading("src", "s2", time.time(), 43.0))
        latest = buf.get_latest("s1")
        assert latest is not None
        assert latest.value == 42.0

    def test_ring_buffer(self):
        buf = DataBuffer(max_size=5)
        for i in range(10):
            buf.put(SensorReading("src", f"s{i}", time.time(), float(i)))
        assert buf.size == 5

    def test_get_recent(self):
        buf = DataBuffer(max_size=100)
        now = time.time()
        buf.put(SensorReading("src", "s1", now - 120, 1.0))
        buf.put(SensorReading("src", "s2", now, 2.0))
        recent = buf.get_recent(seconds=60.0)
        assert len(recent) == 1

    def test_get_by_source(self):
        buf = DataBuffer(max_size=100)
        buf.put(SensorReading("mqtt", "s1", time.time(), 1.0))
        buf.put(SensorReading("file", "s2", time.time(), 2.0))
        buf.put(SensorReading("mqtt", "s3", time.time(), 3.0))
        mqtt_readings = buf.get_by_source("mqtt")
        assert len(mqtt_readings) == 2


class TestDataTransformer:
    def test_transform_mapping(self):
        dt = DataTransformer()
        config = TransformConfig(
            sensor_id="sensor_1",
            entity_id="agent_vehicle_001",
            scale=2.0,
        )
        dt.add_mapping(config)
        reading = SensorReading("mqtt", "sensor_1", time.time(), 42.0)
        result = dt.transform(reading)
        assert result is not None


class TestAlertManager:
    def test_no_alert(self):
        am = AlertManager()
        am.set_threshold("temp", crit_max=100.0)
        alerts = am.check_threshold("temp", 50.0)
        assert len(alerts) == 0

    def test_critical_alert(self):
        am = AlertManager()
        am.set_threshold("temp", crit_max=100.0)
        alerts = am.check_threshold("temp", 150.0)
        assert len(alerts) == 1
        assert alerts[0].level == AlertLevel.CRITICAL

    def test_warning_alert(self):
        am = AlertManager()
        am.set_threshold("temp", warn_max=80.0, crit_max=100.0)
        alerts = am.check_threshold("temp", 90.0)
        assert len(alerts) == 1
        assert alerts[0].level == AlertLevel.WARNING

    def test_get_history(self):
        am = AlertManager()
        am.set_threshold("temp", crit_max=100.0)
        am.check_threshold("temp", 150.0)
        history = am.get_history()
        assert len(history) == 1


class TestSimulatorSource:
    def test_connect_and_read(self):
        src = SimulatorSource(
            sensor_ids=["s1", "s2"],
            interval=0.01,
            noise_std=1.0,
        )
        src.connect()
        readings = []
        for reading in src.read():
            readings.append(reading)
            if len(readings) >= 4:
                break
        src.disconnect()
        assert len(readings) == 4
        assert readings[0].source == "simulator"

    def test_failure_injection(self):
        src = SimulatorSource(
            sensor_ids=["s1"],
            interval=0.01,
            failure_rate=1.0,
        )
        src.connect()
        for reading in src.read():
            assert reading.value is None
            assert reading.metadata["status"] == "failure"
            src.disconnect()
            break


class TestFileSource:
    def test_csv_read(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("sensor_id,timestamp,value\n")
            f.write("s1,1000.0,42.0\n")
            f.write("s2,1001.0,43.0\n")
            path = f.name
        try:
            src = FileSource(path=path, format="csv")
            src.connect()
            readings = list(src.read())
            assert len(readings) == 2
            assert readings[0].sensor_id == "s1"
        finally:
            os.unlink(path)

    def test_jsonl_read(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write(json.dumps({"sensor_id": "s1", "value": 10}) + "\n")
            f.write(json.dumps({"sensor_id": "s2", "value": 20}) + "\n")
            path = f.name
        try:
            src = FileSource(path=path, format="jsonl")
            src.connect()
            readings = list(src.read())
            assert len(readings) == 2
        finally:
            os.unlink(path)


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
