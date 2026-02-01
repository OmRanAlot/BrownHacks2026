"""
WeatherAgent - uAgents Wrapper for Weather-Based Foot Traffic Prediction
=========================================================================
Wraps the existing predictor_agent.py logic (Pinecone RAG + Open-Meteo weather)
into a Fetch.ai uAgent that communicates via messages.

Listens for: WeatherRequest
Returns: WeatherResponse
"""

import os
import sys
from datetime import datetime

from uagents import Agent, Context
from uagents.setup import fund_agent_if_low

# Add parent paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

# Import message schemas
from schema import WeatherRequest, WeatherResponse

# Import existing logic
from agents.predictor_agent import predict_for_datetime


# =============================================================================
# AGENT CONFIGURATION
# =============================================================================

# Generate a seed for consistent agent address (or use env var for production)
WEATHER_AGENT_SEED = os.getenv("WEATHER_AGENT_SEED", "hypelens-weather-agent-seed-v1")

# Agentverse Mailbox configuration (set these in .env for production)
WEATHER_AGENT_MAILBOX_KEY = os.getenv("WEATHER_AGENT_MAILBOX_KEY", None)

weather_agent = Agent(
    name="WeatherAgent",
    seed=WEATHER_AGENT_SEED,
    port=8001,
    endpoint=["http://127.0.0.1:8001/submit"],
    mailbox=f"{WEATHER_AGENT_MAILBOX_KEY}@https://agentverse.ai" if WEATHER_AGENT_MAILBOX_KEY else None,
    network="testnet",  # Register on testnet Almanac
)

# Fund agent if on testnet (for Almanac registration)
fund_agent_if_low(weather_agent.wallet.address())


# =============================================================================
# EVENT HANDLERS
# =============================================================================

@weather_agent.on_event("startup")
async def startup_handler(ctx: Context):
    """Log agent startup with address for discovery."""
    ctx.logger.info("=" * 60)
    ctx.logger.info(f"🌤️  WeatherAgent starting up...")
    ctx.logger.info(f"📍 Agent Address: {weather_agent.address}")
    ctx.logger.info(f"💰 Wallet Address: {weather_agent.wallet.address()}")
    ctx.logger.info("=" * 60)
    ctx.logger.info("Listening for WeatherRequest messages...")


@weather_agent.on_message(model=WeatherRequest)
async def handle_weather_request(ctx: Context, sender: str, msg: WeatherRequest):
    """
    Handle incoming WeatherRequest by calling existing predictor_agent logic.
    """
    ctx.logger.info(f"📥 Received WeatherRequest from {sender}")
    ctx.logger.info(f"   Request ID: {msg.request_id}")
    ctx.logger.info(f"   Date: {msg.date or 'today'}, Time: {msg.time or 'now'}")
    ctx.logger.info(f"   Location: ({msg.latitude}, {msg.longitude})")
    
    try:
        # Call existing prediction logic
        ctx.logger.info("🔄 Calling predict_for_datetime()...")
        
        result = predict_for_datetime(
            date=msg.date,
            time=msg.time,
            borough=msg.borough,
            business_type=msg.business_type,
            lat=msg.latitude,
            lon=msg.longitude,
        )
        
        ctx.logger.info(f"✅ Prediction complete: {result.get('predicted_traffic', 0)} traffic score")
        
        # Build response
        response = WeatherResponse(
            request_id=msg.request_id,
            success=True,
            predicted_traffic=float(result.get("predicted_traffic", 0) or 0),
            confidence=float(result.get("confidence", 0.5) or 0.5),
            reasoning=str(result.get("reasoning", "")),
            weather_condition=_extract_weather_condition(result.get("query_text", "")),
            temperature_f=_extract_temperature(result.get("query_text", "")),
            target_datetime=result.get("target_datetime", datetime.now().isoformat()),
        )
        
    except Exception as e:
        ctx.logger.error(f"❌ Error in weather prediction: {str(e)}")
        response = WeatherResponse(
            request_id=msg.request_id,
            success=False,
            error=str(e)[:500],
        )
    
    # Send response back to sender
    ctx.logger.info(f"📤 Sending WeatherResponse to {sender}")
    await ctx.send(sender, response)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _extract_weather_condition(query_text: str) -> str:
    """Extract weather condition from query text."""
    # Query text format: "... Weather: {condition}, ..."
    if "Weather:" in query_text:
        try:
            start = query_text.index("Weather:") + len("Weather:")
            end = query_text.index(",", start)
            return query_text[start:end].strip()
        except (ValueError, IndexError):
            pass
    return "Unknown"


def _extract_temperature(query_text: str) -> float:
    """Extract temperature from query text."""
    # Query text format: "... Temperature: {temp}, ..."
    if "Temperature:" in query_text:
        try:
            start = query_text.index("Temperature:") + len("Temperature:")
            end = query_text.index(",", start)
            temp_str = query_text[start:end].strip()
            return float(temp_str)
        except (ValueError, IndexError):
            pass
    return None


# =============================================================================
# STANDALONE EXECUTION
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🌤️  Starting WeatherAgent (standalone mode)")
    print("=" * 60)
    weather_agent.run()
