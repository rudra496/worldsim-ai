"""Event system — pub/sub pattern for simulation events."""

from __future__ import annotations

import enum
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


class EventType(enum.Enum):
    """Types of simulation events."""

    TICK = "tick"
    SIMULATION_START = "simulation_start"
    SIMULATION_END = "simulation_end"
    SIMULATION_RESET = "simulation_reset"

    AGENT_CREATED = "agent_created"
    AGENT_DESTROYED = "agent_destroyed"
    AGENT_MOVED = "agent_moved"
    AGENT_ACTION = "agent_action"
    AGENT_INTERACTION = "agent_interaction"

    RESOURCE_PRODUCED = "resource_produced"
    RESOURCE_CONSUMED = "resource_consumed"
    RESOURCE_DEPLETED = "resource_depleted"

    SYSTEM_FAILURE = "system_failure"
    SYSTEM_RECOVERY = "system_recovery"

    ANOMALY_DETECTED = "anomaly_detected"
    OPTIMIZATION_APPLIED = "optimization_applied"

    SCENARIO_START = "scenario_start"
    SCENARIO_END = "scenario_end"
    SCENARIO_EVENT = "scenario_event"


@dataclass
class Event:
    """An event in the simulation."""

    type: EventType
    tick: int = 0
    data: Dict[str, Any] = field(default_factory=dict)
    source: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "tick": self.tick,
            "data": self.data,
            "source": self.source,
        }


class EventBus:
    """
    Publish/subscribe event bus for simulation events.

    Usage:
        bus = EventBus()
        bus.subscribe(EventType.TICK, lambda e: print(e.tick))
        bus.publish(Event(type=EventType.TICK, tick=1))
    """

    def __init__(self):
        self._subscribers: Dict[EventType, List[Callable[[Event], None]]] = defaultdict(list)
        self._event_log: List[Event] = []
        self._max_log = 10000

    def subscribe(self, event_type: EventType, handler: Callable[[Event], None]) -> None:
        self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: EventType, handler: Callable[[Event], None]) -> None:
        if handler in self._subscribers[event_type]:
            self._subscribers[event_type].remove(handler)

    def publish(self, event: Event) -> None:
        self._event_log.append(event)
        if len(self._event_log) > self._max_log:
            self._event_log = self._event_log[-self._max_log:]
        for handler in self._subscribers.get(event.type, []):
            handler(event)

    def publish_all(self, event: Event) -> None:
        """Publish to all subscribers regardless of event type."""
        for handlers in self._subscribers.values():
            for handler in handlers:
                handler(event)

    def get_log(self, event_type: Optional[EventType] = None, limit: int = 100) -> List[Event]:
        if event_type:
            filtered = [e for e in self._event_log if e.type == event_type]
            return filtered[-limit:]
        return self._event_log[-limit:]

    def clear_log(self) -> None:
        self._event_log.clear()

    @property
    def event_count(self) -> int:
        return len(self._event_log)
