"use client"

import React from "react"

import { Cloud, MapPin, Train, AlertCircle } from "lucide-react"
import { useFootTrafficForecast } from "@/components/dashboard/foot-traffic-forecast-context"

/**
 * CitySignalsPanel displays signals from the master agent payload.
 * Each signal: source, extra_customers_per_hour, confidence, explanation.
 * Sub-agents are never called from UI—single source of truth.
 */
const SOURCE_ICONS: Record<string, React.ReactNode> = {
  weather_event: <Cloud className="h-4 w-4" />,
  google_traffic: <MapPin className="h-4 w-4" />,
  mta_subway: <Train className="h-4 w-4" />,
}

function getStatus(extra: number): "positive" | "alert" | "neutral" {
  if (extra > 0) return "positive"
  if (extra < 0) return "alert"
  return "neutral"
}

export function CitySignalsPanel() {
  const state = useFootTrafficForecast()

  if (state.status === "loading") {
    return (
      <div className="h-64 animate-pulse rounded-xl border border-border bg-card p-6" />
    )
  }
  if (state.status === "error") {
    return (
      <div className="rounded-xl border border-border bg-card p-6">
        <p className="text-destructive">Forecast unavailable: {state.error}</p>
      </div>
    )
  }
  if (state.status !== "success") {
    return null
  }

  const { signals } = state.data

  return (
    <div className="rounded-xl border border-border bg-card p-6">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-foreground">City Signals</h3>
        <span className="flex items-center gap-1.5 text-xs text-accent">
          <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-accent" />
          Live (from master agent)
        </span>
      </div>

      <div className="space-y-4">
        {signals.map((s) => (
          <SignalItem
            key={s.source}
            icon={SOURCE_ICONS[s.source] ?? <AlertCircle className="h-4 w-4" />}
            label={s.source.replace(/_/g, " ")}
            value={`${s.extra_customers_per_hour >= 0 ? "+" : ""}${s.extra_customers_per_hour.toFixed(1)} extra/hr`}
            detail={s.explanation}
            status={getStatus(s.extra_customers_per_hour)}
          />
        ))}
      </div>
    </div>
  )
}

function SignalItem({
  icon,
  label,
  value,
  detail,
  status,
}: {
  icon: React.ReactNode
  label: string
  value: string
  detail: string
  status: "positive" | "alert" | "neutral"
}) {
  const statusColors = {
    positive: "bg-accent/10 text-accent",
    alert: "bg-chart-3/10 text-chart-3",
    neutral: "bg-secondary text-muted-foreground",
  }

  return (
    <div className="flex items-start gap-3 rounded-lg bg-secondary/30 p-3">
      <div
        className={`flex h-8 w-8 items-center justify-center rounded-md ${statusColors[status]}`}
      >
        {icon}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-xs text-muted-foreground capitalize">{label}</p>
        <p className="font-medium text-foreground truncate">{value}</p>
        <p className="text-xs text-muted-foreground line-clamp-2">{detail}</p>
      </div>
    </div>
  )
}
