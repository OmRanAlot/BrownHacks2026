"""
HypeLensMasterAgent - Orchestrator for Multi-Agent Foot Traffic Prediction
===========================================================================
The "brain" of the HypeLens Metropolis. This agent:
1. Receives user requests (HypeLensRequest)
2. Fans out sub-requests to Weather, MTA, and Traffic agents
3. Collects and fuses their responses
4. Returns a unified HypeLensResponse with the final "Hype Score"

Uses Fetch.ai uAgents for distributed communication via Agentverse.
"""

import os
import sys
import uuid
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List

from uagents import Agent, Context
from uagents.setup import fund_agent_if_low

# Add parent paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

# Import all message schemas
from schema import (
    HypeLensRequest, HypeLensResponse, SignalData,
    WeatherRequest, WeatherResponse,
    MTARequest, MTAResponse,
    TrafficRequest, TrafficResponse,
)


# =============================================================================
# AGENT CONFIGURATION
# =============================================================================

MASTER_AGENT_SEED = os.getenv("MASTER_AGENT_SEED", "hypelens-master-agent-seed-v1")
MASTER_AGENT_MAILBOX_KEY = os.getenv("MASTER_AGENT_MAILBOX_KEY", None)

# Sub-agent addresses (set these in .env after discovering their addresses)
# These can be discovered from the agent logs on startup
WEATHER_AGENT_ADDRESS = os.getenv("WEATHER_AGENT_ADDRESS", None)
MTA_AGENT_ADDRESS = os.getenv("MTA_AGENT_ADDRESS", None)
TRAFFIC_AGENT_ADDRESS = os.getenv("TRAFFIC_AGENT_ADDRESS", None)

master_agent = Agent(
    name="HypeLensMasterAgent",
    seed=MASTER_AGENT_SEED,
    port=8000,
    endpoint=["http://127.0.0.1:8000/submit"],
    mailbox=f"{MASTER_AGENT_MAILBOX_KEY}@https://agentverse.ai" if MASTER_AGENT_MAILBOX_KEY else None,
    network="testnet",  # Register on testnet Almanac
)

fund_agent_if_low(master_agent.wallet.address())


# =============================================================================
# STATE MANAGEMENT
# =============================================================================

class PendingRequest:
    """Tracks state for a single orchestration request."""
    def __init__(self, original_sender: str, request: HypeLensRequest):
        self.original_sender = original_sender
        self.request = request
        self.started_at = datetime.now()
        
        # Response collection
        self.weather_response: Optional[WeatherResponse] = None
        self.mta_response: Optional[MTAResponse] = None
        self.traffic_response: Optional[TrafficResponse] = None
        
        # Timeout tracking
        self.timeout_seconds = 60
    
    def is_complete(self) -> bool:
        """Check if all sub-agent responses have been received."""
        return all([
            self.weather_response is not None,
            self.mta_response is not None,
            self.traffic_response is not None,
        ])
    
    def is_timed_out(self) -> bool:
        """Check if request has timed out."""
        elapsed = (datetime.now() - self.started_at).total_seconds()
        return elapsed > self.timeout_seconds
    
    def received_count(self) -> int:
        """Count how many responses have been received."""
        count = 0
        if self.weather_response: count += 1
        if self.mta_response: count += 1
        if self.traffic_response: count += 1
        return count


# Global state for tracking pending requests
# Key: request_id -> PendingRequest
_pending_requests: Dict[str, PendingRequest] = {}


# =============================================================================
# SIGNAL FUSION LOGIC (from original master_agent.py)
# =============================================================================

def normalize_weather_signal(resp: WeatherResponse) -> Dict[str, Any]:
    """Convert WeatherResponse to normalized signal format."""
    return {
        "source": "weather_event",
        "extra_customers_per_hour": resp.predicted_traffic if resp.success else 0.0,
        "confidence": resp.confidence if resp.success else 0.05,
        "explanation": resp.reasoning if resp.success else f"Agent error: {resp.error or 'Unknown'}",
    }


def normalize_mta_signal(resp: MTAResponse) -> Dict[str, Any]:
    """Convert MTAResponse to normalized signal format."""
    return {
        "source": "mta_subway",
        "extra_customers_per_hour": resp.expected_extra_customers_hourly if resp.success else 0.0,
        "confidence": resp.confidence if resp.success else 0.05,
        "explanation": "; ".join(resp.main_drivers) if resp.success else f"Agent error: {resp.error or 'Unknown'}",
    }


