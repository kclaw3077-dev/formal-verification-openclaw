"""
FastAPI backend for the Formal Verification for OpenClaw SRE Agent demo.
Serves scenario data, TLA+ specs, and verification results.
"""
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from scenarios import get_scenario, list_scenarios

app = FastAPI(title="Formal Verification for OpenClaw SRE Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

TLA_DIR = Path(__file__).parent.parent / "tla"


@app.get("/api/scenarios")
def api_list_scenarios(lang: str = Query("en", regex="^(en|zh)$")):
    """Return scenario list including lifecycle phase for each scenario."""
    return list_scenarios(lang)


@app.get("/api/scenarios/{scenario_id}")
def api_get_scenario(scenario_id: str, lang: str = Query("en", regex="^(en|zh)$")):
    try:
        return get_scenario(scenario_id, lang)
    except ValueError:
        raise HTTPException(404, f"Scenario '{scenario_id}' not found")


@app.get("/api/scenarios/{scenario_id}/steps/{step_id}")
def api_get_step(scenario_id: str, step_id: int, lang: str = Query("en", regex="^(en|zh)$")):
    try:
        scenario = get_scenario(scenario_id, lang)
    except ValueError:
        raise HTTPException(404, f"Scenario '{scenario_id}' not found")
    for step in scenario.steps:
        if step.step_id == step_id:
            return step
    raise HTTPException(404, f"Step {step_id} not found in scenario '{scenario_id}'")


@app.get("/api/tla/{filename}")
def api_get_tla_spec(filename: str):
    if not filename.endswith(".tla"):
        raise HTTPException(400, "Only .tla files are served")
    path = TLA_DIR / filename
    if not path.exists():
        raise HTTPException(404, f"TLA+ spec '{filename}' not found")
    return {"filename": filename, "content": path.read_text()}


@app.get("/api/tla")
def api_list_tla_specs():
    return [
        {"filename": f.name, "size": f.stat().st_size}
        for f in sorted(TLA_DIR.glob("*.tla"))
    ]


# Serve frontend static files in production
FRONTEND_DIST = Path(__file__).parent.parent / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")
