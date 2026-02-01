import asyncio
import json
import os
import re
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import time

from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

load_dotenv()

from agents.master_agent import MasterFootTrafficAgent

OPENROUTER_CLIENT = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("GEMINI_API_KEY"),
)

app = FastAPI(
    title="Foot Traffic Prediction API",
    description="Orchestrates multi-agent predictions for small businesses",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Request / Response Models
# -------------------------

class FootTrafficRequest(BaseModel):
    business_name: str
    latitude: float
    longitude: float
    baseline_customers_per_hour: int
    start_time: Optional[str] = None   # ISO format
    horizon_hours: int = 24


class FootTrafficResponse(BaseModel):
    business_name: str
    horizon_hours: int
    generated_at: float
    baseline_customers_per_hour: int
    signals: List[Dict[str, Any]]
    forecast: Dict[str, Any]
    explanation: str


def _parse_start_time(start_time: Optional[str]) -> tuple[Optional[str], Optional[int]]:
    """Parse ISO start_time into (date, hour) for MasterFootTrafficAgent."""
    if not start_time:
        return None, None
    try:
        if "T" in start_time:
            dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        else:
            dt = datetime.strptime(start_time.strip(), "%Y-%m-%d")
        date_str = dt.strftime("%Y-%m-%d")
        hour = dt.hour if hasattr(dt, "hour") else None
        return date_str, hour
    except Exception:
        return None, None


# Default baseline for dashboard; can be overridden by query params
DEFAULT_BASELINE = 42.0

# In-memory cache: key -> (expiry_timestamp, result). TTL = 30 minutes.
_FORECAST_CACHE: Dict[str, tuple[float, Dict[str, Any]]] = {}
_CACHE_TTL_SECONDS = 30 * 60


def _cache_key(baseline: float, date: Optional[str], time: Optional[int]) -> str:
    return f"{baseline}_{date or ''}_{time or ''}"


def _get_cached(cache_key: str) -> Optional[Dict[str, Any]]:
    now_ts = time.time()
    if cache_key not in _FORECAST_CACHE:
        return None
    expiry, result = _FORECAST_CACHE[cache_key]
    if now_ts >= expiry:
        del _FORECAST_CACHE[cache_key]
        return None
    return result


def _set_cached(cache_key: str, result: Dict[str, Any]) -> None:
    _FORECAST_CACHE[cache_key] = (time.time() + _CACHE_TTL_SECONDS, result)


def _generate_business_insights(result: Dict[str, Any]) -> List[str]:
    """
    Use an LLM to synthesize the master agent's signals into bullets that explain
    the REASONING and RATIONALE behind the forecast. Does NOT repeat the high-level
    summary (that's already in the metric cards above).
    """
    if not os.getenv("GEMINI_API_KEY"):
        return []

    try:
        signals = result.get("signals", [])

        # Pass full signal data so the LLM can explain the reasoning
        signal_details = []
        source_labels = {
            "weather_event": "Weather",
            "google_traffic": "Nearby road traffic",
            "mta_subway": "Subway / transit",
        }
        for s in signals:
            src = s.get("source", "?")
            label = source_labels.get(src, src.replace("_", " ").title())
            ex = s.get("extra_customers_per_hour", 0)
            conf = s.get("confidence", 0.5)
            exp = s.get("explanation", "").strip()
            if exp:
                signal_details.append(
                    f"- {label}: {ex:+.1f} extra customers/hr (confidence {conf:.0%}). Reasoning: {exp}"
                )
            else:
                signal_details.append(
                    f"- {label}: {ex:+.1f} extra customers/hr (confidence {conf:.0%})."
                )

        prompt = f"""You are a helpful assistant for a cafe/small business owner. The metric cards ABOVE already show the high-level forecast (demand level, confidence, primary driver). Your job is to write 3–5 bullet points that explain the REASONING behind that forecast—what each data source found and WHY it affects foot traffic.

DO NOT repeat the summary or the numbers from the metric cards (e.g. don't say "above baseline" or "expect more customers"). Instead, explain the underlying factors and rationale.

DATA SOURCES AND THEIR REASONING:
{chr(10).join(signal_details) if signal_details else "(No signal data)"}

RULES:
- Each bullet should explain WHAT one data source found and WHY it matters for foot traffic.
- Use plain language. Reference the actual reasoning from the data above.
- Each bullet: 1–2 sentences max. Focus on rationale, not repetition.
- Example style: "Weather conditions are favorable—mild temps and clear skies tend to bring more walk-in traffic." / "Nearby road congestion suggests traffic flowing toward your area, which may increase pedestrian exposure." / "Subway conditions show above-average crowding near station exits, which often translates to more people on the sidewalk."
- Output ONLY a JSON array of strings, one bullet per element. No other text.
Example: ["Weather conditions are favorable today—mild temps tend to bring more walk-in traffic.", "Road traffic patterns suggest congestion flowing toward your area.", "Subway crowding near station exits may increase sidewalk foot traffic."]"""

        response = OPENROUTER_CLIENT.chat.completions.create(
            model="google/gemini-2.5-flash",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        raw = (response.choices[0].message.content or "").strip()

        # Extract JSON array
        m = re.search(r"\[[\s\S]*\]", raw)
        if not m:
            return []
        arr = json.loads(m.group(0))
        if not isinstance(arr, list):
            return []
        return [str(x).strip() for x in arr if x][:6]
    except Exception:
        return []


@app.get("/")
async def root():
    return {
        "service": "Foot Traffic Prediction API",
        "version": "0.1.0",
        "endpoints": ["GET /api/foot-traffic-forecast", "POST /predict-foot-traffic"],
    }


@app.get("/api/foot-traffic-forecast")
async def get_foot_traffic_forecast(
    baseline: Optional[float] = None,
    date: Optional[str] = None,
    time: Optional[int] = None,
):
    """
    Dashboard endpoint: run MasterFootTrafficAgent and return baseline_customers_per_hour, signals, final_forecast.
    Caches results for 30 min to avoid re-running agents. Adds business_insights: LLM-generated bullets.
    """
    try:
        baseline_val = float(baseline) if baseline is not None else DEFAULT_BASELINE
        key = _cache_key(baseline_val, date, time)

        # Return cached if valid
        cached = _get_cached(key)
        if cached is not None:
            return cached

        # Run agents
        agent = MasterFootTrafficAgent(baseline_customers_per_hour=baseline_val)
        result = await agent.run(date=date, time=time)
        # Generate business-friendly bullets (runs in thread pool to avoid blocking)
        insights = await asyncio.to_thread(_generate_business_insights, result)
        if insights:
            result["business_insights"] = insights

        _set_cached(key, result)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------
# API Endpoint
# -------------------------

@app.post("/predict-foot-traffic", response_model=FootTrafficResponse)
async def predict_foot_traffic(request: FootTrafficRequest):
    """
    Single entrypoint for dashboard to fetch foot traffic predictions.
    Calls ONLY the master agent.
    """

    try:
        date, time_hour = _parse_start_time(request.start_time)
        agent = MasterFootTrafficAgent(baseline_customers_per_hour=request.baseline_customers_per_hour)
        result = await agent.run(date=date, time=time_hour)

        final_forecast = result.get("final_forecast", {})
        summary = final_forecast.get("summary", [])
        explanation = "; ".join(summary) if isinstance(summary, list) else str(summary)
        if not explanation:
            explanation = "Prediction generated using multi-agent signal fusion."

        return {
            "business_name": request.business_name,
            "horizon_hours": request.horizon_hours,
            "generated_at": time.time(),
            "baseline_customers_per_hour": request.baseline_customers_per_hour,
            "signals": result.get("signals", []),
            "forecast": final_forecast,
            "explanation": explanation,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Foot traffic prediction failed: {str(e)}"
        )
