"""
Message Schemas for HypeLens Multi-Agent System
================================================
All message models use uagents.Model (Pydantic-based) for type-safe
inter-agent communication.
"""

from typing import Optional, List, Dict, Any
from uagents import Model


# =============================================================================
# CHAT PROTOCOL MESSAGES (Required for Agentverse)
# =============================================================================

class ChatMessage(Model):
    """Incoming chat message from Agentverse users."""
    message: str
    sender: Optional[str] = None


class ChatResponse(Model):
    """Response to chat messages."""
    message: str
    success: bool = True


# =============================================================================
# WEATHER AGENT MESSAGES
# =============================================================================

class WeatherRequest(Model):
    """Request weather-based foot traffic prediction for a specific datetime."""
    request_id: str
    date: Optional[str] = None  # "YYYY-MM-DD" format, defaults to today
    time: Optional[int] = None  # Hour 0-23, defaults to current hour
    borough: str = "Manhattan"
    business_type: str = "cafe"
    latitude: float = 40.770530  # Default: NYC Midtown
    longitude: float = -73.982456


class WeatherResponse(Model):
    """Response from WeatherAgent with weather-based traffic prediction."""
    request_id: str
    success: bool
    predicted_traffic: float = 0.0
    confidence: float = 0.5
    reasoning: str = ""
    weather_condition: str = ""
    temperature_f: Optional[float] = None
    target_datetime: str = ""
    error: Optional[str] = None


# =============================================================================
# MTA AGENT MESSAGES
# =============================================================================

class MTARequest(Model):
    """Request MTA subway impact analysis on foot traffic."""
    request_id: str


class MTAResponse(Model):
    """Response from MTAAgent with subway crowding impact."""
    request_id: str
    success: bool
    expected_extra_customers_30min: int = 0
    expected_extra_customers_hourly: float = 0.0  # 30min * 2
    confidence: float = 0.5
    main_drivers: List[str] = []
    notes: Optional[str] = None
    error: Optional[str] = None


# =============================================================================
# TRAFFIC AGENT MESSAGES (Google Maps Road Congestion)
# =============================================================================

class TrafficRequest(Model):
    """Request Google Traffic congestion impact analysis."""
    request_id: str
    baseline_customers_per_hour: float
    dataset_path: Optional[str] = None  # Optional custom path


class TrafficResponse(Model):
    """Response from TrafficAgent with road congestion impact."""
    request_id: str
    success: bool
    expected_extra_customers_per_hour: float = 0.0
    confidence: float = 0.5
    rationale_bullets: List[str] = []
    cautions: List[str] = []
    dominant_direction: str = "unknown"  # towards_cafe, away_from_cafe, balanced
    error: Optional[str] = None


# =============================================================================
# MASTER AGENT MESSAGES
# =============================================================================

class HypeLensRequest(Model):
    """
    User request to HypeLensMasterAgent for a complete foot traffic prediction.
    This triggers orchestration of all sub-agents.
    """
    request_id: str
    business_name: str = "HypeLens Cafe"
    baseline_customers_per_hour: float = 42.0
    date: Optional[str] = None  # "YYYY-MM-DD"
    time: Optional[int] = None  # Hour 0-23
    latitude: float = 40.770530
    longitude: float = -73.982456


class SignalData(Model):
    """Normalized signal from a sub-agent."""
    source: str  # "weather_event", "google_traffic", "mta_subway"
    extra_customers_per_hour: float
    confidence: float
    explanation: str


class HypeLensResponse(Model):
    """
    Complete foot traffic prediction from HypeLensMasterAgent.
    Fuses all sub-agent signals into a final "Hype Score".
    """
    request_id: str
    success: bool
    business_name: str
    baseline_customers_per_hour: float
    signals: List[Dict[str, Any]] = []  # Raw signal data from each agent
    
    # Final fused prediction
    expected_extra_customers_per_hour: float = 0.0
    expected_total_customers_per_hour: float = 0.0
    overall_confidence: float = 0.5
    summary: str = ""  # e.g., "Above baseline today"
    
    error: Optional[str] = None


# =============================================================================
# INTERNAL ORCHESTRATION MESSAGES
# =============================================================================

class AgentReadySignal(Model):
    """Signal that an agent is ready and registered."""
    agent_name: str
    agent_address: str


class OrchestratorPing(Model):
    """Ping to check if orchestrator is alive."""
    timestamp: str
