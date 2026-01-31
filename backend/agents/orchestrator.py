"""
Orchestrator Agent - Central decision maker for CityFootfall AI
Monitors predictions, detects anomalies, and triggers workflows.
"""

from typing import Optional
from datetime import datetime
import random


class OrchestratorAgent:
    """
    The Orchestrator Agent is the central brain of the system.
    It monitors predictions from the Predictor Agent and decides
    when to trigger actions through the Operator Agent.
    """
    
    def __init__(self):
        self.name = "Orchestrator"
        self.status = "active"
        self.decisions_count = 0
        self.thresholds = {
            "traffic_surge": 80,
            "confidence_min": 0.7,
            "staff_buffer": 0.15,
        }
        self.active_workflows = []
        self.recent_decisions = []
    
    def get_status(self) -> dict:
        """Return agent status."""
        return {
            "name": self.name,
            "status": self.status,
            "decisions_count": self.decisions_count,
            "active_workflows": len(self.active_workflows),
            "thresholds": self.thresholds,
        }
    
    def get_active_workflows(self) -> list:
        """Return list of active workflows."""
        # Return mock data for demo
        return [
            {
                "id": "wf-001",
                "name": "Staffing Optimization",
                "status": "active",
                "triggered": datetime.now().isoformat(),
            },
            {
                "id": "wf-002",
                "name": "Inventory Alert",
                "status": "completed",
                "triggered": datetime.now().isoformat(),
            },
            {
                "id": "wf-003",
                "name": "Surge Detection",
                "status": "monitoring",
                "triggered": datetime.now().isoformat(),
            },
        ]
    
    def get_recent_decisions(self) -> list:
        """Return recent decisions made by the agent."""
        return [
            {
                "id": "dec-001",
                "decision": "Triggered staff optimization due to +22% traffic forecast",
                "timestamp": datetime.now().isoformat(),
                "confidence": 0.85,
            },
            {
                "id": "dec-002",
                "decision": "Approved inventory order based on demand prediction",
                "timestamp": datetime.now().isoformat(),
                "confidence": 0.82,
            },
            {
                "id": "dec-003",
                "decision": "Escalated weather alert to operator",
                "timestamp": datetime.now().isoformat(),
                "confidence": 0.78,
            },
        ]
    
    async def evaluate_prediction(self, prediction: dict) -> dict:
        """
        Evaluate a prediction and decide on actions.
        This is the core decision-making logic.
        """
        decisions = []
        
        # Check if traffic exceeds surge threshold
        if prediction.get("traffic_index", 0) > self.thresholds["traffic_surge"]:
            decisions.append({
                "type": "surge_alert",
                "action": "trigger_staffing_workflow",
                "reason": f"Traffic index {prediction['traffic_index']} exceeds threshold",
            })
        
        # Check confidence level
        if prediction.get("confidence", 0) >= self.thresholds["confidence_min"]:
            decisions.append({
                "type": "high_confidence",
                "action": "auto_execute",
                "reason": f"Confidence {prediction['confidence']} meets minimum",
            })
        
        self.decisions_count += len(decisions)
        self.recent_decisions.extend(decisions)
        
        return {"prediction_evaluated": True, "decisions": decisions}
    
    async def trigger_surge_response(self, prediction: dict) -> list:
        """Trigger surge response workflows."""
        workflows = [
            {
                "id": f"wf-{random.randint(100, 999)}",
                "name": "Emergency Staffing",
                "status": "triggered",
                "prediction_id": prediction.get("id"),
            },
            {
                "id": f"wf-{random.randint(100, 999)}",
                "name": "Inventory Check",
                "status": "triggered",
                "prediction_id": prediction.get("id"),
            },
        ]
        
        self.active_workflows.extend(workflows)
        self.decisions_count += 1
        
        return workflows
    
    def check_thresholds(self, metrics: dict) -> list:
        """Check if any metrics exceed thresholds."""
        alerts = []
        
        for metric, value in metrics.items():
            if metric in self.thresholds:
                if value > self.thresholds[metric]:
                    alerts.append({
                        "metric": metric,
                        "value": value,
                        "threshold": self.thresholds[metric],
                        "status": "exceeded",
                    })
        
        return alerts
