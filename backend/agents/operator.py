"""
Operator Agent - Executes real-world actions through MCP tools
Handles scheduling, notifications, and order management.
"""

from typing import Optional
from datetime import datetime
import random


class OperatorAgent:
    """
    The Operator Agent executes real-world actions through MCP tools.
    It handles staff scheduling, notifications, and inventory orders.
    """
    
    def __init__(self):
        self.name = "Operator"
        self.status = "standby"
        self.actions_count = 0
        self.executed_actions = []
        self.pending_queue = []
        self.mcp_tools = {
            "schedule_shift": {
                "description": "Add or modify staff shifts",
                "calls": 0,
            },
            "send_notification": {
                "description": "Send SMS/email to staff",
                "calls": 0,
            },
            "place_order": {
                "description": "Order inventory from suppliers",
                "calls": 0,
            },
            "update_availability": {
                "description": "Sync with scheduling system",
                "calls": 0,
            },
        }
    
    def get_status(self) -> dict:
        """Return agent status."""
        return {
            "name": self.name,
            "status": self.status,
            "actions_count": self.actions_count,
            "pending_count": len(self.pending_queue),
            "mcp_tools": list(self.mcp_tools.keys()),
        }
    
    def get_executed_actions(self) -> list:
        """Return recently executed actions."""
        return [
            {
                "id": "act-001",
                "type": "schedule",
                "action": "Added shift: Alex Kim (4-9pm)",
                "status": "completed",
                "timestamp": datetime.now().isoformat(),
            },
            {
                "id": "act-002",
                "type": "message",
                "action": "SMS sent to Jordan Lee",
                "status": "completed",
                "timestamp": datetime.now().isoformat(),
            },
            {
                "id": "act-003",
                "type": "order",
                "action": "Milk order +15% placed",
                "status": "completed",
                "timestamp": datetime.now().isoformat(),
            },
        ]
    
    def get_pending_queue(self) -> list:
        """Return pending action queue."""
        return [
            {
                "id": "pend-001",
                "action": "Notify evening staff about extended hours",
                "priority": "medium",
                "created": datetime.now().isoformat(),
            },
            {
                "id": "pend-002",
                "action": "Order pastries for morning rush",
                "priority": "low",
                "created": datetime.now().isoformat(),
            },
        ]
    
    async def execute_action(self, action_type: str, payload: dict) -> dict:
        """Execute an action based on type and payload."""
        self.status = "executing"
        self.actions_count += 1
        
        result = {
            "id": f"act-{self.actions_count}",
            "type": action_type,
            "payload": payload,
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
        }
        
        # Route to appropriate MCP tool
        if action_type == "schedule":
            result["tool_used"] = "schedule_shift"
            self.mcp_tools["schedule_shift"]["calls"] += 1
        elif action_type == "message":
            result["tool_used"] = "send_notification"
            self.mcp_tools["send_notification"]["calls"] += 1
        elif action_type == "order":
            result["tool_used"] = "place_order"
            self.mcp_tools["place_order"]["calls"] += 1
        
        self.executed_actions.append(result)
        self.status = "standby"
        
        return result
    
    async def schedule_shift(
        self,
        employee_id: str,
        employee_name: str,
        shift_start: str,
        shift_end: str,
        role: str,
    ) -> dict:
        """
        MCP Tool: schedule_shift
        Add or modify a staff shift in the scheduling system.
        """
        self.mcp_tools["schedule_shift"]["calls"] += 1
        self.actions_count += 1
        
        result = {
            "success": True,
            "tool": "schedule_shift",
            "action": f"Scheduled {employee_name} as {role} from {shift_start} to {shift_end}",
            "details": {
                "employee_id": employee_id,
                "employee_name": employee_name,
                "shift_start": shift_start,
                "shift_end": shift_end,
                "role": role,
            },
            "timestamp": datetime.now().isoformat(),
        }
        
        self.executed_actions.append(result)
        return result
    
    async def send_notification(
        self,
        recipient_id: str,
        message: str,
        channel: str = "sms",
    ) -> dict:
        """
        MCP Tool: send_notification
        Send a notification to staff via SMS, email, or push.
        """
        self.mcp_tools["send_notification"]["calls"] += 1
        self.actions_count += 1
        
        result = {
            "success": True,
            "tool": "send_notification",
            "action": f"Sent {channel.upper()} to recipient {recipient_id}",
            "details": {
                "recipient_id": recipient_id,
                "message": message,
                "channel": channel,
                "delivered": True,
            },
            "timestamp": datetime.now().isoformat(),
        }
        
        self.executed_actions.append(result)
        return result
    
    async def place_order(
        self,
        item: str,
        quantity: int,
        supplier_id: str,
    ) -> dict:
        """
        MCP Tool: place_order
        Place an inventory order with a supplier.
        """
        self.mcp_tools["place_order"]["calls"] += 1
        self.actions_count += 1
        
        order_id = f"ORD-{random.randint(10000, 99999)}"
        
        result = {
            "success": True,
            "tool": "place_order",
            "action": f"Placed order for {quantity}x {item}",
            "details": {
                "order_id": order_id,
                "item": item,
                "quantity": quantity,
                "supplier_id": supplier_id,
                "estimated_delivery": "Tomorrow 6am",
            },
            "timestamp": datetime.now().isoformat(),
        }
        
        self.executed_actions.append(result)
        return result
    
    async def execute_surge_actions(self, prediction: dict) -> list:
        """Execute a series of actions in response to a surge prediction."""
        actions = []
        
        # Add extra staff
        staff_action = await self.schedule_shift(
            employee_id="emp-004",
            employee_name="Alex Kim",
            shift_start="16:00",
            shift_end="21:00",
            role="Barista",
        )
        actions.append(staff_action)
        
        # Notify on-call staff
        notify_action = await self.send_notification(
            recipient_id="emp-005",
            message=f"Surge alert: High traffic expected. Please confirm availability for evening shift.",
            channel="sms",
        )
        actions.append(notify_action)
        
        # Order extra inventory
        order_action = await self.place_order(
            item="Milk (gallons)",
            quantity=15,
            supplier_id="sup-001",
        )
        actions.append(order_action)
        
        return actions
    
    def get_mcp_tool_stats(self) -> dict:
        """Get statistics for MCP tool usage."""
        return {
            tool: {
                "description": info["description"],
                "total_calls": info["calls"],
            }
            for tool, info in self.mcp_tools.items()
        }
