"""
TrafficAgent - uAgents Wrapper for Google Maps Road Congestion Analysis
========================================================================
Wraps the existing nearbycongestion.py logic (Google Traffic API analysis)
into a Fetch.ai uAgent that communicates via messages.

Listens for: TrafficRequest
Returns: TrafficResponse
"""

import os
import sys

from uagents import Agent, Context
from uagents.setup import fund_agent_if_low

# Add parent paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

# Import message schemas
from schema import TrafficRequest, TrafficResponse

# Import existing logic
from agents.nearbycongestion import forecast_extra_customers

# Default dataset path
PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
DEFAULT_DATASET_PATH = os.path.join(PROJECT_ROOT, "detailed_cafe_congestion.json")


# =============================================================================
# AGENT CONFIGURATION
# =============================================================================

TRAFFIC_AGENT_SEED = os.getenv("TRAFFIC_AGENT_SEED", "hypelens-traffic-agent-seed-v1")
TRAFFIC_AGENT_MAILBOX_KEY = os.getenv("TRAFFIC_AGENT_MAILBOX_KEY", None)

traffic_agent = Agent(
    name="TrafficAgent",
    seed=TRAFFIC_AGENT_SEED,
    port=8003,
    endpoint=["http://127.0.0.1:8003/submit"],
    mailbox=f"{TRAFFIC_AGENT_MAILBOX_KEY}@https://agentverse.ai" if TRAFFIC_AGENT_MAILBOX_KEY else None,
    network="testnet",  # Register on testnet Almanac
)

fund_agent_if_low(traffic_agent.wallet.address())


# =============================================================================
# EVENT HANDLERS
# =============================================================================

@traffic_agent.on_event("startup")
async def startup_handler(ctx: Context):
    """Log agent startup with address for discovery."""
    ctx.logger.info("=" * 60)
    ctx.logger.info(f"🚗 TrafficAgent starting up...")
    ctx.logger.info(f"📍 Agent Address: {traffic_agent.address}")
    ctx.logger.info(f"💰 Wallet Address: {traffic_agent.wallet.address()}")
    ctx.logger.info("=" * 60)
    ctx.logger.info("Listening for TrafficRequest messages...")


@traffic_agent.on_message(model=TrafficRequest)
async def handle_traffic_request(ctx: Context, sender: str, msg: TrafficRequest):
    """
    Handle incoming TrafficRequest by calling existing Google Traffic analysis.
    """
    ctx.logger.info(f"📥 Received TrafficRequest from {sender}")
    ctx.logger.info(f"   Request ID: {msg.request_id}")
    ctx.logger.info(f"   Baseline: {msg.baseline_customers_per_hour} customers/hr")
    
    try:
        # Determine dataset path
        dataset_path = msg.dataset_path or DEFAULT_DATASET_PATH
        
        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"Dataset not found: {dataset_path}")
        
        # Call existing Google Traffic analysis
        ctx.logger.info("🔄 Calling forecast_extra_customers()...")
        ctx.logger.info(f"   Dataset: {os.path.basename(dataset_path)}")
        
        result = forecast_extra_customers(
            dataset_path=dataset_path,
            baseline_customers_per_hour=msg.baseline_customers_per_hour,
        )
        
        extra = result.get("expected_extra_customers_per_hour", 0)
        conf = result.get("confidence_0_to_1", 0.5)
        direction = result.get("features_used", {}).get("dominant_direction", "unknown")
        
        ctx.logger.info(f"✅ Traffic analysis complete:")
        ctx.logger.info(f"   Extra customers/hr: {extra:+.1f}")
        ctx.logger.info(f"   Confidence: {conf:.0%}")
        ctx.logger.info(f"   Direction: {direction}")
        
        # Build response
        response = TrafficResponse(
            request_id=msg.request_id,
            success=True,
            expected_extra_customers_per_hour=float(extra),
            confidence=float(conf),
            rationale_bullets=result.get("rationale_bullets", []),
            cautions=result.get("cautions", []),
            dominant_direction=direction,
        )
        
    except FileNotFoundError as e:
        ctx.logger.error(f"❌ Dataset not found: {str(e)}")
        response = TrafficResponse(
            request_id=msg.request_id,
            success=False,
            error=f"Dataset not found: {str(e)[:200]}",
        )
    except Exception as e:
        ctx.logger.error(f"❌ Error in traffic analysis: {str(e)}")
        response = TrafficResponse(
            request_id=msg.request_id,
            success=False,
            error=str(e)[:500],
        )
    
    # Send response back to sender
    ctx.logger.info(f"📤 Sending TrafficResponse to {sender}")
    await ctx.send(sender, response)


# =============================================================================
# STANDALONE EXECUTION
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚗 Starting TrafficAgent (standalone mode)")
    print("=" * 60)
    traffic_agent.run()
