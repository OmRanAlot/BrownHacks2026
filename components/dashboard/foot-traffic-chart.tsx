"use client"

import {
  Area,
  AreaChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts"
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart"

// Mock hourly foot traffic data
const trafficData = [
  { hour: "6am", baseline: 20, predicted: 22, low: 18, high: 26 },
  { hour: "7am", baseline: 35, predicted: 38, low: 32, high: 44 },
  { hour: "8am", baseline: 55, predicted: 58, low: 50, high: 66 },
  { hour: "9am", baseline: 65, predicted: 62, low: 55, high: 69 },
  { hour: "10am", baseline: 50, predicted: 52, low: 45, high: 59 },
  { hour: "11am", baseline: 55, predicted: 58, low: 50, high: 66 },
  { hour: "12pm", baseline: 75, predicted: 82, low: 72, high: 92 },
  { hour: "1pm", baseline: 80, predicted: 85, low: 75, high: 95 },
  { hour: "2pm", baseline: 65, predicted: 68, low: 60, high: 76 },
  { hour: "3pm", baseline: 55, predicted: 60, low: 52, high: 68 },
  { hour: "4pm", baseline: 60, predicted: 78, low: 68, high: 88 },
  { hour: "5pm", baseline: 70, predicted: 92, low: 82, high: 102 },
  { hour: "6pm", baseline: 75, predicted: 98, low: 88, high: 108 },
  { hour: "7pm", baseline: 65, predicted: 95, low: 85, high: 105 },
  { hour: "8pm", baseline: 55, predicted: 88, low: 78, high: 98 },
  { hour: "9pm", baseline: 40, predicted: 65, low: 55, high: 75 },
  { hour: "10pm", baseline: 25, predicted: 35, low: 28, high: 42 },
]

// Compute colors for chart - not using CSS variables directly
const primaryColor = "#3b82f6" // electric blue
const mutedColor = "#64748b" // muted gray
const confidenceColor = "rgba(59, 130, 246, 0.15)" // transparent blue

export function FootTrafficChart() {
  return (
    <div className="rounded-xl border border-border bg-card p-6">
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-foreground">Foot Traffic Forecast</h2>
          <p className="text-sm text-muted-foreground">Hourly predictions with confidence band</p>
        </div>
        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-2">
            <span className="h-0.5 w-4 bg-muted-foreground" />
            <span className="text-muted-foreground">Historical Baseline</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="h-0.5 w-4 bg-primary" />
            <span className="text-muted-foreground">Predicted Traffic</span>
          </div>
        </div>
      </div>

      <ChartContainer
        config={{
          baseline: {
            label: "Historical Baseline",
            color: mutedColor,
          },
          predicted: {
            label: "Predicted Traffic",
            color: primaryColor,
          },
        }}
        className="h-[300px]"
      >
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={trafficData}
            margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
          >
            <defs>
              <linearGradient id="confidenceGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={primaryColor} stopOpacity={0.2} />
                <stop offset="95%" stopColor={primaryColor} stopOpacity={0.02} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
            <XAxis
              dataKey="hour"
              tick={{ fill: "#64748b", fontSize: 12 }}
              axisLine={{ stroke: "rgba(255,255,255,0.1)" }}
              tickLine={false}
            />
            <YAxis
              tick={{ fill: "#64748b", fontSize: 12 }}
              axisLine={{ stroke: "rgba(255,255,255,0.1)" }}
              tickLine={false}
              label={{
                value: "Traffic Index",
                angle: -90,
                position: "insideLeft",
                fill: "#64748b",
                fontSize: 12,
              }}
            />
            <ChartTooltip content={<ChartTooltipContent />} />
            <ReferenceLine y={80} stroke="#f59e0b" strokeDasharray="5 5" label={{ value: "Surge Threshold", fill: "#f59e0b", fontSize: 10 }} />
            {/* Confidence band */}
            <Area
              type="monotone"
              dataKey="high"
              stroke="transparent"
              fill={confidenceColor}
              fillOpacity={1}
            />
            <Area
              type="monotone"
              dataKey="low"
              stroke="transparent"
              fill="#0f172a"
              fillOpacity={1}
            />
            {/* Baseline line */}
            <Line
              type="monotone"
              dataKey="baseline"
              stroke={mutedColor}
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={false}
            />
            {/* Predicted line */}
            <Line
              type="monotone"
              dataKey="predicted"
              stroke={primaryColor}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 6, fill: primaryColor }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </ChartContainer>

      <div className="mt-4 rounded-lg bg-secondary/50 p-4">
        <p className="text-sm text-foreground">
          <span className="mr-2 font-semibold text-primary">Insight:</span>
          Evening foot traffic expected to spike between 4-8pm due to nearby concert and favorable weather conditions. Consider adding staff for this period.
        </p>
      </div>
    </div>
  )
}
