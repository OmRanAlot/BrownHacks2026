import json
import os
from datetime import datetime
from pinecone import Pinecone
from dotenv import load_dotenv
from pymongo import MongoClient
import time
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.weather import fetch_hourly_weather
load_dotenv()

mongo_client = MongoClient(os.getenv("MONGODB_URI"))
db = mongo_client["event_engine"]
collection = db["events"]

# 1. Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("manual-foot-traffic-vectors")

# print(collection.find_one())

weather_data = fetch_hourly_weather(40.770530, -73.982456, 24)


# print("=="*30)

# print(weather_data[1][0])
# print("=="*30)
# exit()
# 2. Sample Data (Replace with your actual Mongo/Weather fetching logic)
# mongo_event = 


# 3. Flatten into Natural Language
def create_training_string(event, weather):
    # Convert ISO strings to readable dates for the embedding model
    dt = datetime.fromisoformat(event["start_date_time"].replace("Z", ""))
    readable_date = dt.strftime("%B %d at %I:%M %p")
    event_borough = event["event_borough"]
    event_location = event["event_location"]
    event_name = event["event_name"]
    business_type = "cafe"
    hour = dt.hour
    # print(weather[hour])
    weather_condition = weather[hour]["condition"]
    temperature = weather[hour]["temp_f"]
    season = "Winter"
    is_holiday = False

    text_to_embed = (
        f"Borough: {event_borough}, "
        f"Business: {business_type}, "
        f"Weather: {weather_condition}, "
        f"Events: {event_name}, "
        f"Location: {event_location}, "
        f"Temperature: {temperature}, "
        f"Season: {season}, "
        f"Is Holiday: {is_holiday}, "
        f"Hour: {hour}, "
    )


    return text_to_embed

all_records = []
# 4. Prepare Record for Pinecone
hourly_weather = weather_data[1]  # list of hourly dicts
for event in collection.find():
    text_to_embed = create_training_string(event, weather_data[1])
    event_hour = datetime.fromisoformat(event["start_date_time"].replace("Z", "")).hour
    record = {
        "id": f"event_{event.get('event_id', 'unique_id')}",
        "embedding_text": text_to_embed,
        # Metadata must be flat top-level fields (string, number, boolean, or list of strings)
        "borough": str(event["event_borough"]),
        "temp": float(hourly_weather[event_hour]["temp_f"]),
        "event_type": str(event.get("event_type", "Sport")),
        "date": str(event["start_date_time"]),
    }
    all_records.append(record)
    print(f"appending record")

# Pinecone batch limit is 96 records per request
BATCH_SIZE = 90
for i in range(0, len(all_records), BATCH_SIZE):
    batch = all_records[i : i + BATCH_SIZE]
    index.upsert_records(namespace="traffic-data", records=batch)
    print(f"Upserted batch {i // BATCH_SIZE + 1} ({len(batch)} records)")
    time.sleep(5)