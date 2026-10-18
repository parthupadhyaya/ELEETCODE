"""API for the LeetCode visualizer.

Run with:  venv\\Scripts\\uvicorn main:app --reload --port 8000
Set GEMINI_API_KEY to enable /api/run's animation scripts.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from gemini import GeminiError, build_animation
from problems import PROBLEMS, PROBLEMS_BY_ID

TRACER = Path(__file__).with_name("tracer.py")
# The built frontend (npm run build). Served by this app in production so the
# whole site is one URL; in development Vite serves it instead.
FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"
TRACE_TIMEOUT_S = 10
# The only environment variables the tracer subprocess gets. Solutions are
# untrusted and tracer.py's import blocking isn't escape-proof, so secrets like
# GEMINI_API_KEY must never reach that process.
TRACER_ENV_KEYS = ("PATH", "SYSTEMROOT", "TEMP", "TMP", "TMPDIR", "LANG")

app = FastAPI(title="LeetCode Visualizer")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class TraceRequest(BaseModel):
    code: str = Field(max_length=20_000)
    run: str = Field(max_length=5_000)


def failed_trace(error_type, message):
    return {"steps": [], "loops": [], "error": {"type": error_type, "message": message, "line": None}}


def run_tracer(code, run):
    # Each run gets its own interpreter so infinite loops can be killed and
    # nothing a solution does leaks into the server process.
    try:
        proc = subprocess.run(
            [sys.executable, str(TRACER)],
            input=json.dumps({"code": code, "run": run}),
            capture_output=True,
            text=True,
            timeout=TRACE_TIMEOUT_S,
            cwd=TRACER.parent,
            # Fixed hash seed so set iteration order (and so every trace) is
            # the same on every run
            env={
                **{k: os.environ[k] for k in TRACER_ENV_KEYS if k in os.environ},
                "PYTHONHASHSEED": "0",
            },
        )
    except subprocess.TimeoutExpired:
        return failed_trace("Timeout", f"Code ran longer than {TRACE_TIMEOUT_S}s (infinite loop?)")
    if proc.returncode != 0 or not proc.stdout:
        return failed_trace("RunnerError", proc.stderr[-1500:] or "Tracer crashed")
    return json.loads(proc.stdout)


@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/api/problems")
def list_problems():
    return [
        {k: p[k] for k in ("id", "num", "title", "difficulty", "category")}
        for p in PROBLEMS
    ]


@app.get("/api/problems/{problem_id}")
def get_problem(problem_id: str):
    problem = PROBLEMS_BY_ID.get(problem_id)
    if problem is None:
        raise HTTPException(404, f"Unknown problem '{problem_id}'")
    return problem


@app.post("/api/trace")
def trace(req: TraceRequest):
    return run_tracer(req.code, req.run)


@app.post("/api/run")
def run_code(req: TraceRequest):
    """Trace the code, then have Gemini turn the trace into an animation script.

    Returns the full trace plus `animation` (a JSON array of AnimationStep, or
    null) and `animation_error` (why there is no animation, or null). A Gemini
    failure never hides the trace, so the visualizer still works without it.
    """
    result = run_tracer(req.code, req.run)
    return {**result, **animate_trace(req.code, result)}


@app.post("/api/animate")
def animate(req: TraceRequest):
    """Only the animation half of /api/run: {animation, animation_error}.

    The frontend shows /api/trace right away and fetches this in the
    background, since Gemini takes far longer than tracing. The code is traced
    again here; PYTHONHASHSEED is fixed, so trace_index values line up with the
    trace the frontend already has.
    """
    return animate_trace(req.code, run_tracer(req.code, req.run))


def animate_trace(code, result):
    if not result["steps"]:
        return {"animation": None, "animation_error": "Nothing was traced."}
    try:
        return {"animation": [s.model_dump() for s in build_animation(code, result)], "animation_error": None}
    except GeminiError as e:
        return {"animation": None, "animation_error": str(e)}


# Registered last so every /api route above takes precedence
if FRONTEND_DIST.is_dir():
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
