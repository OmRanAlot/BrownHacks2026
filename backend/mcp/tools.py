"""
MCP (Model Context Protocol) Tools Registry
Provides tool definitions and execution for AI agent integration.
"""

from typing import Callable, Any, Optional
from datetime import datetime
import json


class MCPTool:
    """Represents a single MCP tool."""
    
    def __init__(
        self,
        name: str,
        description: str,
        parameters: dict,
        handler: Callable,
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.handler = handler
        self.call_count = 0
        self.last_called = None
    
    def to_schema(self) -> dict:
        """Convert to MCP tool schema format."""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": {
                "type": "object",
                "properties": self.parameters,
                "required": [k for k, v in self.parameters.items() if v.get("required", False)],
            },
        }
    
    async def execute(self, params: dict) -> Any:
        """Execute the tool with given parameters."""
        self.call_count += 1
        self.last_called = datetime.now().isoformat()
        return await self.handler(params)


class MCPToolRegistry:
    """
    Registry for MCP tools.
    Allows registration, discovery, and execution of tools.
    Compatible with the Model Context Protocol for AI agent integration.
    """
    
    def __init__(self):
        self.tools: dict[str, MCPTool] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register default CityFootfall tools."""
        
        # Schedule Shift Tool
        self.register(
            name="schedule_shift",
            description="Schedule a staff shift. Adds or modifies an employee's work schedule.",
            parameters={
                "employee_id": {
                    "type": "string",
                    "description": "Unique identifier for the employee",
                    "required": True,
                },
                "employee_name": {
                    "type": "string",
                    "description": "Name of the employee",
                    "required": True,
                },
                "shift_start": {
                    "type": "string",
                    "description": "Shift start time (HH:MM format)",
                    "required": True,
                },
                "shift_end": {
                    "type": "string",
                    "description": "Shift end time (HH:MM format)",
                    "required": True,
                },
                "role": {
                    "type": "string",
                    "description": "Role for the shift (e.g., Barista, Cashier)",
                    "required": True,
                },
            },
            handler=self._handle_schedule_shift,
        )
        
        # Send Notification Tool
        self.register(
            name="send_notification",
            description="Send a notification to staff via SMS, email, or push notification.",
            parameters={
                "recipient_id": {
                    "type": "string",
                    "description": "ID of the notification recipient",
                    "required": True,
                },
                "message": {
                    "type": "string",
                    "description": "Notification message content",
                    "required": True,
                },
                "channel": {
                    "type": "string",
                    "description": "Notification channel (sms, email, push)",
                    "enum": ["sms", "email", "push"],
                    "required": False,
                },
            },
            handler=self._handle_send_notification,
        )
        
        # Place Order Tool
        self.register(
            name="place_order",
            description="Place an inventory order with a supplier.",
            parameters={
                "item": {
                    "type": "string",
                    "description": "Name of the item to order",
                    "required": True,
                },
                "quantity": {
                    "type": "integer",
                    "description": "Quantity to order",
                    "required": True,
                },
                "supplier_id": {
                    "type": "string",
                    "description": "ID of the supplier",
                    "required": True,
                },
                "priority": {
                    "type": "string",
                    "description": "Order priority (normal, urgent)",
                    "enum": ["normal", "urgent"],
                    "required": False,
                },
            },
            handler=self._handle_place_order,
        )
        
        # Get Prediction Tool
        self.register(
            name="get_prediction",
            description="Get foot traffic prediction for a location.",
            parameters={
                "location_id": {
                    "type": "string",
                    "description": "ID of the business location",
                    "required": True,
                },
                "date": {
                    "type": "string",
                    "description": "Date for prediction (YYYY-MM-DD format)",
                    "required": False,
                },
            },
            handler=self._handle_get_prediction,
        )
        
        # Get City Signals Tool
        self.register(
            name="get_city_signals",
            description="Get current city signals (weather, events, maps activity) for a location.",
            parameters={
                "location_id": {
                    "type": "string",
                    "description": "ID of the business location",
                    "required": True,
                },
            },
            handler=self._handle_get_city_signals,
        )
    
    def register(
        self,
        name: str,
        description: str,
        parameters: dict,
        handler: Callable,
    ) -> None:
        """Register a new MCP tool."""
        tool = MCPTool(
            name=name,
            description=description,
            parameters=parameters,
            handler=handler,
        )
        self.tools[name] = tool
    
    def list_tools(self) -> list:
        """List all available tools in MCP schema format."""
        return [tool.to_schema() for tool in self.tools.values()]
    
    async def execute(self, tool_name: str, params: dict) -> Any:
        """Execute a tool by name with given parameters."""
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        tool = self.tools[tool_name]
        return await tool.execute(params)
    
    def get_tool_stats(self) -> dict:
        """Get usage statistics for all tools."""
        return {
            name: {
                "call_count": tool.call_count,
                "last_called": tool.last_called,
            }
            for name, tool in self.tools.items()
        }
    
    # ============ Tool Handlers ============
    
    async def _handle_schedule_shift(self, params: dict) -> dict:
        """Handle schedule_shift tool execution."""
        return {
            "success": True,
            "message": f"Scheduled {params['employee_name']} from {params['shift_start']} to {params['shift_end']}",
            "shift_id": f"shift-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "details": params,
        }
    
    async def _handle_send_notification(self, params: dict) -> dict:
        """Handle send_notification tool execution."""
        channel = params.get("channel", "sms")
        return {
            "success": True,
            "message": f"Notification sent via {channel} to {params['recipient_id']}",
            "notification_id": f"notif-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "details": params,
        }
    
    async def _handle_place_order(self, params: dict) -> dict:
        """Handle place_order tool execution."""
        return {
            "success": True,
            "message": f"Order placed: {params['quantity']}x {params['item']}",
            "order_id": f"order-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "estimated_delivery": "Next business day",
            "details": params,
        }
    
    async def _handle_get_prediction(self, params: dict) -> dict:
        """Handle get_prediction tool execution."""
        return {
            "success": True,
            "location_id": params["location_id"],
            "date": params.get("date", datetime.now().strftime("%Y-%m-%d")),
            "prediction": {
                "traffic_index": 85,
                "confidence": 0.82,
                "demand_level": "High",
                "primary_driver": "Local events",
            },
        }
    
    async def _handle_get_city_signals(self, params: dict) -> dict:
        """Handle get_city_signals tool execution."""
        return {
            "success": True,
            "location_id": params["location_id"],
            "signals": {
                "weather": {"condition": "clear", "temperature": 72},
                "events": [{"name": "Concert", "distance": 0.4}],
                "maps_activity": {"popularity": 1.23},
                "disruptions": [],
            },
        }


# MCP Server Protocol Implementation
class MCPServer:
    """
    MCP Server implementation for integration with AI agents.
    Follows the Model Context Protocol specification.
    """
    
    def __init__(self, tool_registry: MCPToolRegistry):
        self.registry = tool_registry
        self.protocol_version = "2024-11-05"
        self.server_info = {
            "name": "cityfootfall-mcp-server",
            "version": "1.0.0",
        }
    
    def get_server_info(self) -> dict:
        """Return server information."""
        return {
            "protocolVersion": self.protocol_version,
            "serverInfo": self.server_info,
            "capabilities": {
                "tools": {"listChanged": False},
            },
        }
    
    def list_tools(self) -> dict:
        """List available tools (MCP tools/list response)."""
        return {
            "tools": self.registry.list_tools(),
        }
    
    async def call_tool(self, name: str, arguments: dict) -> dict:
        """Call a tool (MCP tools/call response)."""
        try:
            result = await self.registry.execute(name, arguments)
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2),
                    }
                ],
            }
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error: {str(e)}",
                    }
                ],
                "isError": True,
            }
