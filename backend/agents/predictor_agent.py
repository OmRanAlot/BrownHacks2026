import os
import json
from datetime import datetime, date as date_type
from pinecone import Pinecone
from openai import OpenAI
from dotenv import load_dotenv
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from services.weather import fetch_hourly_weather

load_dotenv()

# Default NYC location for weather when predicting by date/time
DEFAULT_LAT, DEFAULT_LON = 40.770530, -73.982456

# Configuration
PINECONE_INDEX = "manual-foot-traffic-vectors"
NAMESPACE = "traffic-data"

# 1. Initialize Clients
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(PINECONE_INDEX)
openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
gemini = os.getenv("GEMINI_API_KEY")

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=gemini,
)


def _build_query_text_from_datetime(
    date=None,
    time=None,
    *,
    borough="Manhattan",
    business_type="cafe",
    location="NYC",
    events="",
    lat=DEFAULT_LAT,
    lon=DEFAULT_LON,
):
    """
    Build embedding-style query text from date/time and optional context.
    date: str "YYYY-MM-DD" or date object; default today.
    time: str "HH:MM" or "H:MM", or int hour 0-23; default current hour.
    """
    now = datetime.now()
    if date is None and time is None:
        dt = now
    elif date is None:
        dt = now
        if isinstance(time, int):
            dt = dt.replace(hour=min(23, max(0, time)), minute=0, second=0, microsecond=0)
        elif isinstance(time, str):
            parts = time.strip().split(":")
            dt = dt.replace(hour=min(23, max(0, int(parts[0]))), minute=int(parts[1]) if len(parts) > 1 else 0, second=0, microsecond=0)
    else:
        if isinstance(date, str):
            date_str = date.strip()
            if "T" in date_str:
                dt = datetime.fromisoformat(date_str.replace("Z", ""))
            else:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
            if time is not None:
                if isinstance(time, int):
                    dt = dt.replace(hour=min(23, max(0, time)), minute=0, second=0, microsecond=0)
                elif isinstance(time, str):
                    parts = time.strip().split(":")
                    dt = dt.replace(hour=min(23, max(0, int(parts[0]))), minute=int(parts[1]) if len(parts) > 1 else 0, second=0, microsecond=0)
        else:
            dt = date if hasattr(date, "hour") else datetime.combine(date, now.time()) if isinstance(date, date_type) else date
            if time is not None:
                if isinstance(time, int):
                    dt = dt.replace(hour=min(23, max(0, time)), minute=0, second=0, microsecond=0)
                elif isinstance(time, str):
                    parts = time.strip().split(":")
                    dt = dt.replace(hour=min(23, max(0, int(parts[0]))), minute=int(parts[1]) if len(parts) > 1 else 0, second=0, microsecond=0)

    hour = dt.hour
    month = dt.month
    if month in (12, 1, 2):
        season = "Winter"
    elif month in (3, 4, 5):
        season = "Spring"
    elif month in (6, 7, 8):
        season = "Summer"
    else:
        season = "Fall"
    is_holiday = False

    _, hourly_weather = fetch_hourly_weather(lat, lon, 24)
    weather_at_hour = hourly_weather[hour] if hour < len(hourly_weather) else hourly_weather[-1]
    weather_condition = weather_at_hour.get("condition", "Unknown")
    temperature = weather_at_hour.get("temp_f", 70)

    text_to_embed = (
        f"Borough: {borough}, "
        f"Business: {business_type}, "
        f"Weather: {weather_condition}, "
        f"Events: {events or 'None'}, "
        f"Location: {location}, "
        f"Temperature: {temperature}, "
        f"Season: {season}, "
        f"Is Holiday: {is_holiday}, "
        f"Hour: {hour}, "
    )
    return text_to_embed, dt


