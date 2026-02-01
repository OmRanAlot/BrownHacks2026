"""
Dynamic Data Agent
Handles real-time foot traffic and MTA subway data.

This agent focuses on "live" signals that change hour-to-hour.
It intentionally avoids long-term datasets (events, weather history, etc.),
which are handled by the StaticDataAgent.
"""

from datetime import datetime
from typing import Callable, Dict, List, Optional

try:
    # Preferred import path with backend as a package.
    from backend.services.mta import STATION_MAP, get_mta_pulse
except ImportError:
    # Fallback for script-style runs where backend isn't on sys.path.
    from services.mta import STATION_MAP, get_mta_pulse


class DynamicDataAgent:
    """Agent for real-time/dynamic data (local foot traffic + MTA)."""

    def __init__(
        self,
        google_api_key: Optional[str] = None,
        mta_api_key: Optional[str] = None,
        station_map: Optional[Dict[str, str]] = None,
        local_traffic_fetcher: Optional[Callable[[Dict], int]] = None,
    ):
        """
        Initialize dynamic data agent

        Args:
            google_api_key: Google API key for foot traffic data
            mta_api_key: MTA API key for subway data
            station_map: Optional GTFS stop_id -> station_name mapping override
            local_traffic_fetcher: Optional function that returns current foot traffic
                for a given business location (used to plug in your real API)
        """
        self.google_api_key = google_api_key
        self.mta_api_key = mta_api_key
        self.station_map = station_map or STATION_MAP
        self.local_traffic_fetcher = local_traffic_fetcher or self._estimate_local_traffic

    def get_current_foot_traffic(self, location: Dict) -> int:
        """
        Get real-time foot traffic from your local traffic API.

        This method delegates to `self.local_traffic_fetcher` so that we can
        swap in a real provider later without changing the agent's interface.

        Args:
            location: {"lat": float, "lng": float, "borough": str}

        Returns:
            Current foot traffic count (people per hour)
        """
        print(f"   📡 Fetching current foot traffic for {location['borough']}...")

        try:
            current_traffic = int(self.local_traffic_fetcher(location))
        except Exception as e:
            # Fail closed (safe default) if a live API errors out.
            print(f"      ⚠️  Local traffic provider failed: {e}")
            current_traffic = 0

        print(f"      Current traffic: {current_traffic} people/hour")
        return current_traffic

    def get_mta_traffic(self, nearby_stations: List[str]) -> Dict:
        """
        Get real-time MTA subway traffic data.

        We call the GTFS-RT feed via the services layer and return both a
        structured summary and the LLM-friendly pulse messages.

        Args:
            nearby_stations: List of nearby station names

        Returns:
            Dict with MTA traffic metrics
        """
        print(f"   🚇 Fetching MTA data for {len(nearby_stations)} stations...")

        active_station_map = self._build_station_map(nearby_stations)

        # Use the service-layer API to fetch structured train pulses.
        mta_context = get_mta_pulse(
            api_key=self.mta_api_key,
            station_map=active_station_map,
        )

        # Translate pulses into a lightweight "traffic estimate".
        # This keeps the output backward-compatible with the existing
        # `total_entries` / `total_exits` structure used elsewhere.
        intensity_weights = {"HIGH": 250, "MODERATE": 120}
        estimated_entries = sum(
            intensity_weights.get(p["intensity"], 80) for p in mta_context["pulses"]
        )
        estimated_exits = int(estimated_entries * 0.9)

        mta_data = {
            "total_entries": estimated_entries,
            "total_exits": estimated_exits,
            "pulse_reports": mta_context["pulse_reports"],
            "pulses": mta_context["pulses"],
            "summary": mta_context["summary"],
            "timestamp": datetime.now(),
        }

        print(f"      Total MTA entries (est.): {mta_data['total_entries']}")
        return mta_data

    def _build_station_map(self, nearby_stations: List[str]) -> Dict[str, str]:
        """
        Build a GTFS stop_id -> station_name map filtered to the business area.

        The MTA feed uses stop IDs (e.g., "125"), while business configs often
        store readable names. This helper aligns those two worlds.
        """
        if not nearby_stations:
            return self.station_map

        # Normalize for fuzzy matching (case-insensitive).
        normalized = {s.strip().lower() for s in nearby_stations}
        return {
            stop_id: name
            for stop_id, name in self.station_map.items()
            if name.lower() in normalized
        }

    def _estimate_local_traffic(self, location: Dict) -> int:
        """
        Fallback "local traffic" estimator.

        This is a deterministic placeholder so you get stable outputs while
        wiring your real traffic API. Swap it out via `local_traffic_fetcher`.
        """
        current_hour = datetime.now().hour
        day_of_week = datetime.now().weekday()  # 0=Mon, 6=Sun

        # Time-of-day baseline (heuristic for NYC foot traffic).
        if 7 <= current_hour <= 9:  # Morning rush
            base_traffic = 600
        elif 11 <= current_hour <= 14:  # Lunch
            base_traffic = 700
        elif 17 <= current_hour <= 20:  # Dinner/evening
            base_traffic = 800
        else:  # Off-peak
            base_traffic = 300

        # Weekends typically see higher leisure traffic in Manhattan.
        weekend_multiplier = 1.15 if day_of_week >= 5 else 1.0

        # Borough multiplier for rough calibration (expand as you learn data).
        borough = (location.get("borough") or "").lower()
        borough_multiplier = {
            "manhattan": 1.2,
            "brooklyn": 1.05,
            "queens": 0.95,
            "bronx": 0.85,
            "staten island": 0.7,
        }.get(borough, 1.0)

        return int(base_traffic * weekend_multiplier * borough_multiplier)

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