def normalize_traffic_signal(resp: TrafficResponse) -> Dict[str, Any]:
    """Convert TrafficResponse to normalized signal format."""
    return {
        "source": "google_traffic",
        "extra_customers_per_hour": resp.expected_extra_customers_per_hour if resp.success else 0.0,
        "confidence": resp.confidence if resp.success else 0.05,
        "explanation": "; ".join(resp.rationale_bullets) if resp.success else f"Agent error: {resp.error or 'Unknown'}",
    }


def combine_signals(signals: List[Dict[str, Any]], baseline: float) -> Dict[str, Any]:
    """
    Weighted average fusion using confidence as weight.
    Mirrors the logic from the original MasterFootTrafficAgent.
    """
    weighted_sum = 0.0
    weight_total = 0.0
    
    for s in signals:
        w = max(0.05, s["confidence"])
        weighted_sum += s["extra_customers_per_hour"] * w
        weight_total += w
    
    extra_customers = weighted_sum / weight_total if weight_total > 0 else 0.0
    
    # Guardrails (single cafe)
    extra_customers = max(-0.5 * baseline, min(extra_customers, 1.5 * baseline))
    
    # Generate summary based on delta
    pct = (extra_customers / baseline) * 100 if baseline else 0
    if pct >= 50:
        summary = "Much higher than usual"
    elif pct >= 15:
        summary = "Above baseline today"
    elif pct >= -15:
        summary = "On par with usual"
    elif pct >= -40:
        summary = "Below baseline today"
    else:
        summary = "Much lower than usual"
    
    return {
        "expected_extra_customers_per_hour": round(extra_customers, 1),
        "expected_total_customers_per_hour": round(baseline + extra_customers, 1),
        "overall_confidence": round(min(1.0, weight_total / len(signals)) if signals else 0.5, 2),
        "summary": summary,
    }


# =============================================================================
# EVENT HANDLERS
# =============================================================================

@master_agent.on_event("startup")
async def startup_handler(ctx: Context):
    """Log agent startup with address for discovery."""
    ctx.logger.info("=" * 60)
    ctx.logger.info(f"🏙️  HypeLensMasterAgent starting up...")
    ctx.logger.info(f"📍 Agent Address: {master_agent.address}")
    ctx.logger.info(f"💰 Wallet Address: {master_agent.wallet.address()}")
    ctx.logger.info("=" * 60)
    ctx.logger.info("Sub-agent addresses configured:")
    ctx.logger.info(f"   🌤️  Weather: {WEATHER_AGENT_ADDRESS or 'NOT SET'}")
    ctx.logger.info(f"   🚇 MTA:     {MTA_AGENT_ADDRESS or 'NOT SET'}")
    ctx.logger.info(f"   🚗 Traffic: {TRAFFIC_AGENT_ADDRESS or 'NOT SET'}")
    ctx.logger.info("=" * 60)
    ctx.logger.info("Listening for HypeLensRequest messages...")


