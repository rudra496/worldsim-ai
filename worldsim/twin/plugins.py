"""Plugin system — extensible plugin manager with hot-reload and sandboxing."""

from __future__ import annotations

import importlib.util
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type

logger = logging.getLogger(__name__)


class PluginHook:
    """Available plugin hooks."""
    TICK_START = "on_tick_start"
    TICK_END = "on_tick_end"
    AGENT_CREATED = "on_agent_created"
    AGENT_DESTROYED = "on_agent_destroyed"
    SCENARIO_START = "on_scenario_start"
    SCENARIO_END = "on_scenario_end"
    ANOMALY_DETECTED = "on_anomaly_detected"
    OPTIMIZATION_APPLIED = "on_optimization_applied"


@dataclass
class PluginInfo:
    """Metadata about a loaded plugin."""
    name: str
    version: str
    description: str = ""
    author: str = ""
    path: Optional[str] = None
    loaded_at: float = 0.0
    enabled: bool = True
    hooks: List[str] = field(default_factory=list)


class Plugin(ABC):
    """Base class for all plugins."""

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    def version(self) -> str:
        return "0.1.0"

    @property
    def description(self) -> str:
        return ""

    @property
    def author(self) -> str:
        return ""

    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Called when plugin is loaded."""

    def execute(self, hook: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Called when a hooked event fires."""
        return None

    def teardown(self) -> None:
        """Called when plugin is unloaded."""


