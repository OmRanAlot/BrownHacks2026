"""
Predictor Agent - Forecasts foot traffic using city signals
Analyzes weather, events, maps data, and historical patterns.
"""

from typing import Optional
from datetime import datetime, timedelta
import random


class PredictorAgent:
    """
    The Predictor Agent forecasts foot traffic by analyzing
    multiple city signals and generating confidence scores.
    """
    
    def __init__(self):
        self.name = "Predictor"
        self.status = "processing"
        self.predictions_count = 0
        self.signal_weights = {
            "weather": 0.25,
            "events": 0.35,
            "maps_activity": 0.25,
            "historical": 0.15,
        }
        self.anomalies = []
    
    def get_status(self) -> dict:
        """Return agent status."""
        return {
            "name": self.name,
            "status": self.status,
            "predictions_count": self.predictions_count,
            "signal_weights": self.signal_weights,
            "anomalies_detected": len(self.anomalies),
        }
    
    def get_anomalies(self) -> list:
        """Return detected anomalies."""
        return [
            {
                "id": "anom-001",
                "type": "Surge Detected",
                "detail": "Evening traffic 40% above normal",
                "severity": "high",
                "timestamp": datetime.now().isoformat(),
            },
            {
                "id": "anom-002",
                "type": "Pattern Break",
                "detail": "Thursday behaving like weekend",
                "severity": "medium",
                "timestamp": datetime.now().isoformat(),
            },
        ]
    
    async def gather_signals(self, location_id: str) -> dict:
        """
        Gather city signals from various sources.
        In production, this would call real APIs.
        """
        # Mock signal data
        signals = {
            "weather": {
                "condition": "clear",
                "temperature": 72,
                "humidity": 45,
                "rain_probability": 0,
                "source": "weather_api",
            },
            "events": [
                {
                    "name": "Live Concert",
                    "venue": "Brooklyn Bowl",
                    "distance_miles": 0.4,
                    "start_time": "19:00",
                    "expected_attendance": 3000,
                    "source": "events_api",
                }
            ],
            "maps_activity": {
                "current_popularity": 1.23,
                "average_popularity": 1.0,
                "trend": "increasing",
                "nearby_density": "high",
                "source": "maps_api",
            },
            "historical": {
                "day_of_week": datetime.now().strftime("%A"),
                "typical_pattern": "weekday",
                "last_week_same_day": 85,
                "last_month_average": 78,
            },
            "disruptions": [],
        }
        
        return signals
    
    async def predict(
        self,
        location_id: str,
        date: str,
        signals: dict,
    ) -> dict:
        """
        Generate foot traffic prediction based on signals.
        Uses weighted scoring to combine multiple signals.
        """
        self.predictions_count += 1
        
        # Calculate base score from signals
        weather_score = self._score_weather(signals.get("weather", {}))
        events_score = self._score_events(signals.get("events", []))
        maps_score = self._score_maps(signals.get("maps_activity", {}))
        historical_score = self._score_historical(signals.get("historical", {}))
        
        # Weighted combination
        total_score = (
            weather_score * self.signal_weights["weather"]
            + events_score * self.signal_weights["events"]
            + maps_score * self.signal_weights["maps_activity"]
            + historical_score * self.signal_weights["historical"]
        )
        
        # Normalize to traffic index (0-100 scale)
        traffic_index = min(100, int(total_score))
        
        # Calculate confidence based on signal quality
        confidence = self._calculate_confidence(signals)
        
        # Determine demand level
        demand_level = self._get_demand_level(traffic_index)
        
        # Calculate change from baseline
        baseline = signals.get("historical", {}).get("last_month_average", 70)
        change_percent = int(((traffic_index - baseline) / baseline) * 100)
        
        # Determine primary driver
        primary_driver = self._get_primary_driver(
            weather_score, events_score, maps_score, historical_score
        )
        
        # Generate hourly forecasts
        hourly_forecasts = self._generate_hourly_forecasts(traffic_index, signals)
        
        prediction = {
            "id": f"pred-{self.predictions_count}",
            "location_id": location_id,
            "date": date,
            "traffic_index": traffic_index,
            "confidence": confidence,
            "demand_level": demand_level,
            "traffic_change": f"+{change_percent}%" if change_percent > 0 else f"{change_percent}%",
            "primary_driver": primary_driver,
            "hourly_forecasts": hourly_forecasts,
            "signals_used": list(signals.keys()),
            "timestamp": datetime.now().isoformat(),
        }
        
        # Check for anomalies
        self._detect_anomalies(prediction, signals)
        
        return prediction
    
    async def get_hourly_forecast(self, location_id: str, hours: int = 24) -> list:
        """Generate hourly forecast for the next N hours."""
        forecasts = []
        base_hour = datetime.now().hour
        
        for i in range(hours):
            hour = (base_hour + i) % 24
            
            # Simulate daily pattern
            if 6 <= hour <= 9:  # Morning rush
                base = 60 + random.randint(-5, 10)
            elif 11 <= hour <= 14:  # Lunch
                base = 75 + random.randint(-5, 15)
            elif 16 <= hour <= 20:  # Evening/dinner
                base = 85 + random.randint(-5, 20)
            elif 21 <= hour or hour <= 5:  # Night
                base = 30 + random.randint(-10, 10)
            else:
                base = 50 + random.randint(-10, 10)
            
            forecasts.append({
                "hour": f"{hour}:00",
                "traffic_index": base,
                "confidence": round(0.7 + random.random() * 0.2, 2),
                "confidence_low": base - random.randint(5, 15),
                "confidence_high": base + random.randint(5, 15),
            })
        
        return forecasts
    
    def _score_weather(self, weather: dict) -> float:
        """Score weather conditions (higher = better for foot traffic)."""
        base_score = 70
        
        condition = weather.get("condition", "").lower()
        if condition in ["clear", "sunny"]:
            base_score += 20
        elif condition in ["cloudy", "overcast"]:
            base_score += 5
        elif condition in ["rain", "storm"]:
            base_score -= 30
        
        rain_prob = weather.get("rain_probability", 0)
        base_score -= rain_prob * 0.3
        
        return max(0, min(100, base_score))
    
    def _score_events(self, events: list) -> float:
        """Score nearby events impact."""
        if not events:
            return 50  # Neutral
        
        score = 50
        for event in events:
            distance = event.get("distance_miles", 10)
            attendance = event.get("expected_attendance", 0)
            
            # Closer and larger events have more impact
            impact = (attendance / 1000) * (1 / max(0.1, distance))
            score += min(50, impact * 10)
        
        return min(100, score)
    
    def _score_maps(self, maps_data: dict) -> float:
        """Score maps activity data."""
        popularity = maps_data.get("current_popularity", 1.0)
        return min(100, popularity * 80)
    
    def _score_historical(self, historical: dict) -> float:
        """Score based on historical patterns."""
        last_week = historical.get("last_week_same_day", 70)
        last_month = historical.get("last_month_average", 70)
        return (last_week + last_month) / 2
    
    def _calculate_confidence(self, signals: dict) -> float:
        """Calculate prediction confidence based on signal quality."""
        # More signals = higher confidence
        signal_count = len([s for s in signals.values() if s])
        base_confidence = 0.5 + (signal_count * 0.1)
        
        # Add some randomness for realism
        confidence = base_confidence + random.uniform(-0.05, 0.1)
        
        return round(min(0.95, max(0.5, confidence)), 2)
    
    def _get_demand_level(self, traffic_index: int) -> str:
        """Categorize demand level."""
        if traffic_index >= 80:
            return "High"
        elif traffic_index >= 60:
            return "Medium"
        else:
            return "Low"
    
    def _get_primary_driver(
        self,
        weather: float,
        events: float,
        maps: float,
        historical: float,
    ) -> str:
        """Determine the primary driver of the prediction."""
        scores = {
            "Weather conditions": weather,
            "Local events": events,
            "Area activity": maps,
            "Historical patterns": historical,
        }
        return max(scores, key=scores.get)
    
    def _generate_hourly_forecasts(self, base_index: int, signals: dict) -> list:
        """Generate detailed hourly forecasts."""
        forecasts = []
        
        # Check if there's an event
        events = signals.get("events", [])
        event_hour = None
        if events:
            event_time = events[0].get("start_time", "")
            if event_time:
                event_hour = int(event_time.split(":")[0])
        
        for hour in range(6, 23):  # 6am to 10pm
            # Base pattern
            if 7 <= hour <= 9:  # Morning
                modifier = 0.8
            elif 11 <= hour <= 14:  # Lunch
                modifier = 1.1
            elif 16 <= hour <= 20:  # Evening
                modifier = 1.2
            else:
                modifier = 0.7
            
            # Event boost
            if event_hour and abs(hour - event_hour) <= 2:
                modifier += 0.4
            
            traffic = int(base_index * modifier)
            confidence = round(0.75 + random.random() * 0.15, 2)
            
            forecasts.append({
                "hour": f"{hour}:00",
                "predicted": traffic,
                "baseline": int(base_index * 0.85),
                "low": traffic - random.randint(5, 12),
                "high": traffic + random.randint(5, 12),
                "confidence": confidence,
            })
        
        return forecasts
    
    def _detect_anomalies(self, prediction: dict, signals: dict) -> None:
        """Detect anomalies in prediction or signals."""
        traffic = prediction.get("traffic_index", 0)
        baseline = 70  # Assumed baseline
        
        # Check for significant deviation
        if abs(traffic - baseline) > 30:
            self.anomalies.append({
                "id": f"anom-{len(self.anomalies) + 1}",
                "type": "Significant Deviation",
                "detail": f"Traffic index {traffic} deviates {abs(traffic - baseline)} from baseline",
                "severity": "high" if abs(traffic - baseline) > 40 else "medium",
                "timestamp": datetime.now().isoformat(),
            })