@master_agent.on_message(model=HypeLensRequest)
async def handle_hypelens_request(ctx: Context, sender: str, msg: HypeLensRequest):
    """
    Handle incoming user request by fanning out to sub-agents.
    """
    ctx.logger.info("=" * 60)
    ctx.logger.info(f"📥 NEW HYPELENS REQUEST")
    ctx.logger.info(f"   From: {sender}")
    ctx.logger.info(f"   Request ID: {msg.request_id}")
    ctx.logger.info(f"   Business: {msg.business_name}")
    ctx.logger.info(f"   Baseline: {msg.baseline_customers_per_hour} customers/hr")
    ctx.logger.info(f"   Date/Time: {msg.date or 'today'} @ {msg.time or 'now'}")
    ctx.logger.info("=" * 60)
    
    # Check if sub-agent addresses are configured
    missing_agents = []
    if not WEATHER_AGENT_ADDRESS:
        missing_agents.append("WEATHER_AGENT_ADDRESS")
    if not MTA_AGENT_ADDRESS:
        missing_agents.append("MTA_AGENT_ADDRESS")
    if not TRAFFIC_AGENT_ADDRESS:
        missing_agents.append("TRAFFIC_AGENT_ADDRESS")
    
    if missing_agents:
        ctx.logger.error(f"❌ Missing sub-agent addresses: {missing_agents}")
        ctx.logger.error("   Set these in your .env file after discovering agent addresses")
        
        # Send error response
        error_response = HypeLensResponse(
            request_id=msg.request_id,
            success=False,
            business_name=msg.business_name,
            baseline_customers_per_hour=msg.baseline_customers_per_hour,
            error=f"Orchestrator not configured. Missing: {', '.join(missing_agents)}",
        )
        await ctx.send(sender, error_response)
        return
    
    # Create pending request tracker
    pending = PendingRequest(original_sender=sender, request=msg)
    _pending_requests[msg.request_id] = pending
    
    # Fan out to sub-agents
    ctx.logger.info("🔄 ORCHESTRATING SUB-AGENTS...")
    
    # 1. Weather Agent
    ctx.logger.info(f"   → Sending WeatherRequest to {WEATHER_AGENT_ADDRESS}")
    weather_req = WeatherRequest(
        request_id=msg.request_id,
        date=msg.date,
        time=msg.time,
        latitude=msg.latitude,
        longitude=msg.longitude,
    )
    await ctx.send(WEATHER_AGENT_ADDRESS, weather_req)
    
    # 2. MTA Agent
    ctx.logger.info(f"   → Sending MTARequest to {MTA_AGENT_ADDRESS}")
    mta_req = MTARequest(request_id=msg.request_id)
    await ctx.send(MTA_AGENT_ADDRESS, mta_req)
    
    # 3. Traffic Agent
    ctx.logger.info(f"   → Sending TrafficRequest to {TRAFFIC_AGENT_ADDRESS}")
    traffic_req = TrafficRequest(
        request_id=msg.request_id,
        baseline_customers_per_hour=msg.baseline_customers_per_hour,
    )
    await ctx.send(TRAFFIC_AGENT_ADDRESS, traffic_req)
    
    ctx.logger.info("✅ All sub-requests dispatched. Waiting for responses...")


# =============================================================================
# SUB-AGENT RESPONSE HANDLERS
# =============================================================================

@master_agent.on_message(model=WeatherResponse)
async def handle_weather_response(ctx: Context, sender: str, msg: WeatherResponse):
    """Handle response from WeatherAgent."""
    ctx.logger.info(f"📥 Received WeatherResponse for request {msg.request_id}")
    
    pending = _pending_requests.get(msg.request_id)
    if not pending:
        ctx.logger.warning(f"   ⚠️ No pending request found for {msg.request_id}")
        return
    
    pending.weather_response = msg
    ctx.logger.info(f"   🌤️  Weather signal: {msg.predicted_traffic:+.1f} (conf: {msg.confidence:.0%})")
    ctx.logger.info(f"   📊 Progress: {pending.received_count()}/3 responses")
    
    await _check_and_finalize(ctx, msg.request_id)


@master_agent.on_message(model=MTAResponse)
async def handle_mta_response(ctx: Context, sender: str, msg: MTAResponse):
    """Handle response from MTAAgent."""
    ctx.logger.info(f"📥 Received MTAResponse for request {msg.request_id}")
    
    pending = _pending_requests.get(msg.request_id)
    if not pending:
        ctx.logger.warning(f"   ⚠️ No pending request found for {msg.request_id}")
        return
    
    pending.mta_response = msg
    ctx.logger.info(f"   🚇 MTA signal: {msg.expected_extra_customers_hourly:+.1f}/hr (conf: {msg.confidence:.0%})")
    ctx.logger.info(f"   📊 Progress: {pending.received_count()}/3 responses")
    
    await _check_and_finalize(ctx, msg.request_id)


@master_agent.on_message(model=TrafficResponse)
async def handle_traffic_response(ctx: Context, sender: str, msg: TrafficResponse):
    """Handle response from TrafficAgent."""
    ctx.logger.info(f"📥 Received TrafficResponse for request {msg.request_id}")
    
    pending = _pending_requests.get(msg.request_id)
    if not pending:
        ctx.logger.warning(f"   ⚠️ No pending request found for {msg.request_id}")
        return
    
    pending.traffic_response = msg
    ctx.logger.info(f"   🚗 Traffic signal: {msg.expected_extra_customers_per_hour:+.1f}/hr (conf: {msg.confidence:.0%})")
    ctx.logger.info(f"   📊 Progress: {pending.received_count()}/3 responses")
    
    await _check_and_finalize(ctx, msg.request_id)