def _run_prediction(query_text, top_k=3):
    """RAG + LLM prediction; returns parsed JSON and raw response text."""
    search_results = index.search(
        namespace=NAMESPACE,
        query={
            "inputs": {"text": query_text},
            "top_k": top_k,
            "filter": {"foot_traffic": {"$exists": True}},
        },
        fields=["embedding_text", "foot_traffic"],
    )
    historical_context = ""
    result = search_results.result
    hits = result.hits if hasattr(result, "hits") else []
    for hit in hits:
        fields = getattr(hit, "fields", None) or {}
        emb = fields.get("embedding_text", "")
        traffic = fields.get("foot_traffic", "?")
        historical_context += f"- Past Record: {emb} | ACTUAL TRAFFIC: {traffic}\n"

    prompt = f"""
        You are a specialized NYC foot traffic prediction agent for small businesses (especially cafes).

        Your task is to estimate expected foot traffic for a TARGET time window using:
        - Retrieved historical records (if any)
        - Weather conditions
        - Nearby events
        - Common NYC pedestrian behavior

        IMPORTANT RULES:
        - If HISTORY exists, anchor your estimate to similar past records.
        - If HISTORY is sparse or missing, use NYC common-sense reasoning.
        - Weather and major events should have a measurable impact.
        - Assume foot traffic is the number of people likely to walk past or enter within the hour.
        - Cafes are more sensitive to weather and events than offices.

        WEIGHTING GUIDELINES (use implicitly):
        - Major nearby event (concert/sports): +15–40%
        - Light rain: −5–10%
        - Heavy rain/snow/extreme cold: −15–35%
        - Mild weather (60–75°F): +5–15%
        - Evening hours (5–8 PM): generally higher traffic
        - Winter reduces baseline foot traffic unless events offset it

        HISTORY (examples of similar past conditions):
        {historical_context if historical_context else "No close historical matches found."}

        TARGET CONTEXT:
        {query_text}

        OUTPUT REQUIREMENTS:
        Return ONLY valid JSON (no markdown, no extra text).

        Schema:
        {{
        "predicted_traffic": number,        // estimated people for this hour
        "confidence": number,               // float between 0 and 1
        "reasoning": string,                // ONE concise sentence
        "time": string                      // hour of day, e.g. "18:00"
        }}
        """

    response = client.chat.completions.create(
        model="google/gemini-3-flash-preview",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content
    try:
        return json.loads(raw), raw
    except json.JSONDecodeError:
        return {"predicted_traffic": None, "reasoning": raw, "time": None}, raw


def predict_for_datetime(date=None, time=None, borough="Manhattan", business_type="cafe", **kwargs):
    """
    Predict foot traffic for a given date and/or time (no record ID needed).

    Args:
        date: "YYYY-MM-DD" or datetime.date; default today.
        time: "HH:MM" or hour (0-23); default current hour.
        borough: e.g. "Manhattan".
        business_type: e.g. "cafe".
        **kwargs: passed to _build_query_text_from_datetime (location, events, lat, lon).

    Returns:
        dict with keys: predicted_traffic, reasoning, time, query_text, target_datetime.
    """
    
    query_text, target_dt = _build_query_text_from_datetime(
        date=date, time=time, borough=borough, business_type=business_type, **kwargs
    )




    payload, raw = _run_prediction(query_text)
    return {
        "predicted_traffic": payload.get("predicted_traffic"),
        "reasoning": payload.get("reasoning", raw),
        "time": payload.get("time"),
        "query_text": query_text,
        "target_datetime": target_dt.isoformat(),
    }


def predict_missing_metrics(target_ids):
    """
    Iterates through IDs that lack foot_traffic and predicts them.
    """
    for record_id in target_ids:
        # A. Fetch the 'Future' record details from Pinecone
        # We need the embedding_text to use as a query for the past
        target_record = index.fetch(ids=[record_id], namespace=NAMESPACE)
        record = target_record["vectors"].get(record_id)
        if not record:
            print(f"Record {record_id} not found, skipping.")
            continue
        # Records use flat fields; embedding_text may be in metadata or at top level
        meta = getattr(record, "metadata", None) or {}
        query_text = meta.get("embedding_text") if isinstance(meta, dict) else None
        query_text = query_text or getattr(record, "embedding_text", None)
        if not query_text:
            print(f"Record {record_id} has no embedding_text, skipping.")
            continue

        print(f"--- Predicting for {record_id} ---")
        print(f"Target Context: {query_text}")
        payload, raw = _run_prediction(query_text)
        print(raw)
        # Optional: upsert predicted_traffic back to Pinecone for this record_id
# --- EXECUTION ---
# predict_missing_metrics(["event_896004"])
# predict_for_datetime(date="2026-01-31", time=18)  # 6 PM
# predict_for_datetime(time="14:30")  # today at 2:30 PM
# predict_for_datetime(date="2026-02-01")  # tomorrow, default hour
if __name__ == "__main__":
    result = predict_for_datetime(date="2026-02-01", time=9)
    print(json.dumps(result, indent=2))