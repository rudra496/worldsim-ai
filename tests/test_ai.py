"""Tests for AI modules — predictor, optimizer, feedback, multi-agent system."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from worldsim.ai.predictor import SimplePredictor, AnomalyDetector
from worldsim.ai.optimizer import ResourceAllocator, SimpleScheduler
from worldsim.ai.feedback import FeedbackLoop
from worldsim.ai.multi_agent_system import AgentCoordinator


class TestSimplePredictor:
    def test_predict_range(self):
        p = SimplePredictor()
        for i in range(20):
            p.update(float(i))
        preds = p.predict_range(steps=5)
        assert len(preds) == 5
        assert all(isinstance(x, float) for x in preds)

    def test_predict_next(self):
        p = SimplePredictor()
        for i in range(10):
            p.update(float(i))
        val = p.predict_next()
        assert isinstance(val, float)

    def test_predict_next_methods(self):
        p = SimplePredictor()
        for i in range(15):
            p.update(float(i))
        linear = p.predict_next(method="linear")
        avg = p.predict_next(method="moving_average")
        assert isinstance(linear, float)
        assert isinstance(avg, float)

    def test_insufficient_data(self):
        p = SimplePredictor()
        p.update(1.0)
        val = p.predict_next()
        assert isinstance(val, float)


class TestAnomalyDetector:
    def test_no_anomaly(self):
        ad = AnomalyDetector(threshold_std=5.0)
        for i in range(25):
            ad.check(100.0 + i * 0.01, tick=i)
        result = ad.check(100.5, tick=25)
        assert result["is_anomaly"] is False

    def test_detect_anomaly(self):
        ad = AnomalyDetector(threshold_std=2.0)
        for i in range(25):
            ad.check(100.0, tick=i)
        result = ad.check(500.0, tick=25)
        assert result["is_anomaly"] is True

    def test_reset(self):
        ad = AnomalyDetector()
        ad.check(100.0, tick=0)
        ad.reset()
        assert len(ad.get_anomalies()) == 0


class TestResourceAllocator:
    def test_greedy_allocation(self):
        ra = ResourceAllocator(total_budget=100, method="greedy")
        demands = {"a": 60, "b": 50, "c": 30}
        alloc = ra.allocate(demands)
        total = sum(alloc.values())
        assert total <= 100

    def test_proportional_allocation(self):
        ra = ResourceAllocator(total_budget=100, method="proportional")
        demands = {"a": 60, "b": 40}
        alloc = ra.allocate(demands)
        assert alloc["a"] + alloc["b"] <= 100

    def test_with_priorities(self):
        ra = ResourceAllocator(total_budget=100, method="greedy")
        demands = {"a": 50, "b": 60}
        priorities = {"a": 10.0, "b": 1.0}
        alloc = ra.allocate(demands, priorities=priorities)
        assert alloc["a"] + alloc["b"] <= 100


class TestSimpleScheduler:
    def test_schedule_tasks(self):
        scheduler = SimpleScheduler()
        tasks = [
            {"id": "t1", "priority": 1, "duration": 5, "resource_need": 1},
            {"id": "t2", "priority": 10, "duration": 3, "resource_need": 2},
            {"id": "t3", "priority": 5, "duration": 4, "resource_need": 1},
        ]
        agents = [{"id": "a1", "capacity": 5, "speed": 1.0}, {"id": "a2", "capacity": 5, "speed": 1.0}]
        schedule = scheduler.schedule_tasks(tasks, agents)
        assert isinstance(schedule, list)
        assert len(schedule) > 0

    def test_empty_schedule(self):
        scheduler = SimpleScheduler()
        schedule = scheduler.schedule_tasks([], [])
        assert schedule == []


class TestFeedbackLoop:
    def test_enable_disable(self):
        fl = FeedbackLoop()
        fl.enable()
        fl.disable()

    def test_update(self):
        fl = FeedbackLoop()
        result = fl.update(tick=0, actual_metrics={"efficiency": 0.8})
        assert isinstance(result, dict)

    def test_get_stats(self):
        fl = FeedbackLoop()
        fl.update(tick=0, actual_metrics={"efficiency": 0.8})
        stats = fl.get_stats()
        assert isinstance(stats, dict)

    def test_correction_history(self):
        fl = FeedbackLoop()
        for i in range(5):
            fl.update(tick=i, actual_metrics={"efficiency": 0.5 + i * 0.1})
        history = fl.get_correction_history(limit=3)
        assert len(history) <= 3


class TestAgentCoordinator:
    def test_coordinate(self):
        ac = AgentCoordinator(config={"energy_budget": 1000})
        result = ac.coordinate(
            tick=0,
            state={"total_energy_consumption": 50, "total_production": 30},
            env_state={},
            agent_states={},
        )
        assert isinstance(result, dict)

    def test_get_summary(self):
        ac = AgentCoordinator(config={"energy_budget": 1000})
        ac.coordinate(tick=0, state={}, env_state={}, agent_states={})
        summary = ac.get_summary()
        assert isinstance(summary, dict)


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
