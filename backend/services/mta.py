from datetime import datetime
from typing import Dict, List, Optional

import requests
from google.transit import gtfs_realtime_pb2

# Geofence for your cafe at 40.770530, -73.982456
# Only care about stops within these IDs (Lincoln Center area)
STATION_MAP = {
    "125": "66 St - Lincoln Center",
    "123": "72 St (Express Transfer)",
    "126": "59 St - Columbus Circle"
}

MTA_FEED_URL = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs"

def get_mta_pulse(
    api_key: Optional[str] = None,
    station_map: Optional[Dict[str, str]] = None,
    max_minutes: int = 20,
    max_results: int = 15,
) -> Dict:
    """
    Fetch and filter GTFS real-time data for nearby stations.

    Returns a structured payload that includes both machine-readable pulses and
    a compact list of LLM-friendly strings. This makes it easy to use the same
    output for analytics, logging, and RAG ingestion.
    """
    active_station_map = station_map or STATION_MAP

    try:
        # MTA's API requires an API key header for production usage.
        # If api_key is not provided, we still attempt a request to allow
        # local testing with a proxy or pre-authenticated environment.
        headers = {"x-api-key": api_key} if api_key else {}
        response = requests.get(MTA_FEED_URL, headers=headers, timeout=5)
        response.raise_for_status()
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
    except Exception as e:
        return {
            "pulses": [],
            "pulse_reports": [
                f"Infrastructure Alert: MTA Data feed currently unavailable. Error: {e}"
            ],
            "summary": {
                "total_pulses": 0,
                "high_pulses": 0,
                "moderate_pulses": 0,
            },
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "error": str(e),
        }

    pulses: List[Dict] = []
    now_ts = datetime.now().timestamp()

    for entity in feed.entity:
        if not entity.HasField("trip_update"):
            continue

        for update in entity.trip_update.stop_time_update:
            stop_id = update.stop_id[:3]

            # 1) Spatial filter: only process target stations for this business.
            if stop_id not in active_station_map:
                continue

            station_name = active_station_map[stop_id]
            direction = "Downtown" if update.stop_id.endswith("S") else "Uptown"

            # 2) Time validation: ignore past updates and long waits.
            arrival_ts = update.arrival.time if update.HasField("arrival") else 0
            if arrival_ts < now_ts:
                continue

            minutes_away = round((arrival_ts - now_ts) / 60, 1)
            if minutes_away > max_minutes:
                continue

            # 3) Contextual weighting: closer trains drive higher foot traffic.
            intensity = "HIGH" if minutes_away < 3 else "MODERATE"

            pulses.append(
                {
                    "station_id": stop_id,
                    "station": station_name,
                    "direction": direction,
                    "minutes_away": minutes_away,
                    "intensity": intensity,
                    "arrival_timestamp": arrival_ts,
                }
            )

    # Sort by soonest arrival for highest relevance.
    pulses = sorted(pulses, key=lambda p: p["minutes_away"])[:max_results]

    pulse_reports = [
        (
            f"[{pulse['intensity']} PULSE] A {pulse['direction']} train arriving at "
            f"{pulse['station']} in {pulse['minutes_away']} min. "
            f"Estimated cafe impact in {round(pulse['minutes_away'] + 2, 1)} min."
        )
        for pulse in pulses
    ]

    summary = {
        "total_pulses": len(pulses),
        "high_pulses": sum(1 for p in pulses if p["intensity"] == "HIGH"),
        "moderate_pulses": sum(1 for p in pulses if p["intensity"] == "MODERATE"),
    }

    return {
        "pulses": pulses,
        "pulse_reports": pulse_reports,
        "summary": summary,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }

if __name__ == "__main__":
    context = get_mta_pulse()
    print("\n".join(context["pulse_reports"]))