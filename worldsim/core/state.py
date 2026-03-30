"""
State management for simulation reproducibility.

Supports:
- State snapshots for checkpointing
- State diffs for change tracking
- History logging for analysis
"""

from __future__ import annotations

import copy
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class StateSnapshot:
    """Immutable snapshot of simulation state at a given tick."""

    tick: int
    timestamp: float
    data: Dict[str, Any]
    agent_states: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    environment_state: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tick": self.tick,
            "timestamp": self.timestamp,
            "data": self.data,
            "agent_states": self.agent_states,
            "environment_state": self.environment_state,
            "metrics": self.metrics,
        }


@dataclass
class StateDiff:
    """Tracks changes between two states."""

    tick: int
    added: Dict[str, Any] = field(default_factory=dict)
    removed: Dict[str, Any] = field(default_factory=dict)
    modified: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tick": self.tick,
            "added": self.added,
            "removed": self.removed,
            "modified": self.modified,
        }

    @staticmethod
    def compute(old: Dict[str, Any], new: Dict[str, Any], tick: int = 0) -> StateDiff:
        """Compute the diff between two state dicts."""
        diff = StateDiff(tick=tick)
        old_keys = set(old.keys())
        new_keys = set(new.keys())
        diff.added = {k: new[k] for k in new_keys - old_keys}
        diff.removed = {k: old[k] for k in old_keys - new_keys}
        diff.modified = {k: {"old": old[k], "new": new[k]} for k in new_keys & old_keys if old[k] != new[k]}
        return diff


class StateManager:
    """
    Manages simulation state with history and snapshots.

    Usage:
        sm = StateManager()
        sm.set("population", 1000)
        sm.snapshot(tick=0)
    """

    def __init__(self, initial_state: Optional[Dict[str, Any]] = None, max_history: int = 10000):
        self._state: Dict[str, Any] = dict(initial_state) if initial_state else {}
        self._history: List[StateSnapshot] = []
        self._max_history = max_history
        self._tick = 0

    def get(self, key: str, default: Any = None) -> Any:
        return self._state.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._state[key] = value

    def update(self, data: Dict[str, Any]) -> None:
        self._state.update(data)

    def remove(self, key: str) -> None:
        self._state.pop(key, None)

    def get_all(self) -> Dict[str, Any]:
        return dict(self._state)

    def snapshot(self, tick: Optional[int] = None,
                 agent_states: Optional[Dict] = None,
                 environment_state: Optional[Dict] = None,
                 metrics: Optional[Dict] = None) -> StateSnapshot:
        snap = StateSnapshot(
            tick=tick or self._tick,
            timestamp=time.time(),
            data=copy.deepcopy(self._state),
            agent_states=copy.deepcopy(agent_states) if agent_states else {},
            environment_state=copy.deepcopy(environment_state) if environment_state else {},
            metrics=copy.deepcopy(metrics) if metrics else {},
        )
        self._history.append(snap)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]
        return snap

    def diff_from_last(self, tick: Optional[int] = None) -> Optional[StateDiff]:
        if len(self._history) < 2:
            return None
        prev = self._history[-2].data
        curr = self._history[-1].data
        return StateDiff.compute(prev, curr, tick=tick or self._tick)

    def restore(self, snapshot: StateSnapshot) -> None:
        self._state = copy.deepcopy(snapshot.data)

    def get_history(self) -> List[StateSnapshot]:
        return list(self._history)

    def clear_history(self) -> None:
        self._history.clear()

    @property
    def tick(self) -> int:
        return self._tick

    @tick.setter
    def tick(self, value: int) -> None:
        self._tick = value
