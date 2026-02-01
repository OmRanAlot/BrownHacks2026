import json
import math
import os
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

load_dotenv()

# Use project root for data files
_project_root = os.path.join(os.path.dirname(__file__), "..", "..")
BASELINE_PATH = os.path.join(_project_root, "train_busyness_baseline_24h.json")
LIVE_PATH = os.path.join(_project_root, "train_busyness_live.json")

WINDOW_MINUTES = 20
LOOKAHEAD_MINUTES = 30

# Demo knobs (tune these)
FOOT_TRAFFIC_PER_SCORE_UNIT = 35.0
CONVERSION_RATE_TO_CUSTOMERS = 0.08


class ExtraCustomerEstimate(BaseModel):
    expected_customers_next_30_min: int = Field(..., ge=0)
    expected_extra_customers_next_30_min: int = Field(..., ge=0)
    confidence_0_to_1: float = Field(..., ge=0.0, le=1.0)
    main_drivers: List[str] = Field(..., min_items=1, max_items=6)
    notes: Optional[str] = None
    


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def get_hour_bucket(ts: int) -> int:
    return datetime.fromtimestamp(ts, tz=timezone.utc).hour


def filter_baseline_to_hour_and_first_window(trains: List[Dict[str, Any]], hour: int, window_minutes: int):
    """
    Baseline has 24h of arrivals. For a fair comparison, slice to:
    - same UTC hour as live
    - arrivals happening in minute 0..window_minutes of that hour (ex 10:00–10:20)
    """
    out = []
    for t in trains:
        if get_hour_bucket(t["arrival_ts"]) != hour:
            continue
        dt = datetime.fromtimestamp(t["arrival_ts"], tz=timezone.utc)
        minutes_into_hour = dt.minute + dt.second / 60.0
        if 0 <= minutes_into_hour <= window_minutes:
            out.append(t)
    return out


