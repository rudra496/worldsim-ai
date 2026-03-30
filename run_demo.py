#!/usr/bin/env python3
"""
WorldSim AI — Demo Runner
Runs all 4 demo scenarios and prints results.
"""

import time
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from worldsim.scenarios.engine import ScenarioEngine
from worldsim.scenarios.definitions import list_scenario_info
from worldsim.utils.metrics import ResultsExporter


def print_header(text: str):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def run_demo():
    print_header("🌍 WorldSim AI — Demo Runner")

    # List scenarios
    scenarios = list_scenario_info()
    print("Available scenarios:")
    for s in scenarios:
        print(f"  • {s['display_name']}")
        print(f"    {s['description']}")
        print()

    engine = ScenarioEngine()

    for scenario_info in scenarios:
        name = scenario_info["name"]
        print_header(f"Running: {scenario_info['display_name']}")

        start = time.time()
        result = engine.run_scenario(name)
        elapsed = time.time() - start

        summary = result["summary"]
        print(f"  Ticks:     {summary.get('ticks', 0)}")
        print(f"  Time:      {elapsed:.2f}s")
        print(f"  Efficiency:  {summary.get('avg_efficiency', 0):.4f}")
        print(f"  Throughput:  {summary.get('avg_throughput', 0):.4f}")
        print(f"  Stability:   {summary.get('avg_stability', 0):.4f}")
        print(f"  Peak Energy: {summary.get('peak_energy', 0):.2f}")

        # Save results
        os.makedirs("experiments/results", exist_ok=True)
        report = ResultsExporter.summary_report(result["results"])
        report_path = f"experiments/results/{name}_report.txt"
        with open(report_path, "w") as f:
            f.write(report)
        print(f"  Report:    {report_path}")

    print_header("✅ All demos complete!")
    print("Run 'uvicorn worldsim.api.main:app --reload' for the API server.")


if __name__ == "__main__":
    run_demo()
