"""Twin connector — REST/WebSocket API for external system integration."""

from __future__ import annotations

import hashlib
import logging
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class APIKeyAuth:
    """Simple API key authentication."""

    def __init__(self):
        self._keys: Dict[str, Dict[str, Any]] = {}

    def generate_key(self, name: str, role: str = "read") -> str:
        """Generate a new API key."""
        raw = f"{name}:{role}:{time.time()}:{id(self)}"
        key = hashlib.sha256(raw.encode()).hexdigest()[:32]
        self._keys[key] = {"name": name, "role": role, "created_at": time.time()}
        return key

    def validate(self, key: str, required_role: str = "read") -> bool:
        """Validate an API key."""
        info = self._keys.get(key)
        if not info:
            return False
        role_hierarchy = {"read": 0, "write": 1, "admin": 2}
        key_role_level = role_hierarchy.get(info["role"], 0)
        required_level = role_hierarchy.get(required_role, 0)
        return key_role_level >= required_level

    def revoke(self, key: str) -> bool:
        return self._keys.pop(key, None) is not None

    def list_keys(self) -> List[Dict[str, Any]]:
        return [{"key": k[:8] + "...", **v} for k, v in self._keys.items()]


class RateLimiter:
    """Simple token bucket rate limiter."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window = window_seconds
        self._requests: Dict[str, List[float]] = {}

    def check(self, client_id: str) -> bool:
        """Check if a request is allowed."""
        now = time.time()
        if client_id not in self._requests:
            self._requests[client_id] = []
        # Clean old entries
        self._requests[client_id] = [t for t in self._requests[client_id]
                                      if now - t < self.window]
        if len(self._requests[client_id]) >= self.max_requests:
            return False
        self._requests[client_id].append(now)
        return True


class TwinConnector:
    """
    Bridges real-world systems with the digital twin.
    
    Provides:
    - Push model: external systems POST state updates
    - Pull model: external systems GET twin state
    - Bidirectional sync via WebSocket
    - API key authentication
    - Rate limiting
    """

    def __init__(self, twin_id: str = "default", config: Optional[Dict[str, Any]] = None):
        self.twin_id = twin_id
        self.config = config or {}
        self._auth = APIKeyAuth()
        self._rate_limiter = RateLimiter(
            max_requests=self.config.get("rate_limit", 100),
            window_seconds=self.config.get("rate_window", 60),
        )
        self._state_buffer: List[Dict[str, Any]] = []
        self._external_sources: Dict[str, Dict[str, Any]] = {}
        self._ws_clients: List[Any] = []
        self._last_sync: float = 0
        self._sync_interval: float = self.config.get("sync_interval", 1.0)

        # Generate default keys
        self._auth.generate_key("system", "admin")
        self._auth.generate_key("readonly", "read")

    def authenticate(self, api_key: str, role: str = "read") -> bool:
        return self._auth.validate(api_key, role)

    def check_rate_limit(self, client_id: str) -> bool:
        return self._rate_limiter.check(client_id)

    def push_state(self, source_id: str, data: Dict[str, Any],
                   api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Receive state update from an external system (push model).
        
        Args:
            source_id: identifier for the external system
            data: state data to merge into the twin
            api_key: optional API key for auth
        """
        if api_key and not self.authenticate(api_key, "write"):
            return {"success": False, "error": "unauthorized"}

        update = {
            "source_id": source_id,
            "timestamp": time.time(),
            "data": data,
        }
        self._state_buffer.append(update)
        if len(self._state_buffer) > 10000:
            self._state_buffer = self._state_buffer[-10000:]

        self._external_sources[source_id] = {
            "last_update": time.time(),
            "data": data,
        }

        # Notify WebSocket clients
        self._broadcast_ws({"type": "state_update", "source": source_id, "data": data})

        return {"success": True, "twin_id": self.twin_id, "buffer_size": len(self._state_buffer)}

    def pull_state(self, api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Get current twin state (pull model).
        """
        if api_key and not self.authenticate(api_key, "read"):
            return {"success": False, "error": "unauthorized"}

        return {
            "success": True,
            "twin_id": self.twin_id,
            "external_sources": list(self._external_sources.keys()),
            "buffer_size": len(self._state_buffer),
            "last_sync": self._last_sync,
            "recent_updates": self._state_buffer[-10:],
        }

    def get_external_sources(self) -> Dict[str, Any]:
        return dict(self._external_sources)

    def register_ws_client(self, client: Any) -> None:
        self._ws_clients.append(client)

    def unregister_ws_client(self, client: Any) -> None:
        if client in self._ws_clients:
            self._ws_clients.remove(client)

    def _broadcast_ws(self, message: Dict[str, Any]) -> None:
        for client in self._ws_clients:
            try:
                if hasattr(client, 'send_json'):
                    client.send_json(message)
                elif callable(client):
                    client(message)
            except Exception as e:
                logger.warning(f"WS broadcast error: {e}")

    def get_api_keys(self) -> List[Dict[str, Any]]:
        return self._auth.list_keys()

    def generate_api_key(self, name: str, role: str = "read") -> str:
        return self._auth.generate_key(name, role)

    def get_stats(self) -> Dict[str, Any]:
        return {
            "twin_id": self.twin_id,
            "buffer_size": len(self._state_buffer),
            "external_sources": len(self._external_sources),
            "ws_clients": len(self._ws_clients),
            "last_sync": self._last_sync,
        }
