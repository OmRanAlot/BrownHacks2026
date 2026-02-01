from google.transit import gtfs_realtime_pb2
import requests
from datetime import datetime

# Geofence for your cafe at 40.770530, -73.982456
# Only care about stops within these IDs (Lincoln Center area)
STATION_MAP = {
    "125": "66 St - Lincoln Center",
    "123": "72 St (Express Transfer)",
    "126": "59 St - Columbus Circle"
}

MTA_FEED_URL = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs"

def get_mta_pulse():
    """
    Fetches and filters MTA data specifically for the cafe's vicinity.
    Returns a clean list of context strings for the LLM.
    """
    try:
        response = requests.get(MTA_FEED_URL, timeout=5)
        response.raise_for_status()
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
    except Exception as e:
        return [f"Infrastructure Alert: MTA Data feed currently unavailable. Error: {e}"]

    pulse_reports = []
    now = datetime.now().timestamp()

    for entity in feed.entity:
        if not entity.HasField('trip_update'):
            continue
            
        for update in entity.trip_update.stop_time_update:
            stop_id = update.stop_id[:3]
            
            # 1. Spatial Filter: Only process if it's one of our target stations
            if stop_id in STATION_MAP:
                station_name = STATION_MAP[stop_id]
                direction = "Downtown" if update.stop_id.endswith("S") else "Uptown"
                
                # 2. Time Validation: Filter out past updates
                arrival_ts = update.arrival.time if update.HasField('arrival') else 0
                if arrival_ts < now:
                    continue
                
                minutes_away = round((arrival_ts - now) / 60, 1)
                if minutes_away > 20:
                    continue
                # 3. Contextual Weighting (Logic for the LLM)
                # Trains < 3 mins away create an immediate 'High' pulse
                intensity = "HIGH" if minutes_away < 3 else "MODERATE"
                
                msg = (
                    f"[{intensity} PULSE] A {direction} train arriving at {station_name} "
                    f"in {minutes_away} min. Estimated cafe impact in {minutes_away + 2} min."
                )
                pulse_reports.append(msg)

    # Sort by soonest arrival
    return sorted(list(set(pulse_reports)))[:15] # Return top 5 most relevant

if __name__ == "__main__":
    context_for_llm = get_mta_pulse()
    print("\n".join(context_for_llm))