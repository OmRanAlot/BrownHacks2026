"use client"

import * as React from "react"
import { ChevronLeftIcon, ChevronRightIcon } from "lucide-react"
import { DayButton, DayPicker, getDefaultClassNames } from "react-day-picker"
import { format } from "date-fns"

import { cn } from "@/lib/utils"
import { buttonVariants } from "@/components/ui/button"

/** Day-of-week based busy level: Sun=Not busy, Mon-Thu=Slightly Busy, Fri-Sat=Busy */
function getBusinessLevel(date: Date): "green" | "yellow" | "red" {
  const dayOfWeek = date.getDay() // 0=Sun, 1=Mon, ..., 6=Sat
  if (dayOfWeek === 0) return "green"   // Sunday = Not busy
  if (dayOfWeek >= 1 && dayOfWeek <= 4) return "yellow"  // Mon-Thu = Slightly Busy
  return "red"  // Fri-Sat = Busy
}

const dotColors = {
  green: "bg-emerald-600",
  yellow: "bg-amber-500",
  red: "bg-red-600",
} as const

function HeatMapDayButton({
  day,
  modifiers,
  ...props
}: React.ComponentProps<typeof DayButton>) {
  const level = getBusinessLevel(day.date)
  const dotColor = dotColors[level]

  return (
    <button
      type="button"
      data-day={day.date.toLocaleDateString()}
      className={cn(
        buttonVariants({ variant: "ghost", size: "icon" }),
        "relative aspect-square size-auto min-w-(--cell-size) rounded-md font-normal text-foreground hover:bg-accent/50",
        modifiers.outside && "opacity-50"
      )}
      {...props}
    >
      {format(day.date, "d")}
      <span
        className={cn(
          "absolute bottom-1 right-1 h-2 w-2 rounded-full",
          dotColor
        )}
        aria-hidden
      />
    </button>
  )
}

interface BusinessCalendarProps {
  className?: string
}

export function BusinessCalendar({ className }: BusinessCalendarProps) {
  const defaultClassNames = getDefaultClassNames()
  const january2026 = new Date(2026, 0, 1)

  return (
    <div className={cn("w-full max-w-md rounded-sm border border-border bg-card p-4", className)}>
      <div className="mb-4 flex items-center justify-between">
        <span className="font-mono text-xs tracking-widest text-muted-foreground">
          January 2026
        </span>
        <div className="flex items-center gap-3 text-xs text-muted-foreground">
          <span className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-emerald-600" />
            Not busy
          </span>
          <span className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-amber-500" />
            Slightly Busy
          </span>
          <span className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-red-600" />
            Busy
          </span>
        </div>
      </div>

      <DayPicker
        defaultMonth={january2026}
        month={january2026}
        onMonthChange={() => {}}
        showOutsideDays
        className="group/calendar p-0 [--cell-size:2.25rem]"
        classNames={{
          root: cn("w-fit", defaultClassNames.root),
          months: "flex flex-col",
          month: "flex flex-col gap-2",
          month_caption: "flex justify-center font-medium text-sm",
          nav: "hidden",
          button_previous: "hidden",
          button_next: "hidden",
          weekdays: "flex",
          weekday: "w-[--cell-size] text-center text-[0.7rem] text-muted-foreground",
          week: "flex w-full mt-1",
          day: "relative p-0 text-center",
          hidden: "invisible",
        }}
        formatters={{
          formatCaption: () => "January 2026",
        }}
        components={{
          Chevron: ({ orientation, ...chevronProps }) =>
            orientation === "left" ? (
              <ChevronLeftIcon className="size-4" {...chevronProps} />
            ) : (
              <ChevronRightIcon className="size-4" {...chevronProps} />
            ),
          DayButton: HeatMapDayButton,
        }}
      />
    </div>
  )
}
