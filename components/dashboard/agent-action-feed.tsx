"use client"

import { useState, useEffect } from "react"
import { Brain, Bot, Wrench } from "lucide-react"

type AgentAction = {
  id: string
  agent: "predictor" | "orchestrator" | "operator"
  message: string
  timestamp: string
}

const initialActions: AgentAction[] = [
  {
    id: "1",
    agent: "predictor",
    message: "Forecasted 22% increase in foot traffic (4-8pm)",
    timestamp: "2 min ago",
  },
  {
    id: "2",
    agent: "orchestrator",
    message: "Triggered staffing optimization workflow",
    timestamp: "2 min ago",
  },
  {
    id: "3",
    agent: "operator",
    message: "Added 1 barista shift (4-9pm)",
    timestamp: "1 min ago",
  },
  {
    id: "4",
    agent: "operator",
    message: "Sent SMS to on-call staff",
    timestamp: "1 min ago",
  },
  {
    id: "5",
    agent: "operator",
    message: "Placed milk order (+15%)",
    timestamp: "Just now",
  },
]

const agentConfig = {
  predictor: {
    icon: Bot,
    label: "Predictor",
    color: "text-primary bg-primary/10",
  },
  orchestrator: {
    icon: Brain,
    label: "Orchestrator",
    color: "text-chart-3 bg-chart-3/10",
  },
  operator: {
    icon: Wrench,
    label: "Operator",
    color: "text-accent bg-accent/10",
  },
}

export function AgentActionFeed() {
  const [actions, setActions] = useState(initialActions)
  const [isThinking, setIsThinking] = useState(false)

  // Simulate agent thinking periodically
  useEffect(() => {
    const interval = setInterval(() => {
      setIsThinking(true)
      setTimeout(() => setIsThinking(false), 2000)
    }, 10000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="rounded-xl border border-border bg-card p-6">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-foreground">Agent Activity</h3>
        {isThinking ? (
          <span className="flex items-center gap-1.5 text-xs text-chart-3">
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-chart-3" />
            Thinking...
          </span>
        ) : (
          <span className="flex items-center gap-1.5 text-xs text-accent">
            <span className="h-1.5 w-1.5 rounded-full bg-accent" />
            Active
          </span>
        )}
      </div>

      <div className="max-h-[320px] space-y-3 overflow-y-auto">
        {actions.map((action, index) => {
          const config = agentConfig[action.agent]
          const Icon = config.icon
          return (
            <div
              key={action.id}
              className="flex items-start gap-3 rounded-lg bg-secondary/30 p-3 transition-all animate-in fade-in slide-in-from-top-1"
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <div className={`flex h-8 w-8 items-center justify-center rounded-md ${config.color}`}>
                <Icon className="h-4 w-4" />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-medium text-foreground">{config.label} Agent</span>
                  <span className="text-xs text-muted-foreground">{action.timestamp}</span>
                </div>
                <p className="mt-0.5 text-sm text-muted-foreground">{action.message}</p>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
