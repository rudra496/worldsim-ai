"""Configuration management — load/save YAML/JSON configs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


class ConfigManager:
    """Manages simulation configuration files."""

    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir) if config_dir else None
        self._config: Dict[str, Any] = {}

    def load(self, path: str) -> Dict[str, Any]:
        """Load config from YAML or JSON file."""
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Config not found: {path}")

        text = p.read_text()
        if p.suffix in (".yaml", ".yml") and HAS_YAML:
            self._config = yaml.safe_load(text) or {}
        elif p.suffix == ".json":
            self._config = json.loads(text)
        else:
            self._config = json.loads(text)
        return self._config

    def save(self, path: str, config: Optional[Dict[str, Any]] = None) -> None:
        """Save config to file."""
        data = config or self._config
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)

        if p.suffix in (".yaml", ".yml") and HAS_YAML:
            p.write_text(yaml.dump(data, default_flow_style=False))
        else:
            p.write_text(json.dumps(data, indent=2))

    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split(".")
        val = self._config
        for k in keys:
            if isinstance(val, dict):
                val = val.get(k)
            else:
                return default
            if val is None:
                return default
        return val

    def set(self, key: str, value: Any) -> None:
        keys = key.split(".")
        d = self._config
        for k in keys[:-1]:
            d = d.setdefault(k, {})
        d[keys[-1]] = value

    def update(self, data: Dict[str, Any]) -> None:
        self._deep_update(self._config, data)

    @staticmethod
    def _deep_update(target: Dict, source: Dict) -> None:
        for k, v in source.items():
            if k in target and isinstance(target[k], dict) and isinstance(v, dict):
                ConfigManager._deep_update(target[k], v)
            else:
                target[k] = v

    @property
    def config(self) -> Dict[str, Any]:
        return dict(self._config)
