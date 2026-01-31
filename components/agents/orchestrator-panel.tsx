"use client"

import { Brain, CheckCircle2, AlertTriangle, Clock } from "lucide-react"

const workflows = [
  { id: "1", name: "Staffing Optimization", status: "active", triggered: "2 min ago" },
  { id: "2", name: "Inventory Alert", status: "completed", triggered: "15 min ago" },
  { id: "3", name: "Surge Detection", status: "monitoring", triggered: "Continuous" },
]

const decisions = [
  { id: "1", decision: "Triggered staff optimization due to +22% traffic forecast", time: "2 min ago" },
  { id: "2", decision: "Approved inventory order based on demand prediction", time: "15 min ago" },
  { id: "3", decision: "Escalated weather alert to operator", time: "1 hr ago" },
]

const thresholds = [
  { metric: "Traffic Surge", value: ">80", current: "92", status: "exceeded" },
  { metric: "Confidence Min", value: ">0.7", current: "0.82", status: "met" },
  { metric: "Staff Buffer", value: "15%", current: "20%", status: "met" },
]

export function OrchestratorPanel() {
  return (
    <div className="rounded-xl border border-border bg-card">
      <div className="border-b border-border p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-chart-3/10 text-chart-3">
              <Brain className="h-6 w-6" />
            </div>
            <div>
              <h3 className="font-semibold text-foreground">Orchestrator Agent</h3>
              <p className="text-sm text-chart-3">Decision Maker</p>
            </div>
          </div>
          <span className="rounded-full bg-accent/10 px-3 py-1 text-xs font-medium text-accent">Active</span>
        </div>
      </div>

      <div className="space-y-6 p-6">
        {/* Active Workflows */}
        <div>
          <h4 className="mb-3 text-xs font-medium text-muted-foreground">ACTIVE WORKFLOWS</h4>
          <div className="space-y-2">
            {workflows.map((workflow) => (
              <div key={workflow.id} className="flex items-center justify-between rounded-lg bg-secondary/30 px-3 py-2">
                <div className="flex items-center gap-2">
                  <WorkflowStatusIcon status={workflow.status} />
                  <span className="text-sm text-foreground">{workflow.name}</span>
                </div>
                <span className="text-xs text-muted-foreground">{workflow.triggered}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Decision Thresholds */}
        <div>
          <h4 className="mb-3 text-xs font-medium text-muted-foreground">DECISION THRESHOLDS</h4>
          <div className="space-y-2">
            {thresholds.map((threshold) => (
              <div key={threshold.metric} className="flex items-center justify-between rounded-lg bg-secondary/30 px-3 py-2">
                <span className="text-sm text-foreground">{threshold.metric}</span>
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs text-muted-foreground">{threshold.value}</span>
                  <span className={`font-mono text-xs ${threshold.status === "exceeded" ? "text-chart-3" : "text-accent"}`}>
                    {threshold.current}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Decisions */}
        <div>
          <h4 className="mb-3 text-xs font-medium text-muted-foreground">RECENT DECISIONS</h4>
          <div className="space-y-2">
            {decisions.map((decision) => (
              <div key={decision.id} className="rounded-lg bg-secondary/30 px-3 py-2">
                <p className="text-sm text-foreground">{decision.decision}</p>
                <p className="mt-1 text-xs text-muted-foreground">{decision.time}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

function WorkflowStatusIcon({ status }: { status: string }) {
  switch (status) {
    case "active":
      return <span className="h-2 w-2 animate-pulse rounded-full bg-accent" />
    case "completed":
      return <CheckCircle2 className="h-4 w-4 text-accent" />
    case "monitoring":
      return <Clock className="h-4 w-4 text-primary" />
    default:
      return <AlertTriangle className="h-4 w-4 text-chart-3" />
  }
}
