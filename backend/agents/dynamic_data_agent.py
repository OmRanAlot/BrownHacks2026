"""
Dynamic Data Agent
Handles real-time foot traffic and MTA subway data
"""

from typing import Dict, List
from datetime import datetime


class DynamicDataAgent:
    """Agent for real-time/dynamic data (foot traffic, MTA)"""
    
    def __init__(self, google_api_key: str = None, mta_api_key: str = None):
        """
        Initialize dynamic data agent
        
        Args:
            google_api_key: Google API key for foot traffic data
            mta_api_key: MTA API key for subway data
        """
        self.google_api_key = google_api_key
        self.mta_api_key = mta_api_key
    
    def get_current_foot_traffic(self, location: Dict) -> int:
        """
        Get real-time foot traffic from Google Popular Times or similar API
        
        Args:
            location: {"lat": float, "lng": float, "borough": str}
        
        Returns:
            Current foot traffic count (people per hour)
        """
        print(f"   📡 Fetching current foot traffic for {location['borough']}...")
        
        # TODO: Replace with actual Google Popular Times API
        # Example libraries:
        # - populartimes
        # - google-places API
        
        # For hackathon demo - mock data based on time of day
        import random
        current_hour = datetime.now().hour
        
        # Simulate traffic patterns
        if 7 <= current_hour <= 9:  # Morning rush
            base_traffic = 600
        elif 11 <= current_hour <= 14:  # Lunch
            base_traffic = 700
        elif 17 <= current_hour <= 20:  # Dinner/evening
            base_traffic = 800
        else:  # Off-peak
            base_traffic = 300
        
        # Add randomness
        current_traffic = base_traffic + random.randint(-100, 100)
        
        print(f"      Current traffic: {current_traffic} people/hour")
        return current_traffic
    
    def get_mta_traffic(self, nearby_stations: List[str]) -> Dict:
        """
        Get real-time MTA subway traffic data
        
        Args:
            nearby_stations: List of nearby station names
        
        Returns:
            Dict with MTA traffic metrics
        """
        print(f"   🚇 Fetching MTA data for {len(nearby_stations)} stations...")
        
        if not nearby_stations:
            return {
                "total_entries": 0,
                "total_exits": 0,
                "stations": []
            }
        
        # TODO: Replace with actual MTA API
        # MTA Real-Time Data API: https://api.mta.info/
        # You'll need gtfs-realtime-bindings library
        
        # For hackathon demo - mock data
        import random
        
        station_data = []
        total_entries = 0
        
        for station in nearby_stations:
            entries = random.randint(500, 2000)
            exits = int(entries * random.uniform(0.9, 1.1))
            
            station_data.append({
                "station": station,
                "entries": entries,
                "exits": exits
            })
            
            total_entries += entries
        
        mta_data = {
            "total_entries": total_entries,
            "total_exits": sum(s['exits'] for s in station_data),
            "stations": station_data,
            "timestamp": datetime.now()
        }
        
        print(f"      Total MTA entries: {mta_data['total_entries']}")
        return mta_data
    
    def get_dynamic_context(
        self, 
        business_location: Dict, 
        nearby_stations: List[str]
    ) -> Dict:
        """
        Get all dynamic context for current moment
        
        Args:
            business_location: Business location dict
            nearby_stations: List of nearby MTA stations
        
        Returns:
            Dict with current foot traffic and MTA data
        """
        print("\n📡 Gathering dynamic data...")
        
        current_traffic = self.get_current_foot_traffic(business_location)
        mta_data = self.get_mta_traffic(nearby_stations)
        
        return {
            "current_foot_traffic": current_traffic,
            "mta_data": mta_data,
            "timestamp": datetime.now()
        }