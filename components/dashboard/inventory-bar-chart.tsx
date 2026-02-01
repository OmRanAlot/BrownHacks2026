"use client"

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
} from "recharts"
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart"
import { useEventSurge } from "@/components/event-surge-context"

// Estimated Requirement > In Stock for all; Napkins In Stock = 0
const baseInventoryData = [
  { item: "Cups", estimated: 450, inStock: 320 },
  { item: "Coffee Beans", estimated: 120, inStock: 85 },
  { item: "Milk", estimated: 80, inStock: 55 },
  { item: "Donuts", estimated: 90, inStock: 60 },
  { item: "Napkins", estimated: 200, inStock: 0 },
]

// Surge: decreased potential demand (Cups −20%, Coffee −15%, Milk −5%, Donuts −30%, Napkins no change)
const surgeInventoryData = [
  { item: "Cups", estimated: 360, inStock: 320 },
  { item: "Coffee Beans", estimated: 102, inStock: 85 },
  { item: "Milk", estimated: 76, inStock: 55 },
  { item: "Donuts", estimated: 63, inStock: 60 },
  { item: "Napkins", estimated: 200, inStock: 0 },
]

// Estimated requirement = green, In stock = orange
const estimatedColor = "oklch(0.6 0.15 145)"
const inStockColor = "oklch(0.7 0.15 65)"

export function InventoryBarChart() {
  const { isSurgeActive } = useEventSurge()
  const inventoryData = isSurgeActive ? surgeInventoryData : baseInventoryData

  return (
    <div className="rounded-xl border border-border bg-card p-6">
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-foreground">Inventory Levels</h2>
          <p className="text-sm text-muted-foreground">
            {isSurgeActive ? "Reduced potential (event surge) vs In Stock" : "Estimated Requirement vs In Stock"}
          </p>
        </div>
        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-2">
            <span className="h-2.5 w-3 rounded-sm" style={{ backgroundColor: estimatedColor }} />
            <span className="text-muted-foreground">Estimated Requirement</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="h-2.5 w-3 rounded-sm" style={{ backgroundColor: inStockColor }} />
            <span className="text-muted-foreground">In Stock</span>
          </div>
        </div>
      </div>

      <ChartContainer
        config={{
          estimated: { label: "Estimated Requirement", color: estimatedColor },
          inStock: { label: "In Stock", color: inStockColor },
        }}
        className="h-[300px]"
      >
        <BarChart
          data={inventoryData}
          margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
          <XAxis
            dataKey="item"
            tick={{ fill: "#94a3b8", fontSize: 12 }}
            axisLine={{ stroke: "rgba(255,255,255,0.1)" }}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: "#94a3b8", fontSize: 12 }}
            axisLine={{ stroke: "rgba(255,255,255,0.1)" }}
            tickLine={false}
            label={{
              value: "Quantity",
              angle: -90,
              position: "insideLeft",
              fill: "#94a3b8",
              fontSize: 12,
            }}
          />
          <ChartTooltip content={<ChartTooltipContent />} />
          <Bar dataKey="estimated" fill={estimatedColor} name="Estimated Requirement" radius={[2, 2, 0, 0]} />
          <Bar dataKey="inStock" fill={inStockColor} name="In Stock" radius={[2, 2, 0, 0]} />
        </BarChart>
      </ChartContainer>
    </div>
  )
}
