"""Optimization modules — resource allocation and scheduling."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import numpy as np


class ResourceAllocator:
    """
    Allocates resources to agents optimally.

    Uses greedy allocation with optional linear programming refinement.
    """

    def __init__(self, total_budget: float = 1000.0, method: str = "greedy"):
        self.total_budget = total_budget
        self.method = method
        self._allocations: Dict[str, float] = {}

    def allocate(self, demands: Dict[str, float], priorities: Optional[Dict[str, float]] = None) -> Dict[str, float]:
        """
        Allocate resources based on demands and priorities.

        Args:
            demands: agent_id -> demand amount
            priorities: agent_id -> priority weight (higher = more important)

        Returns:
            agent_id -> allocated amount
        """
        if not demands:
            return {}

        if priorities is None:
            priorities = {k: 1.0 for k in demands}

        total_demand = sum(demands.values())
        if total_demand <= self.total_budget:
            return dict(demands)

        if self.method == "greedy":
            return self._greedy_allocate(demands, priorities)
        elif self.method == "proportional":
            return self._proportional_allocate(demands, priorities)
        elif self.method == "lp":
            return self._lp_allocate(demands, priorities)
        return self._greedy_allocate(demands, priorities)

    def _greedy_allocate(self, demands: Dict[str, float],
                         priorities: Dict[str, float]) -> Dict[str, float]:
        """Allocate to highest priority agents first."""
        remaining = self.total_budget
        sorted_agents = sorted(demands.keys(),
                                key=lambda a: priorities.get(a, 1.0), reverse=True)
        allocations = {}
        for agent_id in sorted_agents:
            alloc = min(demands[agent_id], remaining)
            allocations[agent_id] = alloc
            remaining -= alloc
            if remaining <= 0:
                break
        return allocations

    def _proportional_allocate(self, demands: Dict[str, float],
                                priorities: Dict[str, float]) -> Dict[str, float]:
        """Allocate proportionally based on weighted demands."""
        weighted = {k: demands[k] * priorities.get(k, 1.0) for k in demands}
        total_weighted = sum(weighted.values())
        if total_weighted == 0:
            return {k: 0.0 for k in demands}
        allocations = {k: (weighted[k] / total_weighted) * self.total_budget for k in demands}
        # Cap at demand
        return {k: min(v, demands[k]) for k, v in allocations.items()}

    def _lp_allocate(self, demands: Dict[str, float],
                     priorities: Dict[str, float]) -> Dict[str, float]:
        """
        Simple LP-based allocation using scipy.

        Maximizes: sum(priority_i * x_i)
        Subject to: sum(x_i) <= budget, 0 <= x_i <= demand_i
        """
        try:
            from scipy.optimize import linprog
        except ImportError:
            return self._greedy_allocate(demands, priorities)

        agent_ids = list(demands.keys())
        n = len(agent_ids)
        # Minimize negative weighted sum = maximize weighted sum
        c = [-priorities.get(a, 1.0) for a in agent_ids]
        # Budget constraint
        A_ub = [np.ones(n)]
        b_ub = [self.total_budget]
        # Bounds: 0 <= x <= demand
        bounds = [(0, demands[a]) for a in agent_ids]

        result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method="highs")
        if result.success:
            return {aid: float(val) for aid, val in zip(agent_ids, result.x)}
        return self._greedy_allocate(demands, priorities)

    def step(self, tick: int, state: Dict[str, Any], env_state: Dict[str, Any],
             agent_states: Dict[str, Any]) -> Dict[str, Any]:
        """AI module interface."""
        demands = {aid: max(0.01, a.get("energy_consumption", 1.0))
                   for aid, a in agent_states.items()}
        allocations = self.allocate(demands)
        self._allocations = allocations
        return {
            "allocations": allocations,
            "total_allocated": sum(allocations.values()),
            "unmet_demand": sum(demands.values()) - sum(allocations.values()),
        }


class SimpleScheduler:
    """
    Simple scheduling optimization.

    Schedules tasks to agents based on capacity and priority.
    """

    def __init__(self):
        self._schedule: List[Dict[str, Any]] = []

    def schedule_tasks(self, tasks: List[Dict[str, Any]],
                        agents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Assign tasks to agents using priority-based scheduling.

        Args:
            tasks: list of {id, priority, duration, resource_need}
            agents: list of {id, capacity, speed}

        Returns:
            list of {task_id, agent_id, start_time, end_time}
        """
        self._schedule.clear()
        sorted_tasks = sorted(tasks, key=lambda t: t.get("priority", 0), reverse=True)

        agent_capacity = {a["id"]: a.get("capacity", 1.0) for a in agents}
        agent_speed = {a["id"]: a.get("speed", 1.0) for a in agents}
        current_time = {a["id"]: 0 for a in agents}

        for task in sorted_tasks:
            best_agent = min(agent_capacity.keys(),
                            key=lambda a: current_time[a])
            duration = task.get("duration", 1.0) / agent_speed[best_agent]
            self._schedule.append({
                "task_id": task["id"],
                "agent_id": best_agent,
                "start_time": current_time[best_agent],
                "end_time": current_time[best_agent] + duration,
                "priority": task.get("priority", 0),
            })
            current_time[best_agent] += duration

        return self._schedule

    def get_schedule(self) -> List[Dict[str, Any]]:
        return list(self._schedule)

    def makespan(self) -> float:
        if not self._schedule:
            return 0.0
        return max(s["end_time"] for s in self._schedule)

    def step(self, tick: int, state: Dict[str, Any], env_state: Dict[str, Any],
             agent_states: Dict[str, Any]) -> Dict[str, Any]:
        """AI module interface."""
        return {"schedule_length": len(self._schedule), "makespan": self.makespan()}
