"use client"

import { useState, useMemo } from "react"
import { Check, Clock, UserPlus, Printer, AlertTriangle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useEventSurge } from "@/components/event-surge-context"

type StaffMember = {
  id: string
  name: string
  role: string
  shift: string
  status: "confirmed" | "pending" | "new"
}

const initialStaff: StaffMember[] = [
  { id: "1", name: "Sarah Chen", role: "Barista", shift: "7am - 3pm", status: "confirmed" },
  { id: "2", name: "Marcus Johnson", role: "Barista", shift: "10am - 6pm", status: "confirmed" },
  { id: "3", name: "Emily Rodriguez", role: "Cashier", shift: "11am - 7pm", status: "confirmed" },
  { id: "4", name: "Alex Kim", role: "Barista", shift: "4pm - 9pm", status: "new" },
  { id: "5", name: "Jordan Lee", role: "Support", shift: "5pm - 10pm", status: "pending" },
]

export function StaffingOverview({ showPrintButton = false }: { showPrintButton?: boolean }) {
  const { isSurgeActive } = useEventSurge()
  const [staff, setStaff] = useState(initialStaff)

  // When surge is active: remove Alex Kim, shorten Jordan Lee
  const displayStaff = useMemo(() => {
    if (!isSurgeActive) return staff
    return staff
      .filter((s) => s.name !== "Alex Kim")
      .map((s) =>
        s.name === "Jordan Lee" ? { ...s, shift: "5pm - 7pm", status: "confirmed" as const } : s
      )
  }, [staff, isSurgeActive])
  const [approved, setApproved] = useState(false)

  const handleApprove = () => {
    setStaff((prev) =>
      prev.map((member) => ({
        ...member,
        status: "confirmed" as const,
      }))
    )
    setApproved(true)
  }

  const pendingCount = displayStaff.filter((s) => s.status === "pending" || s.status === "new").length

  return (
    <div className="rounded-xl border border-border bg-card p-6">
      {isSurgeActive && (
        <div className="mb-4 flex items-center gap-2 rounded-lg bg-amber-500/10 px-3 py-2 text-sm text-amber-600 dark:text-amber-400">
          <AlertTriangle className="h-4 w-4 shrink-0" />
          <span>Event surge: Alex Kim removed, Jordan Lee shortened to 5–7pm (low demand)</span>
        </div>
      )}
      <div className="mb-4 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h3 className="text-lg font-semibold text-foreground">Staffing Overview</h3>
          <p className="text-sm text-muted-foreground">
            {pendingCount > 0 && !approved
              ? `${pendingCount} changes pending approval`
              : "All shifts confirmed"}
          </p>
        </div>
        {pendingCount > 0 && !approved && (
          <Button onClick={handleApprove} className="gap-2">
            <Check className="h-4 w-4" />
            Approve Changes
          </Button>
        )}
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border">
              <th className="pb-3 text-left text-xs font-medium text-muted-foreground">Employee</th>
              <th className="pb-3 text-left text-xs font-medium text-muted-foreground">Role</th>
              <th className="pb-3 text-left text-xs font-medium text-muted-foreground">Shift</th>
              <th className="pb-3 text-right text-xs font-medium text-muted-foreground">Status</th>
            </tr>
          </thead>
          <tbody>
            {displayStaff.map((member) => (
              <tr key={member.id} className="border-b border-border/50 last:border-0">
                <td className="py-3">
                  <div className="flex items-center gap-3">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-secondary text-sm font-medium text-foreground">
                      {member.name.split(" ").map((n) => n[0]).join("")}
                    </div>
                    <span className="font-medium text-foreground">{member.name}</span>
                  </div>
                </td>
                <td className="py-3 text-sm text-muted-foreground">{member.role}</td>
                <td className="py-3 text-sm text-foreground">{member.shift}</td>
                <td className="py-3 text-right">
                  <StatusBadge status={member.status} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {showPrintButton && (
        <div className="mt-4 flex justify-end border-t border-border pt-4">
          <Button variant="outline" size="sm" className="gap-2">
            <Printer className="h-4 w-4" />
            Print Schedule
          </Button>
        </div>
      )}
    </div>
  )
}

function StatusBadge({ status }: { status: StaffMember["status"] }) {
  const config = {
    confirmed: {
      icon: Check,
      label: "Confirmed",
      className: "bg-success/10 text-success",
    },
    pending: {
      icon: Clock,
      label: "Pending",
      className: "bg-chart-3/10 text-chart-3",
    },
    new: {
      icon: UserPlus,
      label: "New",
      className: "bg-primary/10 text-primary",
    },
  }

  const { icon: Icon, label, className } = config[status]

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium ${className}`}>
      <Icon className="h-3 w-3" />
      {label}
    </span>
  )
}
