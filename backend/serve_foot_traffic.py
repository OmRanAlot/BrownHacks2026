"""
Minimal FastAPI server that exposes MasterFootTrafficAgent as the single source of truth.
The dashboard must call this endpoint only—never sub-agents (weather, Google traffic, MTA) directly.
Run: cd backend && uvicorn serve_foot_traffic:app --reload --port 8001
"""

import asyncio
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from agents.master_agent import MasterFootTrafficAgent

app = FastAPI(
    title="Foot Traffic Forecast API",
    description="Single endpoint: MasterFootTrafficAgent. Sub-agents are not exposed.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Default baseline for demo; can be overridden by query/body
DEFAULT_BASELINE = 42.0


@app.get("/")
async def root():
    return {
        "service": "Foot Traffic Forecast",
        "version": "1.0.0",
        "endpoint": "GET /api/foot-traffic-forecast",
        "note": "MasterFootTrafficAgent is the single source of truth; do not call sub-agents from the UI.",
    }


@app.get("/api/foot-traffic-forecast")
async def get_foot_traffic_forecast(
    baseline: Optional[float] = None,
    date: Optional[str] = None,
    time: Optional[int] = None,
):
    """
    Run MasterFootTrafficAgent once and return baseline_customers_per_hour, signals, final_forecast.
    Sub-agents (weather/event, Google traffic, MTA) are run only inside the master agent.
    """
    try:
        baseline_val = baseline if baseline is not None else DEFAULT_BASELINE
        agent = MasterFootTrafficAgent(baseline_customers_per_hour=baseline_val)
        result = await agent.run(date=date, time=time)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/foot-traffic-forecast")
async def post_foot_traffic_forecast(body: dict):
    """Same as GET but with optional body: { baseline?, date?, time? }."""
    try:
        baseline_val = body.get("baseline", DEFAULT_BASELINE)
        if isinstance(baseline_val, (int, float)):
            baseline_val = float(baseline_val)
        else:
            baseline_val = DEFAULT_BASELINE
        agent = MasterFootTrafficAgent(baseline_customers_per_hour=baseline_val)
        result = await agent.run(
            date=body.get("date"),
            time=body.get("time"),
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
