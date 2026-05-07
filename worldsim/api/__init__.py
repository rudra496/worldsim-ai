"""FastAPI backend — REST API + WebSocket for WorldSim AI."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

app = FastAPI(
    title="WorldSim AI",
    description="AI-powered digital twin simulation platform",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── In-memory simulation store ──────────────────────────────────────

_simulations: Dict[str, Dict[str, Any]] = {}
_ws_clients: Dict[str, List[WebSocket]] = {}


# ── Request/Response Models ─────────────────────────────────────────

class SimulationStartRequest(BaseModel):
    scenario: str = Field(..., description="Scenario name to run")
    ticks: Optional[int] = Field(None, description="Override duration")
    deterministic: Optional[bool] = Field(True)
    seed: Optional[int] = Field(42)


class SimulationStepRequest(BaseModel):
    pass


class ScenarioInfo(BaseModel):
    name: str
    display_name: str
    description: str


# ── Endpoints ───────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"name": "WorldSim AI", "version": "0.1.0", "status": "running"}


@app.get("/scenarios", response_model=List[ScenarioInfo])
def list_scenarios():
    from worldsim.scenarios.definitions import list_scenario_info
    return list_scenario_info()


@app.post("/simulations/start")
async def start_simulation(req: SimulationStartRequest):
    from worldsim.scenarios.engine import ScenarioEngine
    from worldsim.scenarios.definitions import get_scenario

    scenario_config = get_scenario(req.scenario)
    if scenario_config is None:
        raise HTTPException(404, f"Unknown scenario: {req.scenario}")

    sim_id = f"sim_{len(_simulations) + 1}"
    _simulations[sim_id] = {
        "id": sim_id,
        "scenario": req.scenario,
        "status": "running",
        "ticks_completed": 0,
        "results": [],
        "summary": None,
    }

    async def _run():
        try:
            engine = ScenarioEngine()
            result = engine.run_scenario(
                req.scenario,
                ticks=req.ticks,
                override_config={
                    "deterministic": req.deterministic,
                    "seed": req.seed,
                } if req.deterministic is not None or req.seed is not None else None,
            )
            _simulations[sim_id]["results"] = result.get("results", [])
            _simulations[sim_id]["summary"] = result.get("summary", {})
            _simulations[sim_id]["ticks_completed"] = len(result.get("results", []))
            _simulations[sim_id]["status"] = "completed"
        except Exception as e:
            _simulations[sim_id]["status"] = "error"
            _simulations[sim_id]["error"] = str(e)
            logger.error(f"Simulation {sim_id} failed: {e}")

    asyncio.create_task(_run())
    return {"sim_id": sim_id, "scenario": req.scenario, "status": "running"}


@app.get("/simulations")
def list_simulations():
    return [{"id": s["id"], "scenario": s["scenario"], "status": s["status"],
             "ticks": s["ticks_completed"]} for s in _simulations.values()]


@app.get("/simulations/{sim_id}")
def get_simulation(sim_id: str):
    if sim_id not in _simulations:
        raise HTTPException(404, f"Simulation not found: {sim_id}")
    sim = _simulations[sim_id]
    return {"id": sim["id"], "scenario": sim["scenario"], "status": sim["status"],
            "ticks_completed": sim["ticks_completed"], "summary": sim.get("summary")}


@app.get("/simulations/{sim_id}/results")
def get_results(sim_id: str):
    if sim_id not in _simulations:
        raise HTTPException(404, f"Simulation not found: {sim_id}")
    sim = _simulations[sim_id]
    # Return last 100 results for performance
    results = sim["results"]
    if len(results) > 100:
        return {"total": len(results), "showing": 100, "data": results[-100:]}
    return {"total": len(results), "data": results}


@app.get("/simulations/{sim_id}/metrics")
def get_metrics(sim_id: str):
    if sim_id not in _simulations:
        raise HTTPException(404, f"Simulation not found: {sim_id}")
    sim = _simulations[sim_id]
    from worldsim.utils.metrics import MetricsCollector
    mc = MetricsCollector()
    for r in sim["results"]:
        mc.record_dict(r["tick"], r.get("metrics", {}))
    return mc.get_all_summaries()


@app.get("/health")
def health():
    return {"status": "healthy", "simulations": len(_simulations)}


# ── WebSocket ───────────────────────────────────────────────────────

@app.websocket("/ws/simulations/{sim_id}")
async def ws_simulation(websocket: WebSocket, sim_id: str):
    await websocket.accept()
    if sim_id not in _ws_clients:
        _ws_clients[sim_id] = []
    _ws_clients[sim_id].append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        _ws_clients[sim_id].remove(websocket)
