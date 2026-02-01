from __future__ import annotations
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent          # .../backend/agents
REPO_ROOT = BASE_DIR.parent.parent                 # .../BROWNHACKS2026
DATA_PATH = REPO_ROOT / "detailed_cafe_congestion.json"

print("Loading:", DATA_PATH)
print("Exists?", DATA_PATH.exists())

with open(DATA_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

from datetime import datetime
from typing import Any, Dict, List, Optional

from uagents import Agent, Context, Model


# -------------------------
# REST Models
# -------------------------
class POIBusyness(Model):
    poi_name: str
    busyness_score: int
    current_speed: float
    free_flow_speed: float
    current_travel_time: float
    free_flow_travel_time: float
    confidence: float
    road_closure: bool


class SnapshotBusynessResponse(Model):
    snapshot_timestamp: str
    target_location: str
    overall_busyness_score: int
    pois: List[POIBusyness]


class POIOnlyResponse(Model):
    snapshot_timestamp: str
    poi_name: str
    busyness_score: int


# -------------------------
# Helpers
# -------------------------
def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def compute_busyness(traffic_data: Dict[str, Any]) -> int:
    """
    0 (free flow) -> 100 (very busy).
    Uses speed + travel-time slowdowns, weighted and confidence-adjusted.
    """
    current_speed = float(traffic_data.get("currentSpeed", 0) or 0)
    free_flow_speed = float(traffic_data.get("freeFlowSpeed", 0) or 0)

    current_tt = float(traffic_data.get("currentTravelTime", 0) or 0)
    free_flow_tt = float(traffic_data.get("freeFlowTravelTime", 0) or 0)

    confidence = float(traffic_data.get("confidence", 1) or 1)
    road_closure = bool(traffic_data.get("roadClosure", False))

    # Normalize confidence if it comes as 0..100
    if confidence > 1:
        confidence = confidence / 100.0
    confidence = clamp(confidence, 0.0, 1.0)

    if road_closure:
        return 100

    # Speed slowdown (0..1)
    speed_slow = 0.0
    if free_flow_speed > 0:
        speed_ratio = current_speed / free_flow_speed
        speed_slow = 1.0 - clamp(speed_ratio, 0.0, 1.0)

    # Travel time slowdown (0..1)
    time_slow = 0.0
    if current_tt > 0 and free_flow_tt > 0:
        time_ratio = free_flow_tt / current_tt
        time_slow = 1.0 - clamp(time_ratio, 0.0, 1.0)

    # Combine (tweak weights if you want)
    raw = 0.6 * speed_slow + 0.4 * time_slow

    # Confidence weighting
    raw *= confidence

    return int(round(100 * clamp(raw, 0.0, 1.0)))


def load_snapshot() -> Dict[str, Any]:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Could not find JSON at: {DATA_PATH}")

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "metadata" not in data or "points_of_interest" not in data:
        raise ValueError("JSON schema mismatch. Expected keys: metadata, points_of_interest")

    return data


def build_response(snapshot: Dict[str, Any]) -> SnapshotBusynessResponse:
    metadata = snapshot.get("metadata", {})
    snapshot_ts = str(metadata.get("timestamp", ""))
    target_location = str(metadata.get("target_location", ""))

    poi_entries = snapshot.get("points_of_interest", [])
    pois_out: List[POIBusyness] = []

    scores: List[int] = []

    for poi in poi_entries:
        name = str(poi.get("poi_name", "Unknown POI"))
        traffic_data = poi.get("traffic_data", {}) or {}

        score = compute_busyness(traffic_data)
        scores.append(score)

        pois_out.append(
            POIBusyness(
                poi_name=name,
                busyness_score=score,
                current_speed=float(traffic_data.get("currentSpeed", 0) or 0),
                free_flow_speed=float(traffic_data.get("freeFlowSpeed", 0) or 0),
                current_travel_time=float(traffic_data.get("currentTravelTime", 0) or 0),
                free_flow_travel_time=float(traffic_data.get("freeFlowTravelTime", 0) or 0),
                confidence=float(traffic_data.get("confidence", 1) or 1),
                road_closure=bool(traffic_data.get("roadClosure", False)),
            )
        )

    overall = int(round(sum(scores) / len(scores))) if scores else 0

    return SnapshotBusynessResponse(
        snapshot_timestamp=snapshot_ts,
        target_location=target_location,
        overall_busyness_score=overall,
        pois=pois_out,
    )


# -------------------------
# Agent setup
# -------------------------
agent = Agent(
    name="traffic_busyness_agent",
    seed="replace-with-a-real-seed",
)

print("📦 Loading snapshot from:", DATA_PATH)
SNAPSHOT = load_snapshot()
print("✅ Loaded snapshot timestamp:", SNAPSHOT.get("metadata", {}).get("timestamp"))


# -------------------------
# REST endpoints
# -------------------------
@agent.on_rest_get("/busyness/snapshot", response=SnapshotBusynessResponse)
async def get_snapshot_busyness(ctx: Context) -> SnapshotBusynessResponse:
    # If you later write new snapshots to the file, you can reload each request:
    # snapshot = load_snapshot()
    # return build_response(snapshot)

    return build_response(SNAPSHOT)


@agent.on_rest_get("/busyness/poi", response=POIOnlyResponse)
async def get_poi_busyness(ctx: Context) -> POIOnlyResponse:
    """
    Usage:
      /busyness/poi?name=Cafe%20Aroma
    """
    name_query = (ctx.query.get("name") or "").strip().lower()

    if not name_query:
        # Default: first POI
        poi0 = SNAPSHOT["points_of_interest"][0]
        score = compute_busyness(poi0.get("traffic_data", {}) or {})
        return POIOnlyResponse(
            snapshot_timestamp=str(SNAPSHOT["metadata"].get("timestamp", "")),
            poi_name=str(poi0.get("poi_name", "")),
            busyness_score=score,
        )

    for poi in SNAPSHOT.get("points_of_interest", []):
        poi_name = str(poi.get("poi_name", ""))
        if poi_name.lower() == name_query:
            score = compute_busyness(poi.get("traffic_data", {}) or {})
            return POIOnlyResponse(
                snapshot_timestamp=str(SNAPSHOT["metadata"].get("timestamp", "")),
                poi_name=poi_name,
                busyness_score=score,
            )

    # If not found, return a friendly "not found" style response
    return POIOnlyResponse(
        snapshot_timestamp=str(SNAPSHOT["metadata"].get("timestamp", "")),
        poi_name="NOT_FOUND",
        busyness_score=-1,
    )


if __name__ == "__main__":
    agent.run()
