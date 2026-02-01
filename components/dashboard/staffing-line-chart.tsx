"use client"

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
} from "recharts"
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart"

const staffData = [
  { hour: "6am", scheduled: 2, required: 2 },
  { hour: "8am", scheduled: 4, required: 4 },
  { hour: "10am", scheduled: 5, required: 5 },
  { hour: "12pm", scheduled: 8, required: 9 },
  { hour: "2pm", scheduled: 6, required: 6 },
  { hour: "4pm", scheduled: 6, required: 8 },
  { hour: "6pm", scheduled: 8, required: 10 },
  { hour: "8pm", scheduled: 5, required: 7 },
  { hour: "10pm", scheduled: 3, required: 3 },
]

const primaryColor = "oklch(0.75 0.12 75)"
const chart2Color = "oklch(0.6 0.15 145)"

export function StaffingLineChart() {
  return (
    <div className="rounded-xl border border-border bg-card p-6">
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-foreground">Employee Forecast</h2>
          <p className="text-sm text-muted-foreground">Hourly Prediction</p>
        </div>
        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-2">
            <span className="h-0.5 w-4 rounded-full bg-primary" style={{ backgroundColor: primaryColor }} />
            <span className="text-muted-foreground">Staff Scheduled</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="h-0.5 w-4 rounded-full" style={{ backgroundColor: chart2Color }} />
            <span className="text-muted-foreground">Predicted Staff Required</span>
          </div>
        </div>
      </div>

      <ChartContainer
        config={{
          scheduled: { label: "Staff Scheduled", color: primaryColor },
          required: { label: "Predicted Staff Required", color: chart2Color },
        }}
        className="h-[300px]"
      >
        <LineChart
          data={staffData}
          margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
          <XAxis
            dataKey="hour"
            tick={{ fill: "#94a3b8", fontSize: 12 }}
            axisLine={{ stroke: "rgba(255,255,255,0.1)" }}
            tickLine={false}
          />
          <YAxis
            domain={[0, 15]}
            tick={{ fill: "#94a3b8", fontSize: 12 }}
            axisLine={{ stroke: "rgba(255,255,255,0.1)" }}
            tickLine={false}
            label={{
              value: "# of employees",
              angle: -90,
              position: "insideLeft",
              fill: "#94a3b8",
              fontSize: 12,
            }}
          />
          <ChartTooltip content={<ChartTooltipContent />} />
          <Line
            type="monotone"
            dataKey="scheduled"
            stroke={primaryColor}
            strokeWidth={2}
            dot={{ r: 4, fill: primaryColor }}
            activeDot={{ r: 6, fill: primaryColor }}
          />
          <Line
            type="monotone"
            dataKey="required"
            stroke={chart2Color}
            strokeWidth={2}
            strokeDasharray="5 5"
            dot={{ r: 4, fill: chart2Color }}
            activeDot={{ r: 6, fill: chart2Color }}
          />
        </LineChart>
      </ChartContainer>
    </div>
  )
}
