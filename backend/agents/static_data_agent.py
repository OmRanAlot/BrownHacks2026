"""
Static Data Agent
Handles events and weather data (updated daily)
"""

from pymongo import MongoClient
from datetime import datetime
from typing import Dict, List


class StaticDataAgent:
    """Agent for static/cached data (events + weather)"""
    
    def __init__(self, mongo_client: MongoClient, weather_api):
        """
        Initialize static data agent
        
        Args:
            mongo_client: MongoDB client instance
            weather_api: Weather API instance
        """
        self.mongo_client = mongo_client
        self.db = mongo_client['nyc_business_optimizer']
        self.events_collection = self.db['events']
        self.weather_api = weather_api
    
    def get_nearby_events(
        self, 
        business_location: Dict, 
        date_range: Dict, 
        radius_km: float = 2
    ) -> List[Dict]:

        query = {
            "location": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [business_location['lng'], business_location['lat']]
                    },
                    "$maxDistance": radius_km * 1000  # Convert to meters
                }
            },
            "start_time": {
                "$gte": date_range['start'],
                "$lte": date_range['end']
            }
        }
        
        events = list(self.events_collection.find(query).limit(10))
        
        # Extract event names for summary (handle both formats)
        event_names = []
        for e in events:
            name = e.get('name') or e.get('event_name', 'Unknown Event')
            event_names.append(name)
        
        print(f"   📍 Found {len(events)} nearby events")
        if events:
            print(f"      Events: {', '.join(event_names[:3])}")
        
        return events
    def get_weather_data(self, date: datetime) -> Dict:
        """
        Get weather forecast from weather API
        
        Args:
            date: Target date for weather forecast
        
        Returns:
            Weather data dict with 'condition' and 'temp'
        """
        weather_data = self.weather_api.get_forecast(date)
        print(f"   🌤️  Weather: {weather_data['condition']}, {weather_data['temp']}°F")
        return weather_data
    
    def get_static_context(
        self, 
        business_location: Dict, 
        target_datetime: datetime
    ) -> Dict:
        """
        Get all static context for a given time and location
        
        Args:
            business_location: Business location dict
            target_datetime: Target prediction datetime
        
        Returns:
            Dict with events and weather data
        """
        print("\n📊 Gathering static data...")
        
        # Get events for the target day
        events = self.get_nearby_events(
            business_location=business_location,
            date_range={
                'start': target_datetime.replace(hour=0, minute=0),
                'end': target_datetime.replace(hour=23, minute=59)
            }
        )
        
        # Get weather
        weather = self.get_weather_data(target_datetime)
        
        # Create summary
        events_summary = ", ".join([e['name'] for e in events[:3]]) if events else "None"
        
        return {
            "events": events,
            "weather": weather,
            "events_summary": events_summary
        }


class MockWeatherAPI:
    """Mock weather API - replace with your actual weather API"""
    
    def get_forecast(self, date: datetime) -> Dict:
        """
        Mock weather forecast
        Replace with actual API call (OpenWeatherMap, Weather.gov, etc.)
        
        Returns:
            {"condition": str, "temp": int}
        """
        import random
        
        conditions = ["Clear", "Cloudy", "Rainy", "Snowy"]
        return {
            "condition": random.choice(conditions),
            "temp": random.randint(30, 75)
        }