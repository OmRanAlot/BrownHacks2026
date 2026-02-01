"""
HypeLens Test Client
====================
A simple test agent that sends a HypeLensRequest to the MasterAgent
and prints the response.

Usage:
    1. First, run the Bureau: python run.py
    2. In another terminal: python test_client.py
"""

import os
import sys
import uuid
from datetime import datetime

# Add parent paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

from uagents import Agent, Context
from uagents.setup import fund_agent_if_low

from schema import HypeLensRequest, HypeLensResponse


# =============================================================================
# TEST CLIENT CONFIGURATION
# =============================================================================

TEST_CLIENT_SEED = os.getenv("TEST_CLIENT_SEED", "hypelens-test-client-seed-v1")

# Target: the HypeLensMasterAgent address
MASTER_AGENT_ADDRESS = os.getenv("MASTER_AGENT_ADDRESS", None)

test_client = Agent(
    name="HypeLensTestClient",
    seed=TEST_CLIENT_SEED,
    port=9099,
    endpoint=["http://127.0.0.1:9099/submit"],
    network="testnet",  # Register on testnet Almanac
)

fund_agent_if_low(test_client.wallet.address())


# =============================================================================
# EVENT HANDLERS
# =============================================================================

@test_client.on_event("startup")
async def startup_handler(ctx: Context):
    """Send a test request on startup."""
    ctx.logger.info("=" * 60)
    ctx.logger.info("🧪 HypeLens Test Client Starting...")
    ctx.logger.info(f"📍 Client Address: {test_client.address}")
    ctx.logger.info("=" * 60)
    
    if not MASTER_AGENT_ADDRESS:
        ctx.logger.error("❌ MASTER_AGENT_ADDRESS not set in .env!")
        ctx.logger.error("   Run 'python run.py --discover' to get the address")
        return
    
    # Create test request
    request_id = str(uuid.uuid4())[:8]
    test_request = HypeLensRequest(
        request_id=request_id,
        business_name="Test Cafe (HypeLens Demo)",
        baseline_customers_per_hour=42.0,
        date=datetime.now().strftime("%Y-%m-%d"),
        time=datetime.now().hour,
        latitude=40.770530,
        longitude=-73.982456,
    )
    
    ctx.logger.info("\n" + "=" * 60)
    ctx.logger.info("📤 SENDING TEST REQUEST")
    ctx.logger.info("=" * 60)
    ctx.logger.info(f"   To: {MASTER_AGENT_ADDRESS}")
    ctx.logger.info(f"   Request ID: {request_id}")
    ctx.logger.info(f"   Business: {test_request.business_name}")
    ctx.logger.info(f"   Baseline: {test_request.baseline_customers_per_hour} customers/hr")
    ctx.logger.info(f"   Date/Time: {test_request.date} @ {test_request.time}:00")
    ctx.logger.info("=" * 60)
    
    await ctx.send(MASTER_AGENT_ADDRESS, test_request)
    ctx.logger.info("✅ Request sent! Waiting for response...")


@test_client.on_message(model=HypeLensResponse)
async def handle_response(ctx: Context, sender: str, msg: HypeLensResponse):
    """Handle the final prediction response."""
    ctx.logger.info("\n" + "=" * 60)
    ctx.logger.info("📥 RECEIVED HYPELENS RESPONSE")
    ctx.logger.info("=" * 60)
    ctx.logger.info(f"   From: {sender}")
    ctx.logger.info(f"   Request ID: {msg.request_id}")
    ctx.logger.info(f"   Success: {msg.success}")
    
    if msg.error:
        ctx.logger.error(f"   ❌ Error: {msg.error}")
    else:
        ctx.logger.info("\n📊 PREDICTION RESULTS:")
        ctx.logger.info(f"   Business: {msg.business_name}")
        ctx.logger.info(f"   Baseline: {msg.baseline_customers_per_hour} customers/hr")
        ctx.logger.info(f"   Extra: {msg.expected_extra_customers_per_hour:+.1f} customers/hr")
        ctx.logger.info(f"   Total: {msg.expected_total_customers_per_hour} customers/hr")
        ctx.logger.info(f"   Confidence: {msg.overall_confidence:.0%}")
        ctx.logger.info(f"   Summary: {msg.summary}")
        
        ctx.logger.info("\n📡 INDIVIDUAL SIGNALS:")
        for signal in msg.signals:
            src = signal.get("source", "?")
            extra = signal.get("extra_customers_per_hour", 0)
            conf = signal.get("confidence", 0.5)
            exp = signal.get("explanation", "")[:60]
            ctx.logger.info(f"   • {src}: {extra:+.1f}/hr (conf: {conf:.0%})")
            if exp:
                ctx.logger.info(f"     └─ {exp}...")
    
    ctx.logger.info("\n" + "=" * 60)
    ctx.logger.info("✅ TEST COMPLETE")
    ctx.logger.info("=" * 60 + "\n")


# =============================================================================
# STANDALONE EXECUTION
# =============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🧪 HypeLens Test Client")
    print("=" * 60)
    
    if not MASTER_AGENT_ADDRESS:
        print("\n❌ ERROR: MASTER_AGENT_ADDRESS not set!")
        print("\nSteps to fix:")
        print("1. Run: python run.py --discover")
        print("2. Copy the MASTER_AGENT_ADDRESS to your .env file")
        print("3. Re-run this test client")
        print("\n")
        sys.exit(1)
    
    print(f"\nTarget Master Agent: {MASTER_AGENT_ADDRESS}")
    print("\nStarting test client...\n")
    test_client.run()
