"""WorldSim AI CLI."""
import sys


def main():
    if len(sys.argv) < 2:
        print("WorldSim AI v0.1.0")
        print("Usage: worldsim <command>")
        print("  run <scenario>  Run a simulation scenario")
        print("  list            List available scenarios")
        print("  serve           Start the API server")
        print("  demo            Run all demo scenarios")
        return
    cmd = sys.argv[1]
    if cmd == "list":
        from worldsim.scenarios.definitions import list_scenario_info
        for s in list_scenario_info():
            print(f"  {s['display_name']} — {s['description']}")
    elif cmd == "run":
        from worldsim.scenarios.engine import ScenarioEngine
        name = sys.argv[2] if len(sys.argv) > 2 else "smart_city_traffic"
        engine = ScenarioEngine()
        result = engine.run_scenario(name)
        print(f"Scenario: {name}")
        print(f"Ticks: {result['summary']['ticks']}")
        print(f"Avg Efficiency: {result['summary']['avg_efficiency']:.4f}")
        print(f"Avg Stability: {result['summary']['avg_stability']:.4f}")
    elif cmd == "demo":
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from run_demo import run_demo
        run_demo()
    elif cmd == "serve":
        try:
            import uvicorn
        except ImportError:
            print("Error: uvicorn is required. Install with: pip install uvicorn")
            return
        uvicorn.run("worldsim.api:app", host="0.0.0.0", port=8000, reload=True)
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
