"""
CityFootfall AI - FastAPI Backend
A multi-agent system for predicting foot traffic and automating operations.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import random

from agents.orchestrator import OrchestratorAgent
from agents.predictor import PredictorAgent
from agents.operator import OperatorAgent
from mcp.tools import MCPToolRegistry

app = FastAPI(
    title="CityFootfall AI API",
    description="Autonomous agents for urban business operations",
    version="1.0.0",
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
orchestrator = OrchestratorAgent()
predictor = PredictorAgent()
operator = OperatorAgent()

# Initialize MCP tool registry
mcp_registry = MCPToolRegistry()


# ============ Models ============

class LocationRequest(BaseModel):
    location_id: str
    name: str


class PredictionRequest(BaseModel):
    location_id: str
    date: Optional[str] = None


class PredictionResponse(BaseModel):
    location_id: str
    date: str
    hourly_forecasts: list
    confidence: float
    primary_driver: str
    demand_level: str
    traffic_change: str


class ActionRequest(BaseModel):
    action_type: str  # schedule, message, order
    payload: dict


class CitySignals(BaseModel):
    weather: dict
    events: list
    maps_activity: dict
    disruptions: list


class AgentStatus(BaseModel):
    name: str
    status: str
    last_action: str
    decisions_count: int


# ============ API Endpoints ============

@app.get("/")
async def root():
    return {
        "service": "CityFootfall AI",
        "version": "1.0.0",
        "status": "online",
        "agents": ["orchestrator", "predictor", "operator"],
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agents_online": True,
    }


# ============ Prediction Endpoints ============

@app.post("/api/predict", response_model=PredictionResponse)
async def get_prediction(request: PredictionRequest):
    """Generate foot traffic prediction for a location."""
    try:
        # Gather city signals
        signals = await predictor.gather_signals(request.location_id)
        
        # Generate prediction
        prediction = await predictor.predict(
            location_id=request.location_id,
            date=request.date or datetime.now().strftime("%Y-%m-%d"),
            signals=signals,
        )
        
        # Orchestrator evaluates prediction
        await orchestrator.evaluate_prediction(prediction)
        
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/signals/{location_id}")
async def get_city_signals(location_id: str):
    """Get current city signals for a location."""
    signals = await predictor.gather_signals(location_id)
    return signals


@app.get("/api/forecast/{location_id}")
async def get_hourly_forecast(location_id: str, hours: int = 24):
    """Get hourly foot traffic forecast."""
    forecast = await predictor.get_hourly_forecast(location_id, hours)
    return {"location_id": location_id, "forecasts": forecast}


# ============ Agent Endpoints ============

@app.get("/api/agents/status")
async def get_agents_status():
    """Get status of all agents."""
    return {
        "orchestrator": orchestrator.get_status(),
        "predictor": predictor.get_status(),
        "operator": operator.get_status(),
    }


@app.get("/api/agents/orchestrator/workflows")
async def get_orchestrator_workflows():
    """Get active workflows from orchestrator."""
    return {"workflows": orchestrator.get_active_workflows()}


@app.get("/api/agents/orchestrator/decisions")
async def get_orchestrator_decisions():
    """Get recent decisions from orchestrator."""
    return {"decisions": orchestrator.get_recent_decisions()}


@app.get("/api/agents/predictor/anomalies")
async def get_predictor_anomalies():
    """Get detected anomalies from predictor."""
    return {"anomalies": predictor.get_anomalies()}


@app.get("/api/agents/operator/actions")
async def get_operator_actions():
    """Get executed actions from operator."""
    return {"actions": operator.get_executed_actions()}


@app.get("/api/agents/operator/queue")
async def get_operator_queue():
    """Get pending action queue from operator."""
    return {"pending": operator.get_pending_queue()}


# ============ Action Endpoints ============

@app.post("/api/actions/execute")
async def execute_action(request: ActionRequest):
    """Execute an action through the operator agent."""
    try:
        result = await operator.execute_action(
            action_type=request.action_type,
            payload=request.payload,
        )
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/actions/schedule-shift")
async def schedule_shift(
    employee_id: str,
    employee_name: str,
    shift_start: str,
    shift_end: str,
    role: str,
):
    """Schedule a staff shift using MCP tool."""
    result = await operator.schedule_shift(
        employee_id=employee_id,
        employee_name=employee_name,
        shift_start=shift_start,
        shift_end=shift_end,
        role=role,
    )
    return result


@app.post("/api/actions/send-notification")
async def send_notification(
    recipient_id: str,
    message: str,
    channel: str = "sms",
):
    """Send notification to staff using MCP tool."""
    result = await operator.send_notification(
        recipient_id=recipient_id,
        message=message,
        channel=channel,
    )
    return result


@app.post("/api/actions/place-order")
async def place_order(
    item: str,
    quantity: int,
    supplier_id: str,
):
    """Place inventory order using MCP tool."""
    result = await operator.place_order(
        item=item,
        quantity=quantity,
        supplier_id=supplier_id,
    )
    return result


# ============ MCP Tool Endpoints ============

@app.get("/api/mcp/tools")
async def list_mcp_tools():
    """List all available MCP tools."""
    return {"tools": mcp_registry.list_tools()}


@app.post("/api/mcp/execute/{tool_name}")
async def execute_mcp_tool(tool_name: str, params: dict):
    """Execute an MCP tool directly."""
    try:
        result = await mcp_registry.execute(tool_name, params)
        return {"success": True, "result": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ Simulation Endpoints ============

@app.post("/api/simulate/event-surge")
async def simulate_event_surge(location_id: str):
    """Simulate an event surge for demo purposes."""
    # Trigger prediction with surge conditions
    surge_signals = {
        "weather": {"condition": "clear", "temp": 72, "rain_prob": 0},
        "events": [
            {"name": "Concert", "distance": 0.4, "time": "19:00", "expected_attendance": 5000}
        ],
        "maps_activity": {"popularity": 1.4, "trend": "increasing"},
        "disruptions": [],
    }
    
    # Generate prediction
    prediction = await predictor.predict(
        location_id=location_id,
        date=datetime.now().strftime("%Y-%m-%d"),
        signals=surge_signals,
    )
    
    # Orchestrator triggers workflows
    workflows = await orchestrator.trigger_surge_response(prediction)
    
    # Operator executes actions
    actions = await operator.execute_surge_actions(prediction)
    
    return {
        "simulation": "event_surge",
        "prediction": prediction,
        "workflows_triggered": workflows,
        "actions_executed": actions,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
