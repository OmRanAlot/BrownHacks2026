"""
MTAAgent - uAgents Wrapper for MTA Subway Crowding Analysis
============================================================
Wraps the existing mta.py logic (live vs baseline train busyness analysis)
into a Fetch.ai uAgent that communicates via messages.

Listens for: MTARequest
Returns: MTAResponse
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
from schema import MTARequest, MTAResponse

# Import existing logic
from agents.mta import run_mta_forecast


# =============================================================================
# AGENT CONFIGURATION
# =============================================================================

MTA_AGENT_SEED = os.getenv("MTA_AGENT_SEED", "hypelens-mta-agent-seed-v1")
MTA_AGENT_MAILBOX_KEY = os.getenv("MTA_AGENT_MAILBOX_KEY", None)

mta_agent = Agent(
    name="MTAAgent",
    seed=MTA_AGENT_SEED,
    port=8002,
    endpoint=["http://127.0.0.1:8002/submit"],
    mailbox=f"{MTA_AGENT_MAILBOX_KEY}@https://agentverse.ai" if MTA_AGENT_MAILBOX_KEY else None,
    network="testnet",  # Register on testnet Almanac
)

fund_agent_if_low(mta_agent.wallet.address())


# =============================================================================
# EVENT HANDLERS
# =============================================================================

@mta_agent.on_event("startup")
async def startup_handler(ctx: Context):
    """Log agent startup with address for discovery."""
    ctx.logger.info("=" * 60)
    ctx.logger.info(f"🚇 MTAAgent starting up...")
    ctx.logger.info(f"📍 Agent Address: {mta_agent.address}")
    ctx.logger.info(f"💰 Wallet Address: {mta_agent.wallet.address()}")
    ctx.logger.info("=" * 60)
    ctx.logger.info("Listening for MTARequest messages...")


@mta_agent.on_message(model=MTARequest)
async def handle_mta_request(ctx: Context, sender: str, msg: MTARequest):
    """
    Handle incoming MTARequest by calling existing MTA forecast logic.
    """
    ctx.logger.info(f"📥 Received MTARequest from {sender}")
    ctx.logger.info(f"   Request ID: {msg.request_id}")
    
    try:
        # Call existing MTA forecast logic
        ctx.logger.info("🔄 Calling run_mta_forecast()...")
        ctx.logger.info("   Analyzing live vs baseline subway busyness...")
        
        result = run_mta_forecast()
        
        extra_30min = result.get("expected_extra_customers_next_30_min", 0)
        extra_hourly = extra_30min * 2  # Convert to hourly rate
        
        ctx.logger.info(f"✅ MTA analysis complete:")
        ctx.logger.info(f"   Extra customers (30min): {extra_30min}")
        ctx.logger.info(f"   Extra customers (hourly): {extra_hourly}")
        ctx.logger.info(f"   Confidence: {result.get('confidence_0_to_1', 0.5):.0%}")
        
        # Build response
        response = MTAResponse(
            request_id=msg.request_id,
            success=True,
            expected_extra_customers_30min=int(extra_30min),
            expected_extra_customers_hourly=float(extra_hourly),
            confidence=float(result.get("confidence_0_to_1", 0.5)),
            main_drivers=result.get("main_drivers", []),
            notes=result.get("notes"),
        )
        
    except Exception as e:
        ctx.logger.error(f"❌ Error in MTA forecast: {str(e)}")
        response = MTAResponse(
            request_id=msg.request_id,
            success=False,
            error=str(e)[:500],
        )
    
    # Send response back to sender
    ctx.logger.info(f"📤 Sending MTAResponse to {sender}")
    await ctx.send(sender, response)


# =============================================================================
# STANDALONE EXECUTION
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚇 Starting MTAAgent (standalone mode)")
    print("=" * 60)
    mta_agent.run()