async def _check_and_finalize(ctx: Context, request_id: str):
    """
    Check if all responses received, then fuse and send final response.
    """
    pending = _pending_requests.get(request_id)
    if not pending:
        return
    
    if not pending.is_complete():
        return
    
    ctx.logger.info("=" * 60)
    ctx.logger.info("✅ ALL SUB-AGENT RESPONSES RECEIVED")
    ctx.logger.info("🔄 FUSING SIGNALS...")
    
    # Normalize all signals
    signals = [
        normalize_weather_signal(pending.weather_response),
        normalize_mta_signal(pending.mta_response),
        normalize_traffic_signal(pending.traffic_response),
    ]
    
    # Log individual signals
    for s in signals:
        ctx.logger.info(f"   {s['source']}: {s['extra_customers_per_hour']:+.1f} (conf: {s['confidence']:.0%})")
    
    # Combine signals
    baseline = pending.request.baseline_customers_per_hour
    combined = combine_signals(signals, baseline)
    
    ctx.logger.info("=" * 60)
    ctx.logger.info("📊 FINAL PREDICTION:")
    ctx.logger.info(f"   Baseline: {baseline} customers/hr")
    ctx.logger.info(f"   Extra: {combined['expected_extra_customers_per_hour']:+.1f} customers/hr")
    ctx.logger.info(f"   Total: {combined['expected_total_customers_per_hour']} customers/hr")
    ctx.logger.info(f"   Confidence: {combined['overall_confidence']:.0%}")
    ctx.logger.info(f"   Summary: {combined['summary']}")
    ctx.logger.info("=" * 60)
    
    # Build and send final response
    final_response = HypeLensResponse(
        request_id=request_id,
        success=True,
        business_name=pending.request.business_name,
        baseline_customers_per_hour=baseline,
        signals=[s for s in signals],  # Include raw signals
        expected_extra_customers_per_hour=combined["expected_extra_customers_per_hour"],
        expected_total_customers_per_hour=combined["expected_total_customers_per_hour"],
        overall_confidence=combined["overall_confidence"],
        summary=combined["summary"],
    )
    
    ctx.logger.info(f"📤 Sending HypeLensResponse to {pending.original_sender}")
    await ctx.send(pending.original_sender, final_response)
    
    # Clean up
    del _pending_requests[request_id]
    ctx.logger.info(f"🧹 Cleaned up request {request_id}")


# =============================================================================
# PERIODIC TIMEOUT CHECK
# =============================================================================

@master_agent.on_interval(period=30.0)
async def timeout_check(ctx: Context):
    """Check for timed-out requests and send error responses."""
    timed_out = []
    
    for req_id, pending in _pending_requests.items():
        if pending.is_timed_out():
            timed_out.append(req_id)
    
    for req_id in timed_out:
        pending = _pending_requests.pop(req_id)
        ctx.logger.warning(f"⏰ Request {req_id} timed out after {pending.timeout_seconds}s")
        ctx.logger.warning(f"   Received {pending.received_count()}/3 responses")
        
        # Send partial response with available data
        signals = []
        if pending.weather_response:
            signals.append(normalize_weather_signal(pending.weather_response))
        if pending.mta_response:
            signals.append(normalize_mta_signal(pending.mta_response))
        if pending.traffic_response:
            signals.append(normalize_traffic_signal(pending.traffic_response))
        
        baseline = pending.request.baseline_customers_per_hour
        combined = combine_signals(signals, baseline) if signals else {
            "expected_extra_customers_per_hour": 0,
            "expected_total_customers_per_hour": baseline,
            "overall_confidence": 0.1,
            "summary": "Partial data - some agents timed out",
        }
        
        error_response = HypeLensResponse(
            request_id=req_id,
            success=False,
            business_name=pending.request.business_name,
            baseline_customers_per_hour=baseline,
            signals=signals,
            expected_extra_customers_per_hour=combined["expected_extra_customers_per_hour"],
            expected_total_customers_per_hour=combined["expected_total_customers_per_hour"],
            overall_confidence=combined["overall_confidence"],
            summary=combined["summary"],
            error=f"Request timed out. Only {pending.received_count()}/3 sub-agents responded.",
        )
        
        await ctx.send(pending.original_sender, error_response)


# =============================================================================
# STANDALONE EXECUTION
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🏙️  Starting HypeLensMasterAgent (standalone mode)")
    print("=" * 60)
    master_agent.run()
