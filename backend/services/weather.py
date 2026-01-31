import requests
import json
from datetime import datetime

# Small, practical mapping for Open-Meteo's weather_code (WMO interpretation codes)
# The API returns weather_code as a number. :contentReference[oaicite:1]{index=1}
WEATHER_CODE_LABELS = {
    0: "Clear",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}

def fetch_hourly_weather(lat: float, lon: float, hours: int = 24, timezone: str = "auto"):
    """
    Fetch hourly weather data from Open-Meteo and return the next `hours` rows
    as a list of dicts suitable for an LLM feed.
    """
    base_url = "https://api.open-meteo.com/v1/forecast"

    # Hourly variables chosen for "going out" relevance:
    # - temp + feels-like (apparent)
    # - precipitation + probability
    # - wind speed + gusts (affects comfort, umbrellas, walking)
    # - cloud cover (affects vibe + sunlight)
    # - visibility (fog, heavy precip)
    # - UV index (daytime outdoor activity)
    # - weather_code (simple condition categorization)
    # These variables are requested via the hourly parameter. :contentReference[oaicite:2]{index=2}
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join([
            "temperature_2m",
            "apparent_temperature",
            "precipitation",
            "precipitation_probability",
            "weather_code",
            "wind_speed_10m",
            "wind_gusts_10m",
            "cloud_cover",
            "visibility",
            "uv_index",
            "is_day",
        ]),
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
        "precipitation_unit": "inch",
        "timezone": timezone,
    }

    r = requests.get(base_url, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()

    hourly = data.get("hourly", {})
    times = hourly.get("time", [])

    # Helper to safely pull an array and index it
    def val(key, i, default=None):
        arr = hourly.get(key, [])
        return arr[i] if i < len(arr) else default

    out = []
    for i in range(min(hours, len(times))):
        code = val("weather_code", i)
        out.append({
            "time": times[i],
            "is_day": bool(val("is_day", i, 0)),
            "temp_f": val("temperature_2m", i),
            "feels_like_f": val("apparent_temperature", i),
            "precip_in": val("precipitation", i),
            "precip_prob_percent": val("precipitation_probability", i),
            "wind_mph": val("wind_speed_10m", i),
            "wind_gust_mph": val("wind_gusts_10m", i),
            "cloud_cover_percent": val("cloud_cover", i),
            "visibility_m": val("visibility", i),
            "uv_index": val("uv_index", i),
            "weather_code": code,
            "condition": WEATHER_CODE_LABELS.get(code, "Unknown"),
        })

    meta = {
        "lat": lat,
        "lon": lon,
        "timezone": data.get("timezone"),
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "hours_returned": len(out),
    }

    return meta, out


if __name__ == "__main__":
    # Example: Brown University (Providence, RI)
    LAT, LON = 41.8268, -71.4025

    meta, llm_feed = fetch_hourly_weather(LAT, LON, hours=24, timezone="America/New_York")

    payload = {"meta": meta, "hourly": llm_feed}

    with open("llm_weather_input_openmeteo.json", "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print("\n--- COPY JSON BELOW ---\n")
    print(json.dumps(payload, indent=2))
    print("\n--- END JSON ---\n")
    print("Saved to: llm_weather_input_openmeteo.json")
