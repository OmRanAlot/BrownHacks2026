import os
import json
import re
from statistics import mean
from typing import Any, Dict, List, Optional

import dotenv
from pydantic import BaseModel, Field, ValidationError
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

dotenv.load_dotenv()
DATASET_PATH = os.path.join(os.path.dirname(__file__), "detailed_cafe_congestion.json")

GEMINI_MODEL = "gemini-2.5-flash"  # fast + great for hackathon

CLAMP_LO = -15.0
CLAMP_HI = 30.0

LOW_CONF_THRESHOLD = 0.35
LOW_CONF_SHRINK = 0.4

DIRECTION_DEADBAND_SEC = 15


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def weighted_avg(pairs: List[tuple]) -> Optional[float]:
    if not pairs:
        return None
    den = sum(w for _, w in pairs)
    if den == 0:
        return None
    return sum(v * w for v, w in pairs) / den


def safe_json_extract(text: str) -> Dict[str, Any]:
    text = text.strip()

    try:
        return json.loads(text)
    except Exception:
        pass

    m = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not m:
        raise ValueError("No JSON object found in model output.")
    candidate = m.group(0)

    try:
        return json.loads(candidate)
    except Exception:
        candidate2 = re.sub(r",\s*([}\]])", r"\1", candidate)
        return json.loads(candidate2)


def extract_features(dataset: Dict[str, Any]) -> Dict[str, Any]:
    pois = dataset.get("points_of_interest", [])
    if not pois:
        return {}

    congestion_ratios = []
    travel_time_deltas = []
    confidences = []
    road_closures = 0

    inbound_delays = []
    outbound_delays = []

    for p in pois:
        w = float(p.get("weight", 1.0))
        td = p.get("traffic_data") or {}

        cs = td.get("currentSpeed")
        fs = td.get("freeFlowSpeed")
        ctt = td.get("currentTravelTime")
        ftt = td.get("freeFlowTravelTime")
        conf = td.get("confidence")
        rc = td.get("roadClosure")

        if cs is not None and fs not in (None, 0):
            congestion_ratios.append((float(cs) / float(fs), w))

        if ctt is not None and ftt is not None:
            travel_time_deltas.append((float(ctt) - float(ftt), w))

        if conf is not None:
            confidences.append(float(conf))

        if rc is True:
            road_closures += 1

        dt = p.get("directional_traffic") or {}
        to_cafe = dt.get("to_cafe") or {}
        from_cafe = dt.get("from_cafe") or {}

        in_d = to_cafe.get("trafficDelayInSeconds")
        out_d = from_cafe.get("trafficDelayInSeconds")

        if in_d is not None:
            inbound_delays.append((float(in_d), w))
        if out_d is not None:
            outbound_delays.append((float(out_d), w))

    avg_ratio = weighted_avg(congestion_ratios)
    avg_tt_delta = weighted_avg(travel_time_deltas)
    inbound_delay = weighted_avg(inbound_delays)
    outbound_delay = weighted_avg(outbound_delays)

    direction_bias = None
    if inbound_delay is not None and outbound_delay is not None:
        direction_bias = inbound_delay - outbound_delay

    bad_count = 0
    ratio_count = 0
    for r, _w in congestion_ratios:
        ratio_count += 1
        if r < 0.7:
            bad_count += 1
    bad_share = (bad_count / ratio_count) if ratio_count else None

    dominant_direction = "unknown"
    if direction_bias is not None:
        if abs(direction_bias) <= DIRECTION_DEADBAND_SEC:
            dominant_direction = "balanced"
        elif direction_bias > 0:
            dominant_direction = "towards_cafe"
        else:
            dominant_direction = "away_from_cafe"

    return {
        "avg_congestion_ratio": avg_ratio,
        "avg_travel_time_delta_sec": avg_tt_delta,
        "inbound_delay_sec_weighted": inbound_delay,
        "outbound_delay_sec_weighted": outbound_delay,
        "direction_bias_sec": direction_bias,
        "dominant_direction": dominant_direction,
        "road_closure_count": road_closures,
        "confidence_avg": mean(confidences) if confidences else None,
        "bad_congestion_share": bad_share,
        "poi_count": len(pois),
        "timestamp": (dataset.get("metadata") or {}).get("timestamp"),
    }


class ExtraCustomersOut(BaseModel):
    expected_extra_customers_per_hour: float = Field(...)
    confidence_0_to_1: float = Field(..., ge=0.0, le=1.0)
    rationale_bullets: List[str] = Field(..., min_length=1)
    cautions: List[str] = Field(default_factory=list)