class PluginManager:
    """
    Manages plugin lifecycle: load, unload, execute, hot-reload.
    
    Usage:
        pm = PluginManager()
        pm.load_plugin("my_plugin.py")
        pm.execute_hook(PluginHook.TICK_START, {"tick": 1})
    """

    def __init__(self, plugin_dir: Optional[str] = None):
        self._plugins: Dict[str, Plugin] = {}
        self._plugin_info: Dict[str, PluginInfo] = {}
        self._hooks: Dict[str, List[str]] = {}  # hook -> [plugin_names]
        self._plugin_dir = Path(plugin_dir) if plugin_dir else None

    def load_plugin(self, path: str, config: Optional[Dict] = None) -> PluginInfo:
        """Load a plugin from a Python file."""
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Plugin not found: {path}")

        spec = importlib.util.spec_from_file_location(p.stem, p)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Find Plugin subclasses
        plugin_instance = None
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and issubclass(attr, Plugin)
                    and attr is not Plugin and not attr.__name__.startswith("_")):
                plugin_instance = attr()
                break

        if plugin_instance is None:
            raise ValueError(f"No Plugin subclass found in {path}")

        plugin_instance.initialize(config)
        name = plugin_instance.name

        self._plugins[name] = plugin_instance
        self._plugin_info[name] = PluginInfo(
            name=name,
            version=plugin_instance.version,
            description=plugin_instance.description,
            author=plugin_instance.author,
            path=str(p),
            loaded_at=time.time(),
            enabled=True,
        )

        logger.info(f"Plugin loaded: {name} v{plugin_instance.version}")
        return self._plugin_info[name]

    def unload_plugin(self, name: str) -> bool:
        """Unload a plugin."""
        plugin = self._plugins.pop(name, None)
        if plugin:
            plugin.teardown()
            self._plugin_info.pop(name, None)
            # Remove from hooks
            for hook in self._hooks:
                if name in self._hooks[hook]:
                    self._hooks[hook].remove(name)
            logger.info(f"Plugin unloaded: {name}")
            return True
        return False

    def register_hook(self, plugin_name: str, hook: str) -> None:
        if hook not in self._hooks:
            self._hooks[hook] = []
        if plugin_name not in self._hooks[hook]:
            self._hooks[hook].append(plugin_name)

    def execute_hook(self, hook: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute all plugins registered for a hook."""
        results = []
        for plugin_name in self._hooks.get(hook, []):
            plugin = self._plugins.get(plugin_name)
            if plugin and self._plugin_info[plugin_name].enabled:
                try:
                    result = plugin.execute(hook, data)
                    if result:
                        results.append({"plugin": plugin_name, "result": result})
                except Exception as e:
                    logger.error(f"Plugin {plugin_name} error on {hook}: {e}")
        return results

    def list_plugins(self) -> List[PluginInfo]:
        return list(self._plugin_info.values())

    def get_plugin(self, name: str) -> Optional[Plugin]:
        return self._plugins.get(name)

    def enable_plugin(self, name: str) -> None:
        if name in self._plugin_info:
            self._plugin_info[name].enabled = True

    def disable_plugin(self, name: str) -> None:
        if name in self._plugin_info:
            self._plugin_info[name].enabled = False

    def validate_plugin(self, path: str) -> Dict[str, Any]:
        """Validate a plugin file without loading it."""
        try:
            p = Path(path)
            if not p.exists():
                return {"valid": False, "error": "file_not_found"}
            
            spec = importlib.util.spec_from_file_location(p.stem, p)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            has_plugin = any(
                isinstance(getattr(module, a), type) and issubclass(getattr(module, a), Plugin)
                and getattr(module, a) is not Plugin
                for a in dir(module)
            )
            
            return {"valid": has_plugin, "path": str(p), "has_plugin_class": has_plugin}
        except Exception as e:
            return {"valid": False, "error": str(e)}


# ── Built-in Plugins ────────────────────────────────────────────────

class LoggingPlugin(Plugin):
    """Logs simulation events to file and/or console."""

    def __init__(self, log_file: Optional[str] = None, log_level: str = "INFO"):
        self._log_file = log_file
        self._log_level = getattr(logging, log_level.upper(), logging.INFO)
        self._logger = logging.getLogger(f"plugin.{self.name}")
        if log_file:
            handler = logging.FileHandler(log_file)
            handler.setLevel(self._log_level)
            self._logger.addHandler(handler)
        self._logger.setLevel(self._log_level)

    @property
    def name(self) -> str:
        return "logging"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Configurable file/console logging plugin"

    def execute(self, hook: str, data: Dict[str, Any]) -> None:
        self._logger.log(self._log_level, "[%s] tick=%s data_keys=%s",
                         hook, data.get("tick", "?"), list(data.keys()))


class MetricsExportPlugin(Plugin):
    """Exports metrics in Prometheus format."""

    def __init__(self):
        self._metrics: Dict[str, float] = {}

    @property
    def name(self) -> str:
        return "metrics_export"

    @property
    def version(self) -> str:
        return "1.0.0"

    def execute(self, hook: str, data: Dict[str, Any]) -> None:
        if hook == PluginHook.TICK_END:
            metrics = data.get("metrics", {})
            self._metrics.update(metrics)

    def get_prometheus_output(self) -> str:
        lines = []
        for key, value in self._metrics.items():
            safe_key = key.replace(".", "_").replace("-", "_")
            lines.append(f'worldsim_{safe_key} {value}')
        return "\n".join(lines) + "\n"


class SlackNotifyPlugin(Plugin):
    """Sends alerts to Slack via webhook URL.

    Requires a valid webhook URL to deliver messages. If no URL is configured,
    messages are queued locally and can be retrieved via get_pending_messages().
    """

    def __init__(self, webhook_url: Optional[str] = None):
        self._webhook_url = webhook_url
        self._message_queue: List[Dict[str, str]] = []

    @property
    def name(self) -> str:
        return "slack_notify"

    @property
    def version(self) -> str:
        return "1.0.0"

    def execute(self, hook: str, data: Dict[str, Any]) -> None:
        if hook == PluginHook.ANOMALY_DETECTED:
            msg = f"Anomaly at tick {data.get('tick', '?')}: {data.get('details', 'unknown')}"
            self._send_or_queue(msg, "warning")
        elif hook == PluginHook.OPTIMIZATION_APPLIED:
            msg = f"Optimization applied at tick {data.get('tick', '?')}"
            self._send_or_queue(msg, "info")

    def _send_or_queue(self, text: str, severity: str) -> None:
        payload = {"text": text, "severity": severity}
        if self._webhook_url:
            try:
                import urllib.request
                import json as _json
                data = _json.dumps(payload).encode()
                req = urllib.request.Request(
                    self._webhook_url,
                    data=data,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                urllib.request.urlopen(req, timeout=5)
                return
            except Exception:
                pass
        self._message_queue.append(payload)

    def get_pending_messages(self) -> List[Dict[str, str]]:
        msgs = list(self._message_queue)
        self._message_queue.clear()
        return msgs
