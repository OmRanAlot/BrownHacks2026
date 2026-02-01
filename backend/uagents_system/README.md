# HypeLens Multi-Agent System

A distributed micro-agent architecture for NYC cafe foot traffic prediction using the Fetch.ai `uagents` framework.

## Architecture

```
                    ┌─────────────────────────────────────┐
                    │        HypeLensMasterAgent          │
                    │        (Orchestrator)               │
                    │        Port: 8000                   │
                    └──────────────┬──────────────────────┘
                                   │
           ┌───────────────────────┼───────────────────────┐
           │                       │                       │
           ▼                       ▼                       ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   WeatherAgent   │    │     MTAAgent     │    │   TrafficAgent   │
│   (RAG + Weather)│    │  (Subway Data)   │    │ (Google Traffic) │
│   Port: 8001     │    │   Port: 8002     │    │   Port: 8003     │
└──────────────────┘    └──────────────────┘    └──────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ predict_for_     │    │ run_mta_         │    │ forecast_extra_  │
│ datetime()       │    │ forecast()       │    │ customers()      │
└──────────────────┘    └──────────────────┘    └──────────────────┘
    (Pinecone +              (Live vs              (Google Traffic
     Open-Meteo)           Baseline MTA)              API data)
```

## Message Flow

1. **User Request** → `HypeLensRequest` → MasterAgent
2. **Fan-out**: Master sends `WeatherRequest`, `MTARequest`, `TrafficRequest` in parallel
3. **Sub-agents execute** their wrapped logic and return responses
4. **Fusion**: Master collects all responses, normalizes signals, applies weighted average
5. **Final Response** → `HypeLensResponse` with "Hype Score"

## Quick Start

### 1. Install Dependencies

```bash
cd backend/uagents_system
pip install -r requirements.txt
```

### 2. Discover Agent Addresses

```bash
python run.py --discover
```

This prints all agent addresses. Copy them to your `.env` file:

```env
# HypeLens uAgents Addresses
WEATHER_AGENT_ADDRESS=agent1q...
MTA_AGENT_ADDRESS=agent1q...
TRAFFIC_AGENT_ADDRESS=agent1q...
MASTER_AGENT_ADDRESS=agent1q...
```

### 3. Start the Bureau (All Agents)

```bash
python run.py
```

This starts all 4 agents in a single Bureau process.

### 4. Test the System

In another terminal:

```bash
python test_client.py
```

## Files

| File | Description |
|------|-------------|
| `schema.py` | Pydantic message models for all inter-agent communication |
| `weather_agent.py` | Wraps `predictor_agent.py` (RAG + Open-Meteo weather) |
| `mta_agent.py` | Wraps `mta.py` (subway crowding analysis) |
| `traffic_agent.py` | Wraps `nearbycongestion.py` (Google Traffic) |
| `master_agent_uagent.py` | Orchestrator that fuses all signals |
| `run.py` | Bureau runner to start all agents |
| `test_client.py` | Test agent to verify the system |
| `config.py` | Centralized configuration |

## Message Schemas

### HypeLensRequest (User → Master)
```python
class HypeLensRequest(Model):
    request_id: str
    business_name: str = "HypeLens Cafe"
    baseline_customers_per_hour: float = 42.0
    date: Optional[str] = None  # "YYYY-MM-DD"
    time: Optional[int] = None  # Hour 0-23
    latitude: float = 40.770530
    longitude: float = -73.982456
```

### HypeLensResponse (Master → User)
```python
class HypeLensResponse(Model):
    request_id: str
    success: bool
    business_name: str
    baseline_customers_per_hour: float
    signals: List[Dict[str, Any]]  # Raw signals from each agent
    expected_extra_customers_per_hour: float
    expected_total_customers_per_hour: float
    overall_confidence: float
    summary: str  # e.g., "Above baseline today"
    error: Optional[str] = None
```

## Agentverse Mailbox (Optional)

For production deployment without port-forwarding, configure Agentverse mailboxes:

1. Go to [Agentverse](https://agentverse.ai)
2. Create a mailbox for each agent
3. Add mailbox keys to `.env`:

```env
WEATHER_AGENT_MAILBOX_KEY=your-key-here
MTA_AGENT_MAILBOX_KEY=your-key-here
TRAFFIC_AGENT_MAILBOX_KEY=your-key-here
MASTER_AGENT_MAILBOX_KEY=your-key-here
```

## Running Individual Agents

Each agent can also run standalone:

```bash
python weather_agent.py   # Port 8001
python mta_agent.py       # Port 8002
python traffic_agent.py   # Port 8003
python master_agent_uagent.py  # Port 8000
```

## Logging

All agents use `ctx.logger.info` for rich console output. You'll see:

```
============================================================
📥 Received WeatherRequest from agent1q...
   Request ID: abc123
   Date: 2026-02-01, Time: 14
🔄 Calling predict_for_datetime()...
✅ Prediction complete: 45.2 traffic score
📤 Sending WeatherResponse to agent1q...
============================================================
```

## Signal Fusion Algorithm

The MasterAgent combines signals using confidence-weighted averaging:

```python
# Weighted average
for signal in signals:
    weight = max(0.05, signal.confidence)
    weighted_sum += signal.extra_customers_per_hour * weight
    weight_total += weight

extra = weighted_sum / weight_total

# Guardrails (cap at ±50-150% of baseline)
extra = max(-0.5 * baseline, min(extra, 1.5 * baseline))
```

## Troubleshooting

### "Agent address not found"
Run `python run.py --discover` and copy addresses to `.env`

### "Connection refused"
Make sure the Bureau is running: `python run.py`

### "Timeout" errors
- Check if sub-agents are responding (look at their logs)
- Increase timeout in `master_agent_uagent.py` (`PendingRequest.timeout_seconds`)

### Missing API keys
Ensure your `.env` has:
- `GEMINI_API_KEY` (for LLM calls)
- `OPENAI_API_KEY` (for embeddings)
- `PINECONE_API_KEY` (for vector search)
- `GOOGLE_API_KEY` (for traffic data)
