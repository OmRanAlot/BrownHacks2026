import logging
import os
from datetime import datetime, timedelta

import dotenv
import pandas as pd
from pymongo import UpdateOne
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from sodapy import Socrata

try:
    from .geocoding import geocode_location
except ImportError:
    from geocoding import geocode_location

dotenv.load_dotenv()

# --- Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("event_engine")

USER = os.getenv("MONGODB_USR")
PW = os.getenv("MONGODB_PW")

uri = os.getenv("MONGODB_URI")

mongo_client = MongoClient(uri, server_api=ServerApi("1"))
db = mongo_client["event_engine"]
collection = db["events"]


def search_event_by_id(event_id: str) -> dict | None:
    """
    Look up an event by event_id in MongoDB. Usable from outside this module.
    Returns the full event document or None if not found.
    """
    doc = collection.find_one({"event_id": str(event_id)})
    if doc:
        doc.pop("_id", None)  # omit MongoDB _id for cleaner return
    return doc


try:
    mongo_client.admin.command("ping")
    log.info("Connected to MongoDB")
except Exception as e:
    log.error("MongoDB connection failed: %s", e)


class EventEngine:
    def __init__(self, time_window: int = 7):
        self.DOMAIN = "data.cityofnewyork.us"
        self.DATASET_ID = "tvpp-9vvx"
        self.APP_TOKEN = os.getenv("APP_TOKEN")
        self.VENUE_KEYWORDS = ["park", "field", "playground", "plgd"]
        self.client = Socrata(self.DOMAIN, self.APP_TOKEN)
        self.Cafe_LAT = 40.770534
        self.Cafe_LON = -73.982447
        self.time_window = time_window
        log.info("EventEngine initialized (time_window=%d days)", time_window)

    def get_events(self):
        now = datetime.now()
        end_date = now + timedelta(days=self.time_window)
        now_str = now.strftime("%Y-%m-%dT%H:%M:%S")
        end_str = end_date.strftime("%Y-%m-%dT%H:%M:%S")

        log.info("Fetching events from API (%s to %s)", now_str, end_str)
        results = self.client.get(
            self.DATASET_ID,
            select="event_id, event_name, start_date_time, event_type, event_location, event_borough",
            where=f"start_date_time >= '{now_str}' AND start_date_time <= '{end_str}' AND event_borough = 'Manhattan'",
            limit=5000,
        )
        log.info("Fetched %d raw events from API", len(results))

        api_event_ids = [r.get("event_id") for r in results if r.get("event_id")]
        cached_docs = {
            str(doc["event_id"]): doc
            for doc in collection.find({"event_id": {"$in": api_event_ids}})
        }
        log.info("Found %d cached events in MongoDB", len(cached_docs))

        processed = []
        new_events = []
        for result in results:
            event_id = result.get("event_id")
            if not event_id:
                continue

            event_id_str = str(event_id)
            if event_id_str in cached_docs:
                doc = cached_docs[event_id_str].copy()
                doc.pop("_id", None)
                processed.append(doc)
                log.debug("Cache hit: event_id=%s", event_id_str)
                continue

            event_location = result["event_location"]
            venue_substring = self.extract_substring_to_keyword(event_location)
            result["venue_substring"] = venue_substring

            log.debug("Geocoding event_id=%s: %s", event_id_str, event_location[:50])
            coords = self.get_event_coordinates(event_location)
            if coords is not None:
                result["latitude"] = coords[0]
                result["longitude"] = coords[1]
            else:
                result["latitude"] = None
                result["longitude"] = None

            processed.append(result)
            new_events.append(result)

        cached_count = len(processed) - len(new_events)
        log.info("Processed %d events (%d from cache, %d geocoded)", len(processed), cached_count, len(new_events))

        if new_events:
            write_result = self.write_events_to_mongo(new_events)
            log.info("MongoDB write: inserted=%d, updated=%d, matched=%d", write_result["inserted"], write_result["updated"], write_result["matched"])

        return processed

    def extract_substring_to_keyword(self, loc: str) -> str | None:
        """
        If any of VENUE_KEYWORDS is in loc (case-insensitive), return substring from
        start through the end of the first-occurring keyword. Otherwise return None.
        """
        if pd.isna(loc) or not isinstance(loc, str):
            return None
        loc_lower = loc.lower()
        earliest_end = None  # (start_idx, end_idx) of earliest keyword
        for kw in self.VENUE_KEYWORDS:
            idx = loc_lower.find(kw)
            if idx != -1:
                end_idx = idx + len(kw)
                if earliest_end is None or idx < earliest_end[0]:
                    earliest_end = (idx, end_idx)
        if earliest_end is None:
            return None
        return loc[: earliest_end[1]].strip()

    def get_event_coordinates(self, event_location: str) -> tuple[float, float] | None:
        location = geocode_location(event_location + ", New York, NY")
        if location.coordinates is None:
            return None
        return location.coordinates

    def write_events_to_mongo(self, events: list[dict], upsert: bool = True) -> dict:
        """
        Write event data to MongoDB. Uses event_id as unique key; existing docs
        are updated when upsert=True. Returns inserted/updated counts.
        """
        if not events:
            log.debug("write_events_to_mongo: no events to write")
            return {"inserted": 0, "updated": 0, "matched": 0}

        operations = []
        for event in events:
            doc = {k: v for k, v in event.items() if v is not None}
            event_id = doc.get("event_id")
            if not event_id:
                log.warning("Skipping event with no event_id: %s", event)
                continue
            operations.append(
                UpdateOne({"event_id": event_id}, {"$set": doc}, upsert=upsert)
            )

        result = collection.bulk_write(operations)
        return {
            "inserted": result.upserted_count,
            "updated": result.modified_count,
            "matched": result.matched_count,
        }


if __name__ == "__main__":
    start = datetime.now()
    log.info("Starting event engine run")

    event_engine = EventEngine()
    events = event_engine.get_events()

    elapsed = datetime.now() - start
    log.info("Completed: %d events in %s", len(events), elapsed)