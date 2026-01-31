import { NextResponse } from "next/server"

// Mock agent activity data
const mockAgentActivity = {
  orchestrator: {
    name: "Orchestrator",
    status: "active",
    decisions_count: 47,
    workflows: [
      { id: "wf-001", name: "Staffing Optimization", status: "active", triggered: "2 min ago" },
      { id: "wf-002", name: "Inventory Alert", status: "completed", triggered: "15 min ago" },
      { id: "wf-003", name: "Surge Detection", status: "monitoring", triggered: "Continuous" },
    ],
    decisions: [
      { id: "dec-001", decision: "Triggered staff optimization due to +22% traffic forecast", time: "2 min ago" },
      { id: "dec-002", decision: "Approved inventory order based on demand prediction", time: "15 min ago" },
      { id: "dec-003", decision: "Escalated weather alert to operator", time: "1 hr ago" },
    ],
    thresholds: [
      { metric: "Traffic Surge", value: ">80", current: "92", status: "exceeded" },
      { metric: "Confidence Min", value: ">0.7", current: "0.82", status: "met" },
      { metric: "Staff Buffer", value: "15%", current: "20%", status: "met" },
    ],
  },
  predictor: {
    name: "Predictor",
    status: "processing",
    predictions_count: 156,
    signals: [
      { source: "Weather API", value: "Clear, 72°F", weight: "0.25" },
      { source: "Events API", value: "Concert at 7pm", weight: "0.35" },
      { source: "Maps API", value: "+23% activity", weight: "0.25" },
      { source: "Historical", value: "Thursday pattern", weight: "0.15" },
    ],
    forecasts: [
      { period: "4pm - 5pm", traffic: 78, confidence: 0.85, change: "+18%" },
      { period: "5pm - 6pm", traffic: 92, confidence: 0.82, change: "+31%" },
      { period: "6pm - 7pm", traffic: 98, confidence: 0.80, change: "+40%" },
      { period: "7pm - 8pm", traffic: 95, confidence: 0.78, change: "+36%" },
    ],
    anomalies: [
      { id: "anom-001", type: "Surge Detected", detail: "Evening traffic 40% above normal", severity: "high" },
      { id: "anom-002", type: "Pattern Break", detail: "Thursday behaving like weekend", severity: "medium" },
    ],
  },
  operator: {
    name: "Operator",
    status: "standby",
    actions_count: 23,
    tools: [
      { name: "schedule_shift", description: "Add or modify staff shifts", calls: 12 },
      { name: "send_notification", description: "Send SMS/email to staff", calls: 8 },
      { name: "place_order", description: "Order inventory from suppliers", calls: 3 },
      { name: "update_availability", description: "Sync with scheduling system", calls: 5 },
    ],
    actions: [
      { id: "act-001", type: "schedule", action: "Added shift: Alex Kim (4-9pm)", status: "completed", time: "1 min ago" },
      { id: "act-002", type: "message", action: "SMS sent to Jordan Lee", status: "completed", time: "1 min ago" },
      { id: "act-003", type: "order", action: "Milk order +15% placed", status: "completed", time: "Just now" },
    ],
    pending: [
      { id: "pend-001", action: "Notify evening staff about extended hours", priority: "medium" },
      { id: "pend-002", action: "Order pastries for morning rush", priority: "low" },
    ],
  },
}

export async function GET() {
  return NextResponse.json(mockAgentActivity)
}
