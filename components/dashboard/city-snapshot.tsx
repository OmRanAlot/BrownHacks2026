"use client"

import React from "react"

import { TrendingUp, Gauge, Target, Zap } from "lucide-react"

export function CitySnapshot() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <MetricCard
        icon={<TrendingUp className="h-5 w-5" />}
        label="Predicted Foot Traffic"
        value="+18%"
        subtext="vs average"
        trend="up"
      />
      <MetricCard
        icon={<Gauge className="h-5 w-5" />}
        label="Demand Level"
        value="High"
        subtext="Above threshold"
        trend="up"
      />
      <MetricCard
        icon={<Target className="h-5 w-5" />}
        label="Prediction Confidence"
        value="0.82"
        subtext="High confidence"
        trend="neutral"
      />
      <MetricCard
        icon={<Zap className="h-5 w-5" />}
        label="Primary Driver"
        value="Concert"
        subtext="+ clear weather"
        trend="neutral"
      />
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
