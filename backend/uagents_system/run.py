"""
HypeLens Multi-Agent System Runner
==================================
Uses the Fetch.ai Bureau to start all agents simultaneously.

Usage:
    python run.py              # Start all agents
    python run.py --discover   # Only print agent addresses for configuration

After running with --discover, copy the agent addresses to your .env file:
    WEATHER_AGENT_ADDRESS=agent1q...
    MTA_AGENT_ADDRESS=agent1q...
    TRAFFIC_AGENT_ADDRESS=agent1q...
"""

import os
import sys
import argparse

# Add parent paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

from uagents import Bureau

# Import all agents
from weather_agent import weather_agent
from mta_agent import mta_agent
from traffic_agent import traffic_agent
from master_agent_uagent import master_agent


def print_agent_addresses():
    """Print all agent addresses for configuration."""
    print("\n" + "=" * 70)
    print("🔍 HYPELENS AGENT DISCOVERY")
    print("=" * 70)
    print("\nCopy these addresses to your .env file:\n")
    print(f"WEATHER_AGENT_ADDRESS={weather_agent.address}")
    print(f"MTA_AGENT_ADDRESS={mta_agent.address}")
    print(f"TRAFFIC_AGENT_ADDRESS={traffic_agent.address}")
    print(f"MASTER_AGENT_ADDRESS={master_agent.address}")
    print("\n" + "=" * 70)
    print("\n📋 Example .env additions:\n")
    print(f"# HypeLens uAgents Addresses (auto-discovered)")
    print(f"WEATHER_AGENT_ADDRESS={weather_agent.address}")
    print(f"MTA_AGENT_ADDRESS={mta_agent.address}")
    print(f"TRAFFIC_AGENT_ADDRESS={traffic_agent.address}")
    print(f"MASTER_AGENT_ADDRESS={master_agent.address}")
    print("\n" + "=" * 70)


def run_bureau():
    """Start all agents using Bureau."""
    print("\n" + "=" * 70)
    print("🏙️  HYPELENS METROPOLIS - Multi-Agent System")
    print("=" * 70)
    print("\nStarting all agents via Bureau...")
    print("\nAgent Addresses:")
    print(f"   🏙️  Master:  {master_agent.address}")
    print(f"   🌤️  Weather: {weather_agent.address}")
    print(f"   🚇 MTA:     {mta_agent.address}")
    print(f"   🚗 Traffic: {traffic_agent.address}")
    print("\nPorts:")
    print("   Master:  http://127.0.0.1:8000")
    print("   Weather: http://127.0.0.1:8001")
    print("   MTA:     http://127.0.0.1:8002")
    print("   Traffic: http://127.0.0.1:8003")
    print("\n" + "=" * 70)
    print("💡 TIP: To send a test request, run: python test_client.py")
    print("=" * 70 + "\n")
    
    # Create Bureau and add all agents
    bureau = Bureau(
        port=8000,  # Main port for the Bureau
        endpoint=["http://127.0.0.1:8000/submit"],
    )
    
    bureau.add(master_agent)
    bureau.add(weather_agent)
    bureau.add(mta_agent)
    bureau.add(traffic_agent)
    
    # Run all agents
    bureau.run()


def main():
    parser = argparse.ArgumentParser(
        description="HypeLens Multi-Agent System Runner"
    )
    parser.add_argument(
        "--discover",
        action="store_true",
        help="Only print agent addresses for configuration (don't run agents)"
    )
    args = parser.parse_args()
    
    if args.discover:
        print_agent_addresses()
    else:
        # First show addresses, then run
        print_agent_addresses()
        print("\n🚀 Starting Bureau in 3 seconds...\n")
        import time
        time.sleep(3)
        run_bureau()


if __name__ == "__main__":
    main()
