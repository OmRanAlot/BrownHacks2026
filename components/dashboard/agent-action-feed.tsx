"use client"

import { Cloud, MapPin, Train, Brain, Wrench } from "lucide-react"
import { useFootTrafficForecast } from "@/components/dashboard/foot-traffic-forecast-context"
import type { FootTrafficSignal } from "@/lib/foot-traffic-forecast"

type AgentAction = {
  id: string
  agent: "weather" | "traffic" | "transit" | "orchestrator" | "operator"
  label: string
  message: string
}

const SOURCE_TO_AGENT: Record<string, { agent: AgentAction["agent"]; label: string; icon: typeof Cloud }> = {
  weather_event: { agent: "weather", label: "Weather", icon: Cloud },
  google_traffic: { agent: "traffic", label: "Traffic", icon: MapPin },
  mta_subway: { agent: "transit", label: "Transit", icon: Train },
}

const agentConfig: Record<AgentAction["agent"], { icon: typeof Cloud; color: string }> = {
  weather: { icon: Cloud, color: "text-sky-500 bg-sky-500/10" },
  traffic: { icon: MapPin, color: "text-amber-500 bg-amber-500/10" },
  transit: { icon: Train, color: "text-emerald-500 bg-emerald-500/10" },
  orchestrator: { icon: Brain, color: "text-chart-3 bg-chart-3/10" },
  operator: { icon: Wrench, color: "text-accent bg-accent/10" },
}

function signalsToActions(
  signals: FootTrafficSignal[],
  finalSummary: string[],
  expectedExtra: number,
  variant: "overview" | "staffing" | "inventory"
): AgentAction[] {
  const actions: AgentAction[] = []

  // Three agent signals (ordered: weather, traffic, transit)
  const order = ["weather_event", "google_traffic", "mta_subway"]
  for (let i = 0; i < order.length; i++) {
    const s = signals.find((sig) => sig.source === order[i])
    if (!s) continue
    const meta = SOURCE_TO_AGENT[s.source]
    if (!meta) continue
    const extra = s.extra_customers_per_hour
    const sign = extra >= 0 ? "+" : ""
    const msg = s.explanation
      ? `${sign}${extra.toFixed(1)} extra/hr. ${s.explanation}`
      : `${sign}${extra.toFixed(1)} extra customers/hr (${(s.confidence * 100).toFixed(0)}% confidence)`
    actions.push({
      id: `signal-${s.source}`,
      agent: meta.agent,
      label: meta.label,
      message: msg,
    })
  }

  // Orchestrator: combined forecast
  const summary = finalSummary?.[0] ?? "Combined all signals into unified forecast."
  actions.push({
    id: "orchestrator",
    agent: "orchestrator",
    label: "Orchestrator",
    message: summary,
  })

  // Variant-specific derived suggestion from combined forecast
  if (variant === "staffing" || variant === "inventory") {
    if (variant === "staffing") {
      const shift =
        expectedExtra > 5
          ? "Consider adding a shift for expected higher foot traffic."
          : expectedExtra < -5
            ? "Normal staffing sufficient."
            : "Monitor demand."
      actions.push({ id: "operator-staffing", agent: "operator", label: "Operator", message: shift })
    } else {
      const stock =
        expectedExtra > 5
          ? "Increase prep for expected rush."
          : "Standard inventory levels."
      actions.push({ id: "operator-inventory", agent: "operator", label: "Operator", message: stock })
    }
  }

  return actions
}

type FeedVariant = "overview" | "staffing" | "inventory"

export function AgentActionFeed({ variant = "overview" }: { variant?: FeedVariant } = {}) {
  const state = useFootTrafficForecast()

  const actions =
    state.status === "success"
      ? signalsToActions(
          state.data.signals,
          state.data.final_forecast?.summary ?? [],
          state.data.final_forecast?.expected_extra_customers_per_hour ?? 0,
          variant
        )
      : []

  return (
    <div className="rounded-xl border border-border bg-card p-6">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-foreground">Agent Activity</h3>
        <span className="flex items-center gap-1.5 text-xs text-accent">
          <span className={`h-1.5 w-1.5 rounded-full bg-accent ${state.status === "success" ? "" : "animate-pulse"}`} />
          {state.status === "loading" ? "Loading..." : state.status === "success" ? "Live" : state.status === "error" ? "Unavailable" : "Idle"}
        </span>
      </div>

      <div className="max-h-[320px] space-y-3 overflow-y-auto">
        {state.status === "loading" && (
          <div className="space-y-3">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-16 animate-pulse rounded-lg bg-secondary/30" />
            ))}
          </div>
        )}
        {state.status === "error" && (
          <p className="text-sm text-muted-foreground">Agent data unavailable. {state.error}</p>
        )}
        {state.status === "success" &&
          actions.map((action, index) => {
            const config = agentConfig[action.agent]
            const Icon = config.icon
            return (
              <div
                key={action.id}
                className="flex items-start gap-3 rounded-lg bg-secondary/30 p-3 transition-all animate-in fade-in slide-in-from-top-1"
                style={{ animationDelay: `${index * 50}ms` }}
              >
                <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-md ${config.color}`}>
                  <Icon className="h-4 w-4" />
                </div>
                <div className="min-w-0 flex-1">
                  <span className="text-xs font-medium text-foreground">{action.label} Agent</span>
                  <p className="mt-0.5 text-sm text-muted-foreground">{action.message}</p>
                </div>
              </div>
            )
          })}
      </div>
    </div>
  )
}
