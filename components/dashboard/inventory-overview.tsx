"use client"

import { useState } from "react"
import { Check } from "lucide-react"
import { Button } from "@/components/ui/button"

type InventoryRow = {
  id: string
  item: string
  estimatedRequirement: string
  stockRemaining: string
  status: "shipment" | "noAction" | "outOfStock" | "confirmation"
}

// Estimated requirement aligns with InventoryBarChart data
const initialRows: InventoryRow[] = [
  { id: "1", item: "Cups", estimatedRequirement: "450", stockRemaining: "420", status: "noAction" },
  { id: "2", item: "Coffee Beans", estimatedRequirement: "120", stockRemaining: "100", status: "noAction" },
  { id: "3", item: "Milk", estimatedRequirement: "80", stockRemaining: "70", status: "noAction" },
  { id: "4", item: "Donuts", estimatedRequirement: "90", stockRemaining: "70", status: "noAction" },
  { id: "5", item: "Napkins", estimatedRequirement: "200", stockRemaining: "70", status: "shipment" },
]

function StatusBadge({ status }: { status: InventoryRow["status"] }) {
  const config = {
    shipment: {
      label: "Shipment enroute",
      className: "bg-orange-500/10 text-orange-500",
    },
    confirmation: {
      label: "Confirmation",
      className: "bg-success/10 text-success",
    },
    noAction: {
      label: "No Action Required",
      className: "bg-success/10 text-success",
    },
    outOfStock: {
      label: "Out of stock",
      className: "bg-destructive/10 text-destructive",
    },
  }
  const { label, className } = config[status]
  return (
    <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium ${className}`}>
      {label}
    </span>
  )
}

export function InventoryOverview() {
  const [rows, setRows] = useState<InventoryRow[]>(initialRows)
  const [orderConfirmed, setOrderConfirmed] = useState(false)

  const handleConfirmOrder = () => {
    setRows((prev) =>
      prev.map((row) => ({ ...row, status: "shipment" as const }))
    )
    setOrderConfirmed(true)
  }

  return (
    <div className="rounded-xl border border-border bg-card p-6">
      <div className="mb-4 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h3 className="text-lg font-semibold text-foreground">Inventory Overview</h3>
          <p className="text-sm text-muted-foreground">
            Current stock levels and status
          </p>
        </div>
        {!orderConfirmed && (
          <Button onClick={handleConfirmOrder} className="gap-2">
            <Check className="h-4 w-4" />
            Confirm Order
          </Button>
        )}
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border">
              <th className="pb-3 text-left text-xs font-medium text-muted-foreground">Item</th>
              <th className="pb-3 text-left text-xs font-medium text-muted-foreground">Estimated requirement (kg, L)</th>
              <th className="pb-3 text-left text-xs font-medium text-muted-foreground">Stock Remaining (kg, L)</th>
              <th className="pb-3 text-right text-xs font-medium text-muted-foreground">Status</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.id} className="border-b border-border/50 last:border-0">
                <td className="py-3 font-medium text-foreground">{row.item}</td>
                <td className="py-3 text-sm text-muted-foreground">{row.estimatedRequirement}</td>
                <td className="py-3 text-sm text-muted-foreground">{row.stockRemaining}</td>
                <td className="py-3 text-right">
                  <StatusBadge status={row.status} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
