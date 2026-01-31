"use client"

import React from "react"

import { Cloud, Music, MapPin, Construction } from "lucide-react"

export function CitySignalsPanel() {
  return (
    <div className="rounded-xl border border-border bg-card p-6">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-foreground">City Signals</h3>
        <span className="flex items-center gap-1.5 text-xs text-accent">
          <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-accent" />
          Live
        </span>
      </div>

      <div className="space-y-4">
        <SignalItem
          icon={<Cloud className="h-4 w-4" />}
          label="Weather"
          value="Clear · 72°F"
          detail="No rain expected"
          status="positive"
        />
        <SignalItem
          icon={<Music className="h-4 w-4" />}
          label="Events"
          value="Live concert"
          detail="0.4 miles away · 7pm"
          status="alert"
        />
        <SignalItem
          icon={<MapPin className="h-4 w-4" />}
          label="Maps Activity"
          value="Above average"
          detail="Area popularity +23%"
          status="positive"
        />
        <SignalItem
          icon={<Construction className="h-4 w-4" />}
          label="Disruptions"
          value="None detected"
          detail="All routes clear"
          status="neutral"
        />
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
      <div className={`flex h-8 w-8 items-center justify-center rounded-md ${statusColors[status]}`}>
        {icon}
      </div>
      <div className="flex-1">
        <p className="text-xs text-muted-foreground">{label}</p>
        <p className="font-medium text-foreground">{value}</p>
        <p className="text-xs text-muted-foreground">{detail}</p>
      </div>
    </div>
  )
}