def summarize_window(trains: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not trains:
        return {
            "train_count": 0,
            "score_sum": 0.0,
            "score_avg": 0.0,
            "bunched_count": 0,
            "delayed_count": 0,
            "top_routes": [],
        }

    score_sum = sum(float(t.get("busy_score_0_to_1", 0.0)) for t in trains)
    bunched_count = sum(1 for t in trains if t.get("bunching") is True)
    delayed_count = sum(1 for t in trains if float(t.get("delay_min", 0.0)) >= 1.0)

    route_counts: Dict[str, int] = {}
    for t in trains:
        r = t.get("route_id") or "?"
        route_counts[r] = route_counts.get(r, 0) + 1

    top_routes = sorted(route_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "train_count": len(trains),
        "score_sum": round(score_sum, 3),
        "score_avg": round(score_sum / len(trains), 3),
        "bunched_count": bunched_count,
        "delayed_count": delayed_count,
        "top_routes": top_routes,
    }


def compute_numeric_prior(live_summary: Dict[str, Any], base_summary: Dict[str, Any]) -> Dict[str, Any]:
    delta_score = float(live_summary["score_sum"]) - float(base_summary["score_sum"])
    delta_score = max(delta_score, 0.0)

    extra_people = delta_score * FOOT_TRAFFIC_PER_SCORE_UNIT
    extra_customers = extra_people * CONVERSION_RATE_TO_CUSTOMERS

    return {
        "delta_score_sum": round(delta_score, 3),
        "extra_people_prior": round(extra_people, 1),
        "extra_customers_prior": int(round(extra_customers)),
    }


def build_inputs(_: Any) -> Dict[str, Any]:
    live = load_json(LIVE_PATH)
    baseline = load_json(BASELINE_PATH)

    live_dt = datetime.fromisoformat(live["generated_at"].replace("Z", "+00:00"))
    hour = live_dt.hour

    live_trains = live["trains"]
    baseline_slice = filter_baseline_to_hour_and_first_window(
        baseline["trains"], hour=hour, window_minutes=WINDOW_MINUTES
    )

    live_summary = summarize_window(live_trains)
    base_summary = summarize_window(baseline_slice)
    prior = compute_numeric_prior(live_summary, base_summary)

    return {
        "hour_bucket_utc": hour,
        "live_summary": live_summary,
        "baseline_summary": base_summary,
        "prior": prior,
        "live_sample": sorted(live_trains, key=lambda x: x.get("minutes_away", 999))[:12],
        "baseline_sample": sorted(baseline_slice, key=lambda x: x["arrival_ts"])[:12],
        "assumptions": {
            "lookahead_minutes": LOOKAHEAD_MINUTES,
            "foot_traffic_per_score_unit": FOOT_TRAFFIC_PER_SCORE_UNIT,
            "conversion_rate_to_customers": CONVERSION_RATE_TO_CUSTOMERS,
            "note": "Use numeric prior as a baseline and adjust conservatively."
        },
    }


def run_mta_forecast() -> dict:
    # ✅ Gemini model via LangChain
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.2
        )

        # Structured output: if your version supports it, this is clean.
        # If it throws, tell me the exact error and I’ll swap to a JSON parser fallback.
    structured_llm = llm.with_structured_output(ExtraCustomerEstimate)

    prompt = ChatPromptTemplate.from_messages([
        ("system",
        "You are a specialized demand forecasting agent for a SINGLE cafe located near NYC subway station exits.\n"
        "Your task is to estimate short-term customer demand caused by subway conditions.\n\n"
        "You will receive LIVE vs BASELINE train busyness summaries for the SAME UTC hour window.\n"
        "You MUST start from the numeric prior and only adjust conservatively.\n\n"
        "CAUSAL MODEL TO USE:\n"
        "- Increased subway crowding can increase sidewalk density near station exits.\n"
        "- Train bunching and delays cause people to wait, linger, or resurface near exits.\n"
        "- Only a small fraction of additional foot traffic converts to cafe customers.\n"
        "- This is a single cafe, not a station-wide retailer.\n\n"
        "Assume the cafe benefits more from delayed exits than from fast commuter throughput."
        "IMPORTANT CONSTRAINTS:\n"
        "- expected_extra_customers_next_30_min must be realistic (usually 0–15).\n"
        "- If signals are mixed or weak, stay close to the numeric prior.\n"
        "- Never invent large demand spikes without strong evidence.\n\n"
        "Return ONLY valid JSON with the required fields."
        ),
        ("human",
        "HOUR (UTC): {hour_bucket_utc}\n\n"
        "LIVE SUMMARY:\n{live_summary}\n\n"
        "BASELINE SUMMARY:\n{baseline_summary}\n\n"
        "NUMERIC PRIOR (ANCHOR — start here):\n{prior}\n\n"
        "LIVE TRAIN SAMPLE (soonest arrivals first):\n{live_sample}\n\n"
        "BASELINE TRAIN SAMPLE:\n{baseline_sample}\n\n"
        "ASSUMPTIONS:\n{assumptions}\n\n"
        "ADJUSTMENT GUIDELINES:\n"
        "- Higher live train_count vs baseline suggests more people exiting stations.\n"
        "- Higher score_avg or score_sum vs baseline increases foot traffic pressure.\n"
        "- Train bunching amplifies sidewalk congestion near exits.\n"
        "- Delays >= 1 min increase dwell time near station entrances.\n"
        "- If live conditions are similar to baseline, keep extra customers near the prior.\n\n"
        "OUTPUT JSON FIELDS:\n"
        "- expected_customers_next_30_min\n"
        "- expected_extra_customers_next_30_min\n"
        "- confidence_0_to_1\n"
        "- main_drivers (1–6 short bullets)\n"
        "- notes (optional)\n"
        )
    ])

    chain = (
        RunnableLambda(build_inputs)
        | prompt
        | structured_llm
    )
    result = chain.invoke({})
    return result.model_dump()


