"""Metrics collection, aggregation, and export."""

from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np


@dataclass
class MetricPoint:
    tick: int
    name: str
    value: float


class MetricsCollector:
    """
    Collects and aggregates simulation metrics.

    Usage:
        mc = MetricsCollector()
        mc.record(tick=1, name="efficiency", value=0.85)
        summary = mc.get_summary("efficiency")
    """

    def __init__(self):
        self._metrics: Dict[str, List[MetricPoint]] = {}

    def record(self, tick: int, name: str, value: float) -> None:
        if name not in self._metrics:
            self._metrics[name] = []
        self._metrics[name].append(MetricPoint(tick=tick, name=name, value=value))

    def record_dict(self, tick: int, metrics: Dict[str, float]) -> None:
        for name, value in metrics.items():
            self.record(tick, name, value)

    def get_series(self, name: str) -> List[MetricPoint]:
        return self._metrics.get(name, [])

    def get_values(self, name: str) -> List[float]:
        return [p.value for p in self.get_series(name)]

    def get_summary(self, name: str) -> Dict[str, float]:
        values = self.get_values(name)
        if not values:
            return {"name": name, "count": 0}
        arr = np.array(values)
        return {
            "name": name,
            "count": len(values),
            "mean": float(np.mean(arr)),
            "std": float(np.std(arr)),
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
            "p25": float(np.percentile(arr, 25)),
            "p50": float(np.percentile(arr, 50)),
            "p75": float(np.percentile(arr, 75)),
            "last": float(values[-1]),
        }

    def get_all_summaries(self) -> Dict[str, Dict[str, float]]:
        return {name: self.get_summary(name) for name in self._metrics}

    def clear(self) -> None:
        self._metrics.clear()


class ResultsExporter:
    """Exports simulation results to various formats."""

    @staticmethod
    def to_json(results: List[Dict[str, Any]], include_metrics: bool = True) -> str:
        """Export results to JSON string."""
        export = []
        for r in results:
            entry = {"tick": r["tick"]}
            if include_metrics and "metrics" in r:
                entry["metrics"] = r["metrics"]
            if "agent_states" in r:
                entry["agent_count"] = len(r["agent_states"])
            if "environment_state" in r:
                entry["environment"] = r["environment_state"]
            export.append(entry)
        return json.dumps(export, indent=2)

    @staticmethod
    def to_csv(results: List[Dict[str, Any]]) -> str:
        """Export metrics to CSV string."""
        if not results:
            return ""
        output = io.StringIO()
        writer = csv.writer(output)
        # Header
        metrics = results[0].get("metrics", {})
        headers = ["tick"] + sorted(metrics.keys())
        writer.writerow(headers)
        # Rows
        for r in results:
            m = r.get("metrics", {})
            row = [r["tick"]] + [m.get(h, "") for h in headers[1:]]
            writer.writerow(row)
        return output.getvalue()

    @staticmethod
    def summary_report(results: List[Dict[str, Any]]) -> str:
        """Generate a text summary report."""
        if not results:
            return "No results to report."

        lines = [
            "=" * 60,
            "SIMULATION RESULTS REPORT",
            "=" * 60,
            f"Total ticks: {len(results)}",
            f"Tick range: {results[0]['tick']} - {results[-1]['tick']}",
            "",
        ]

        metrics = [r.get("metrics", {}) for r in results]
        if metrics:
            mc = MetricsCollector()
            for r in results:
                mc.record_dict(r["tick"], r.get("metrics", {}))

            lines.append("METRICS SUMMARY:")
            lines.append("-" * 40)
            for name, summary in mc.get_all_summaries().items():
                lines.append(
                    f"  {name}: mean={summary['mean']:.4f}, "
                    f"std={summary['std']:.4f}, "
                    f"min={summary['min']:.4f}, max={summary['max']:.4f}"
                )

        # Agent states from last tick
        last = results[-1]
        if "agent_states" in last:
            lines.append(f"\nFinal agent count: {len(last['agent_states'])}")

        lines.append("\n" + "=" * 60)
        return "\n".join(lines)

    @staticmethod
    def save(results: List[Dict[str, Any]], path: str, fmt: str = "json") -> None:
        """Save results to a file."""
        from pathlib import Path
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        if fmt == "json":
            p.write_text(ResultsExporter.to_json(results))
        elif fmt == "csv":
            p.write_text(ResultsExporter.to_csv(results))
        elif fmt == "report":
            p.write_text(ResultsExporter.summary_report(results))
