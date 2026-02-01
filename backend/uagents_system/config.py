"""
HypeLens uAgents Configuration
==============================
Centralized configuration for agent seeds and addresses.
All values can be overridden via environment variables.

SETUP INSTRUCTIONS:
1. Run: python run.py --discover
2. Copy the printed addresses to your .env file
3. (Optional) For Agentverse Mailbox, create mailboxes at https://agentverse.ai
   and add the keys to your .env file
"""

import os
from dotenv import load_dotenv

# Load environment
load_dotenv()


# =============================================================================
# AGENT SEEDS (for deterministic address generation)
# =============================================================================
# These seeds generate consistent agent addresses across restarts.
# Change them if you want new addresses (e.g., for fresh deployment).

WEATHER_AGENT_SEED = os.getenv(
    "WEATHER_AGENT_SEED", 
    "hypelens-weather-agent-seed-v1"
)
MTA_AGENT_SEED = os.getenv(
    "MTA_AGENT_SEED", 
    "hypelens-mta-agent-seed-v1"
)
TRAFFIC_AGENT_SEED = os.getenv(
    "TRAFFIC_AGENT_SEED", 
    "hypelens-traffic-agent-seed-v1"
)
MASTER_AGENT_SEED = os.getenv(
    "MASTER_AGENT_SEED", 
    "hypelens-master-agent-seed-v1"
)


# =============================================================================
# AGENT ADDRESSES (discovered after first run)
# =============================================================================
# These are populated by running: python run.py --discover
# Copy them to your .env file.

WEATHER_AGENT_ADDRESS = os.getenv("WEATHER_AGENT_ADDRESS", None)
MTA_AGENT_ADDRESS = os.getenv("MTA_AGENT_ADDRESS", None)
TRAFFIC_AGENT_ADDRESS = os.getenv("TRAFFIC_AGENT_ADDRESS", None)
MASTER_AGENT_ADDRESS = os.getenv("MASTER_AGENT_ADDRESS", None)


# =============================================================================
# AGENTVERSE MAILBOX KEYS (for remote communication)
# =============================================================================
# Create mailboxes at https://agentverse.ai and add keys here.
# This enables agents to communicate without local port-forwarding.

WEATHER_AGENT_MAILBOX_KEY = os.getenv("WEATHER_AGENT_MAILBOX_KEY", None)
MTA_AGENT_MAILBOX_KEY = os.getenv("MTA_AGENT_MAILBOX_KEY", None)
TRAFFIC_AGENT_MAILBOX_KEY = os.getenv("TRAFFIC_AGENT_MAILBOX_KEY", None)
MASTER_AGENT_MAILBOX_KEY = os.getenv("MASTER_AGENT_MAILBOX_KEY", None)


# =============================================================================
# AGENT PORTS (for local HTTP endpoints)
# =============================================================================

MASTER_AGENT_PORT = int(os.getenv("MASTER_AGENT_PORT", "8000"))
WEATHER_AGENT_PORT = int(os.getenv("WEATHER_AGENT_PORT", "8001"))
MTA_AGENT_PORT = int(os.getenv("MTA_AGENT_PORT", "8002"))
TRAFFIC_AGENT_PORT = int(os.getenv("TRAFFIC_AGENT_PORT", "8003"))


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def validate_config():
    """Check if required addresses are configured."""
    missing = []
    
    if not WEATHER_AGENT_ADDRESS:
        missing.append("WEATHER_AGENT_ADDRESS")
    if not MTA_AGENT_ADDRESS:
        missing.append("MTA_AGENT_ADDRESS")
    if not TRAFFIC_AGENT_ADDRESS:
        missing.append("TRAFFIC_AGENT_ADDRESS")
    
    if missing:
        print("\n⚠️  WARNING: Some agent addresses are not configured!")
        print(f"   Missing: {', '.join(missing)}")
        print("\n   Run: python run.py --discover")
        print("   Then copy the addresses to your .env file\n")
        return False
    
    return True


def print_config():
    """Print current configuration."""
    print("\n" + "=" * 60)
    print("🔧 HYPELENS CONFIGURATION")
    print("=" * 60)
    print("\nAgent Addresses:")
    print(f"   Master:  {MASTER_AGENT_ADDRESS or 'NOT SET'}")
    print(f"   Weather: {WEATHER_AGENT_ADDRESS or 'NOT SET'}")
    print(f"   MTA:     {MTA_AGENT_ADDRESS or 'NOT SET'}")
    print(f"   Traffic: {TRAFFIC_AGENT_ADDRESS or 'NOT SET'}")
    print("\nMailbox Keys:")
    print(f"   Master:  {'SET' if MASTER_AGENT_MAILBOX_KEY else 'NOT SET'}")
    print(f"   Weather: {'SET' if WEATHER_AGENT_MAILBOX_KEY else 'NOT SET'}")
    print(f"   MTA:     {'SET' if MTA_AGENT_MAILBOX_KEY else 'NOT SET'}")
    print(f"   Traffic: {'SET' if TRAFFIC_AGENT_MAILBOX_KEY else 'NOT SET'}")
    print("\nPorts:")
    print(f"   Master:  {MASTER_AGENT_PORT}")
    print(f"   Weather: {WEATHER_AGENT_PORT}")
    print(f"   MTA:     {MTA_AGENT_PORT}")
    print(f"   Traffic: {TRAFFIC_AGENT_PORT}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    print_config()
    validate_config()
