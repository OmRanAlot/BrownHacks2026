"use client"

import React from "react"

import { TrendingUp, Gauge, Target, Zap } from "lucide-react"
import { useFootTrafficForecast } from "@/components/dashboard/foot-traffic-forecast-context"

/**
 * CitySnapshot displays baseline_customers_per_hour and final_forecast from the master agent.
 * No reshaping or recomputation—single source of truth from MasterFootTrafficAgent.
 */
export function CitySnapshot() {
  const state = useFootTrafficForecast()

  if (state.status === "loading") {
    return <CitySnapshotSkeleton />
  }
  if (state.status === "error") {
    return (
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="col-span-full rounded-xl border border-destructive/50 bg-destructive/10 p-6 text-destructive">
          Forecast unavailable: {state.error}
        </div>
      </div>
    )
  }
  if (state.status !== "success") {
    return <CitySnapshotSkeleton />
  }

  const { baseline_customers_per_hour, final_forecast } = state.data
  const baseline = baseline_customers_per_hour
  const total = final_forecast.expected_total_customers_per_hour
  const extra = final_forecast.expected_extra_customers_per_hour
  const pctChange =
    baseline > 0 ? ((extra / baseline) * 100).toFixed(1) : "0"
  const trend: "up" | "down" | "neutral" =
    extra > 0 ? "up" : extra < 0 ? "down" : "neutral"
  const demandLevel =
    extra > baseline * 0.2 ? "High" : extra > 0 ? "Moderate" : "Low"

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <MetricCard
        icon={<TrendingUp className="h-5 w-5" />}
        label="Predicted Foot Traffic"
        value={extra >= 0 ? `+${pctChange}%` : `${pctChange}%`}
        subtext="vs. Baseline"
        trend={trend}
      />
      <MetricCard
        icon={<Gauge className="h-5 w-5" />}
        label="Demand Level"
        value={demandLevel}
        subtext="Above threshold"
        trend={extra > 0 ? "up" : "neutral"}
      />
      <MetricCard
        icon={<Target className="h-5 w-5" />}
        label="Prediction Confidence"
        value={String(final_forecast.confidence)}
        subtext="High confidence"
        trend="neutral"
      />
      <MetricCard
        icon={<Zap className="h-5 w-5" />}
        label="Primary Driver"
        value={
          final_forecast.summary?.[0]?.replace(/^\[[^\]]+\]\s*/, "") ?? "N/A"
        }
        subtext={`Baseline ${baseline} → ${total} customers/hr`}
        trend="neutral"
      />
    </div>
  )
}

function CitySnapshotSkeleton() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {[1, 2, 3, 4].map((i) => (
        <div
          key={i}
          className="h-24 animate-pulse rounded-xl border border-border bg-card"
        />
      ))}
    </div>
  )
}

function MetricCard({
  icon,
  label,
  value,
  subtext,
  trend,
}: {
  icon: React.ReactNode
  label: string
  value: string
  subtext: string
  trend: "up" | "down" | "neutral"
}) {
  const trendColors = {
    up: "text-accent",
    down: "text-destructive",
    neutral: "text-primary",
  }

  return (
    <div className="rounded-xl border border-border bg-card p-6">
      <div className="mb-4 flex items-center justify-between">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-secondary text-primary">
          {icon}
        </div>
        <span className="text-xs text-muted-foreground">{label}</span>
      </div>
      <div className="flex items-end justify-between">
        <span className={`text-3xl font-bold ${trendColors[trend]}`}>{value}</span>
        <span className="text-sm text-muted-foreground">{subtext}</span>
      </div>
    </div>
  )
}
