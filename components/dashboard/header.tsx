"use client"

import Link from "next/link"
import { useState } from "react"
import { MapPin, Calendar, ChevronDown, Activity } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

const locations = [
  "Williamsburg Café",
  "SoHo Coffee Shop",
  "Brooklyn Heights Bistro",
]

const dateOptions = ["Today", "Tomorrow", "This Week"]

export function DashboardHeader() {
  const [selectedLocation, setSelectedLocation] = useState(locations[0])
  const [selectedDate, setSelectedDate] = useState(dateOptions[0])

  return (
    <header className="sticky top-0 z-50 border-b border-border bg-background/95 backdrop-blur-sm">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <div className="flex items-center gap-6">
          <Link href="/" className="font-serif text-lg font-bold tracking-wide text-foreground">
            CITYFOOTFALL
          </Link>

          <div className="flex items-center gap-3">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" className="gap-2 bg-transparent">
                  <MapPin className="h-4 w-4 text-primary" />
                  <span className="hidden sm:inline">{selectedLocation}</span>
                  <ChevronDown className="h-4 w-4 text-muted-foreground" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="start">
                {locations.map((location) => (
                  <DropdownMenuItem
                    key={location}
                    onClick={() => setSelectedLocation(location)}
                    className={selectedLocation === location ? "bg-secondary" : ""}
                  >
                    {location}
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" className="gap-2 bg-transparent">
                  <Calendar className="h-4 w-4 text-primary" />
                  <span>{selectedDate}</span>
                  <ChevronDown className="h-4 w-4 text-muted-foreground" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="start">
                {dateOptions.map((date) => (
                  <DropdownMenuItem
                    key={date}
                    onClick={() => setSelectedDate(date)}
                    className={selectedDate === date ? "bg-secondary" : ""}
                  >
                    {date}
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="hidden items-center gap-2 rounded-sm border border-border px-3 py-1.5 md:flex">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-chart-2 opacity-75" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-chart-2" />
            </span>
            <span className="text-xs font-medium text-chart-2">Agents Active</span>
          </div>
          <Link href="/agents">
            <Button variant="ghost" size="sm" className="gap-2">
              <Activity className="h-4 w-4" />
              <span className="hidden sm:inline">Agent Activity</span>
            </Button>
          </Link>
        </div>
      </div>
    </header>
  )
}
