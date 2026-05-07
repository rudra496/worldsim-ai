"""Tests for digital twin, GIS, plugins, marketplace."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from worldsim.twin.gis import CoordinateTransform, GeoFence, GISIntegration
from worldsim.twin.plugins import PluginManager, PluginHook, LoggingPlugin, MetricsExportPlugin
from worldsim.twin.marketplace import MarketplaceAPI, PluginRegistry, PluginMetadata
from worldsim.twin.connector import TwinConnector
from worldsim.twin.core import DigitalTwin, SyncMode
import tempfile, shutil


class TestCoordinateTransform:
    def test_geo_to_grid(self):
        ct = CoordinateTransform(bounds=(23.6, 90.3, 23.9, 90.5), grid_size=(50, 50))
        x, y = ct.geo_to_grid(23.75, 90.4)
        assert 0 <= x < 50 and 0 <= y < 50

    def test_grid_to_geo(self):
        ct = CoordinateTransform(bounds=(23.6, 90.3, 23.9, 90.5), grid_size=(50, 50))
        lat, lon = ct.grid_to_geo(25, 25)
        assert 23.6 <= lat <= 23.9 and 90.3 <= lon <= 90.5

    def test_round_trip(self):
        ct = CoordinateTransform(bounds=(23.6, 90.3, 23.9, 90.5), grid_size=(50, 50))
        lat, lon = ct.grid_to_geo(25, 25)
        x2, y2 = ct.geo_to_grid(lat, lon)
        assert abs(x2 - 25) <= 1 and abs(y2 - 25) <= 1


class TestGeoFence:
    def test_contains(self):
        fence = GeoFence("test", [(0, 0), (0, 10), (10, 10), (10, 0)])
        assert fence.contains(5, 5)
        assert not fence.contains(15, 5)
        assert not fence.contains(-1, 5)


class TestPluginManager:
    def test_list_plugins_empty(self):
        pm = PluginManager()
        assert len(pm.list_plugins()) == 0

    def test_execute_hook_no_plugins(self):
        pm = PluginManager()
        results = pm.execute_hook(PluginHook.TICK_END, {"tick": 1})
        assert isinstance(results, list)


class TestMetricsExportPlugin:
    def test_prometheus_output(self):
        mep = MetricsExportPlugin()
        mep.execute(PluginHook.TICK_END, {"metrics": {"efficiency": 0.85, "throughput": 4.2}})
        mep.execute(PluginHook.TICK_END, {"metrics": {"efficiency": 0.87, "throughput": 4.5}})
        output = mep.get_prometheus_output()
        assert "efficiency" in output
        assert "throughput" in output


class TestMarketplace:
    def test_list_and_search(self):
        tmp = tempfile.mkdtemp()
        try:
            registry = PluginRegistry(registry_dir=tmp)
            mp = MarketplaceAPI(registry=registry)
            plugins = mp.list_available()
            assert len(plugins) > 0
            results = mp.search("logging")
            assert len(results) > 0
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_install_uninstall(self):
        tmp = tempfile.mkdtemp()
        try:
            registry = PluginRegistry(registry_dir=tmp)
            mp = MarketplaceAPI(registry=registry)
            install = mp.install_plugin("logging")
            assert install["success"]
            installed = registry.get_installed()
            assert len(installed) > 0
            uninstall = mp.uninstall_plugin("logging")
            assert uninstall["success"]
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class TestTwinConnector:
    def test_api_keys(self):
        tc = TwinConnector("test_twin")
        keys = tc.get_api_keys()
        assert len(keys) >= 2

    def test_generate_key(self):
        tc = TwinConnector("test_twin")
        new_key = tc.generate_api_key("test_user", "write")
        assert len(new_key) == 32

    def test_authenticate(self):
        tc = TwinConnector("test_twin")
        key = tc.generate_api_key("user", "write")
        assert tc.authenticate(key, "write")

    def test_push_pull_state(self):
        tc = TwinConnector("test_twin")
        key = tc.generate_api_key("user", "write")
        result = tc.push_state("sensor_1", {"temp": 25.5}, api_key=key)
        assert result["success"]
        state = tc.pull_state(api_key=key)
        assert state["success"]

    def test_rate_limit(self):
        tc = TwinConnector("test_twin")
        assert tc.check_rate_limit("c1")
        assert tc.check_rate_limit("c1")
        assert tc.check_rate_limit("c1")
        # Should still work — default limit is high enough

    def test_stats(self):
        tc = TwinConnector("test_twin")
        stats = tc.get_stats()
        assert stats["twin_id"] == "test_twin"


class TestDigitalTwin:
    def test_create(self):
        dt = DigitalTwin(twin_id="test_dt")
        assert dt.twin_id == "test_dt"

    def test_sync_mode(self):
        dt = DigitalTwin(twin_id="test_dt", sync_mode=SyncMode.REPLAY)
        assert dt.sync_mode == SyncMode.REPLAY
        dt.sync_mode = SyncMode.LIVE
        assert dt.sync_mode == SyncMode.LIVE

    def test_get_twin_state(self):
        dt = DigitalTwin(twin_id="test_dt")
        state = dt.get_twin_state()
        assert state.tick == 0

    def test_start_stop(self):
        dt = DigitalTwin(twin_id="test_dt", sync_mode=SyncMode.REPLAY)
        dt.start()
        import time
        time.sleep(0.2)
        assert dt.current_tick > 0
        dt.stop()


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
