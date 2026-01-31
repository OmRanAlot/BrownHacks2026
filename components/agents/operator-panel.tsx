"use client"

import { useState } from "react"
import { Wrench, Calendar, MessageSquare, ShoppingCart, CheckCircle2, Clock, Play } from "lucide-react"
import { Button } from "@/components/ui/button"

const actions = [
  {
    id: "1",
    type: "schedule",
    action: "Added shift: Alex Kim (4-9pm)",
    status: "completed",
    time: "1 min ago",
  },
  {
    id: "2",
    type: "message",
    action: "SMS sent to Jordan Lee",
    status: "completed",
    time: "1 min ago",
  },
  {
    id: "3",
    type: "order",
    action: "Milk order +15% placed",
    status: "completed",
    time: "Just now",
  },
]

const mcpTools = [
  { name: "schedule_shift", description: "Add or modify staff shifts", calls: 12 },
  { name: "send_notification", description: "Send SMS/email to staff", calls: 8 },
  { name: "place_order", description: "Order inventory from suppliers", calls: 3 },
  { name: "update_availability", description: "Sync with scheduling system", calls: 5 },
]

const pendingActions = [
  { id: "1", action: "Notify evening staff about extended hours", priority: "medium" },
  { id: "2", action: "Order pastries for morning rush", priority: "low" },
]

export function OperatorPanel() {
  const [simulating, setSimulating] = useState(false)

  const handleSimulate = () => {
    setSimulating(true)
    setTimeout(() => setSimulating(false), 3000)
  }

  return (
    <div className="rounded-xl border border-border bg-card">
      <div className="border-b border-border p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-accent/10 text-accent">
              <Wrench className="h-6 w-6" />
            </div>
            <div>
              <h3 className="font-semibold text-foreground">Operator Agent</h3>
              <p className="text-sm text-accent">Executor</p>
            </div>
          </div>
          <span className="rounded-full bg-secondary px-3 py-1 text-xs font-medium text-secondary-foreground">Standby</span>
        </div>
      </div>

      <div className="space-y-6 p-6">
        {/* MCP Tools */}
        <div>
          <h4 className="mb-3 text-xs font-medium text-muted-foreground">MCP TOOLS AVAILABLE</h4>
          <div className="space-y-2">
            {mcpTools.map((tool) => (
              <div key={tool.name} className="flex items-center justify-between rounded-lg bg-secondary/30 px-3 py-2">
                <div>
                  <span className="font-mono text-sm text-primary">{tool.name}()</span>
                  <p className="text-xs text-muted-foreground">{tool.description}</p>
                </div>
                <span className="rounded bg-secondary px-2 py-0.5 text-xs text-muted-foreground">
                  {tool.calls} calls
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Actions Executed */}
        <div>
          <h4 className="mb-3 text-xs font-medium text-muted-foreground">ACTIONS EXECUTED</h4>
          <div className="space-y-2">
            {actions.map((action) => (
              <div key={action.id} className="flex items-center gap-3 rounded-lg bg-secondary/30 px-3 py-2">
                <ActionIcon type={action.type} />
                <div className="flex-1">
                  <p className="text-sm text-foreground">{action.action}</p>
                  <p className="text-xs text-muted-foreground">{action.time}</p>
                </div>
                <CheckCircle2 className="h-4 w-4 text-accent" />
              </div>
            ))}
          </div>
        </div>

        {/* Pending Queue */}
        <div>
          <h4 className="mb-3 text-xs font-medium text-muted-foreground">PENDING QUEUE</h4>
          <div className="space-y-2">
            {pendingActions.map((action) => (
              <div key={action.id} className="flex items-center gap-3 rounded-lg bg-secondary/30 px-3 py-2">
                <Clock className="h-4 w-4 text-muted-foreground" />
                <div className="flex-1">
                  <p className="text-sm text-foreground">{action.action}</p>
                  <p className="text-xs text-muted-foreground">Priority: {action.priority}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Simulate Button */}
        <Button onClick={handleSimulate} disabled={simulating} className="w-full gap-2">
          <Play className="h-4 w-4" />
          {simulating ? "Simulating Event Surge..." : "Simulate Event Surge"}
        </Button>
      </div>
    </div>
  )
}

function ActionIcon({ type }: { type: string }) {
  switch (type) {
    case "schedule":
      return <Calendar className="h-4 w-4 text-primary" />
    case "message":
      return <MessageSquare className="h-4 w-4 text-chart-3" />
    case "order":
      return <ShoppingCart className="h-4 w-4 text-accent" />
    default:
      return <Wrench className="h-4 w-4 text-muted-foreground" />
  }
}
