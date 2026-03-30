"""Agent behavior models — rule-based and probabilistic decision making."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import numpy as np


class BehaviorModel(ABC):
    """Base class for agent behavior models."""

    def __init__(self, params: Optional[Dict[str, Any]] = None):
        self.params = params or {}

    @abstractmethod
    def decide(self, state: Dict[str, Any], neighbors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Decide the agent's next action based on state and neighbors."""
        ...


class RuleBasedBehavior(BehaviorModel):
    """
    Rule-based behavior: if-then rules determine agent actions.

    Params:
        rules: list of (condition_fn, action_fn) tuples
    """

    def __init__(self, rules: Optional[List[tuple]] = None, default_action: Optional[Dict] = None):
        super().__init__()
        self.rules = rules or []
        self.default_action = default_action or {"action": "idle"}

    def decide(self, state: Dict[str, Any], neighbors: List[Dict[str, Any]]) -> Dict[str, Any]:
        for condition, action in self.rules:
            if condition(state, neighbors):
                return action(state, neighbors)
        return self.default_action


class ProbabilisticBehavior(BehaviorModel):
    """
    Probabilistic behavior: weighted random action selection.

    Params:
        actions: dict of {action_name: weight}
    """

    def __init__(self, actions: Optional[Dict[str, float]] = None, seed: Optional[int] = None):
        super().__init__()
        self.actions = actions or {"idle": 1.0}
        self._rng = np.random.default_rng(seed)

    def decide(self, state: Dict[str, Any], neighbors: List[Dict[str, Any]]) -> Dict[str, Any]:
        names = list(self.actions.keys())
        weights = list(self.actions.values())
        total = sum(weights)
        probs = [w / total for w in weights]
        chosen = self._rng.choice(names, p=probs)
        return {"action": chosen}