# ✅ IMPORTANT: escaped braces with {{ and }}
PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are a specialized Google Traffic interpretation agent for a SINGLE, fixed NYC cafe location.\n"
     "Your job is to estimate how nearby road congestion affects walk-in customers per hour.\n\n"
     "You MUST output ONLY valid JSON (no markdown, no commentary).\n\n"
     "Think causally:\n"
     "- Traffic does NOT equal customers by default.\n"
     "- Only congestion that increases pedestrian exposure or delays people NEAR the cafe increases walk-ins.\n"
     "- Direction matters more than raw congestion.\n\n"
     "Return JSON with EXACTLY these keys:\n"
     "{{\n"
     '  "expected_extra_customers_per_hour": number,\n'
     '  "confidence_0_to_1": number,\n'
     '  "rationale_bullets": string[],\n'
     '  "cautions": string[]\n'
     "}}\n"),
    ("user",
     "CAFE CONTEXT:\n"
     "- This is the SAME cafe every time (hardcoded location).\n"
     "- We are estimating incremental walk-ins caused by nearby traffic patterns.\n\n"
     "BASELINE CUSTOMERS PER HOUR (anchor): {baseline}\n\n"
     "GOOGLE TRAFFIC FEATURES (already extracted):\n{features}\n\n"
     "INTERPRETATION RULES:\n"
     "- avg_congestion_ratio < 0.8 across multiple POIs indicates meaningful slowdown.\n"
     "- inbound_delay_sec_weighted > outbound_delay_sec_weighted suggests traffic flowing TOWARD the cafe.\n"
     "- dominant_direction = 'towards_cafe' increases likelihood of walk-ins.\n"
     "- dominant_direction = 'away_from_cafe' REDUCES or negates extra customers.\n"
     "- Road closures can either help (forced proximity) or hurt (blocked access); be cautious.\n"
     "- If bad_congestion_share is low, traffic impact is likely noise.\n"
     "- If confidence_avg is missing or < 0.5, keep prediction very close to 0.\n\n"
     "OUTPUT GUIDELINES:\n"
     "- expected_extra_customers_per_hour should usually be between -15 and +30.\n"
     "- Use negative values if traffic likely discourages access.\n"
     "- Be conservative unless multiple signals agree.\n"
     "- rationale_bullets should reference specific features (direction, delays, congestion).\n\n"
     "Now output ONLY the JSON.\n")
])


def forecast_extra_customers(
    dataset_path: str,
    baseline_customers_per_hour: float,
    temperature: float = 0.4
) -> Dict[str, Any]:
    if not os.getenv("GOOGLE_API_KEY"):
        raise RuntimeError(
            "Missing GOOGLE_API_KEY. Put it in your .env as GOOGLE_API_KEY=... and restart your terminal/IDE."
        )

    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    features = extract_features(dataset)

    llm = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        temperature=temperature,
    )

    msg = (PROMPT | llm).invoke({
        "baseline": baseline_customers_per_hour,
        "features": json.dumps(features, indent=2),
    })

    raw_text = getattr(msg, "content", str(msg))

    try:
        parsed = safe_json_extract(raw_text)
        result = ExtraCustomersOut(**parsed)
    except (ValueError, ValidationError) as e:
        return {
            "expected_extra_customers_per_hour": 0.0,
            "confidence_0_to_1": 0.15,
            "rationale_bullets": ["Model output failed parsing/validation; defaulting to 0 extra customers."],
            "cautions": [str(e)],
            "raw_model_output": raw_text[:800],
            "features_used": features
        }

    # Guardrails
    result.expected_extra_customers_per_hour = float(
        clamp(result.expected_extra_customers_per_hour, CLAMP_LO, CLAMP_HI)
    )

    if result.confidence_0_to_1 < LOW_CONF_THRESHOLD:
        result.expected_extra_customers_per_hour *= LOW_CONF_SHRINK

    # Optional: clamp relative to baseline
    result.expected_extra_customers_per_hour = float(
        clamp(
            result.expected_extra_customers_per_hour,
            -0.8 * baseline_customers_per_hour,
            1.2 * baseline_customers_per_hour,
        )
    )

    out = result.model_dump()
    out["features_used"] = features
    return out


if __name__ == "__main__":
    baseline = 42.0  # replace with your baseline customers/hour for this day+hour
    output = forecast_extra_customers(DATASET_PATH, baseline)
    print(json.dumps(output, indent=2))
