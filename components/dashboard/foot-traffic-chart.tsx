"use client"

import React from "react"
import {
  Bar,
  BarChart,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts"
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart"
import { useFootTrafficForecast } from "@/components/dashboard/foot-traffic-forecast-context"

/**
 * Displays baseline vs predicted from final_forecast. Master agent is single source of truth.
 * No reshaping—we show baseline_customers_per_hour and expected_total_customers_per_hour only.
 */
const primaryColor = "#3b82f6"
const mutedColor = "#64748b"

export function FootTrafficChart() {
  const state = useFootTrafficForecast()

  if (state.status === "loading") {
    return (
      <div className="h-[300px] animate-pulse rounded-xl border border-border bg-card p-6" />
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

  const { baseline_customers_per_hour, final_forecast, business_insights } = state.data
  const baseline = baseline_customers_per_hour
  const predicted = final_forecast.expected_total_customers_per_hour

  return (
    <div className="rounded-xl border border-border bg-card p-6">
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-foreground">
            Foot Traffic Forecast
          </h2>
          <p className="text-sm text-muted-foreground">
            Baseline vs predicted customers/hr (master agent output)
          </p>
        </div>
        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-2">
            <span className="h-0.5 w-4 bg-muted-foreground" />
            <span className="text-muted-foreground">Baseline</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="h-0.5 w-4 bg-primary" />
            <span className="text-muted-foreground">Predicted</span>
          </div>
        </div>
      </div>

      <ChartContainer
        config={{
          baseline: { label: "Baseline", color: mutedColor },
          predicted: { label: "Predicted", color: primaryColor },
        }}
        className="h-[300px]"
      >
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={[{ label: "Baseline vs Predicted", baseline, predicted }]}
            margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
            <XAxis
              dataKey="label"
              tick={{ fill: "#64748b", fontSize: 12 }}
              axisLine={{ stroke: "rgba(255,255,255,0.1)" }}
              tickLine={false}
            />
            <YAxis
              tick={{ fill: "#64748b", fontSize: 12 }}
              axisLine={{ stroke: "rgba(255,255,255,0.1)" }}
              tickLine={false}
              label={{
                value: "Customers/hr",
                angle: -90,
                position: "insideLeft",
                fill: "#64748b",
                fontSize: 12,
              }}
            />
            <ChartTooltip content={<ChartTooltipContent />} />
            <Bar dataKey="baseline" fill={mutedColor} radius={[4, 4, 0, 0]} name="Baseline" />
            <Bar dataKey="predicted" fill={primaryColor} radius={[4, 4, 0, 0]} name="Predicted" />
          </BarChart>
        </ResponsiveContainer>
      </ChartContainer>

      <div className="mt-4 rounded-lg bg-secondary/50 p-4">
        <h4 className="mb-2 text-sm font-semibold text-primary">Why we forecast this</h4>
        <ul className="space-y-2 text-sm text-foreground">
          {business_insights?.length ? (
            business_insights.map((insight, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
                <span>{insight}</span>
              </li>
            ))
          ) : (
            <>
              {final_forecast.summary?.length ? (
                final_forecast.summary.map((s, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
                    <span>{s}</span>
                  </li>
                ))
              ) : (
                <li className="flex items-start gap-2">
                  <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
                  <span>
                    {final_forecast.expected_extra_customers_per_hour >= 0 ? "+" : ""}
                    {final_forecast.expected_extra_customers_per_hour} extra customers/hr vs baseline
                  </span>
                </li>
              )}
              <li className="flex items-start gap-2">
                <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
                <span>
                  {baseline} → {predicted} customers/hr
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
                <span>Confidence: {(final_forecast.confidence * 100).toFixed(0)}%</span>
              </li>
            </>
          )}
        </ul>
      </div>
    </div>
  )
}
