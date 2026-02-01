"""
HypeLens uAgents System
=======================
A distributed multi-agent architecture for NYC cafe foot traffic prediction.

Agents:
- WeatherAgent: Weather-based foot traffic predictions (RAG + Open-Meteo)
- MTAAgent: MTA subway crowding impact analysis
- TrafficAgent: Google Maps road congestion analysis
- HypeLensMasterAgent: Orchestrator that fuses all signals into a final prediction
"""
