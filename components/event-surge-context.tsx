"use client"

import React, {
  createContext,
  useContext,
  useState,
  useCallback,
  type ReactNode,
} from "react"

/**
 * Hardcoded event surge scenario: foot traffic DROP (e.g. storm, construction).
 * Adjusts schedules and inventory orders accordingly.
 */
export type SurgeScenario = {
  active: boolean
  footTrafficDropPercent: number
  reason: string
  staffingChanges: { name: string; action: string; detail: string }[]
  inventoryChanges: { item: string; adjustment: string; detail: string }[]
  operatorActions: { type: string; action: string; time: string }[]
}

const DROP_SCENARIO: SurgeScenario = {
  active: true,
  footTrafficDropPercent: -28,
  reason: "Severe weather / construction closure — traffic expected to drop significantly",
  staffingChanges: [
    { name: "Alex Kim", action: "removed", detail: "4–9pm shift cancelled (low demand)" },
    { name: "Jordan Lee", action: "shortened", detail: "5–10pm → 5–7pm (reduced hours)" },
    { name: "Emily Rodriguez", action: "unchanged", detail: "11am–7pm (core coverage)" },
  ],
  inventoryChanges: [
    { item: "Milk", adjustment: "-20%", detail: "Order reduced from +15% to -5%" },
    { item: "Donuts", adjustment: "-30%", detail: "Fewer units for slower day" },
    { item: "Coffee Beans", adjustment: "-15%", detail: "Delay shipment — current stock sufficient" },
    { item: "Cups", adjustment: "no change", detail: "Stock adequate for reduced volume" },
  ],
  operatorActions: [
    { type: "schedule", action: "Removed shift: Alex Kim (4-9pm)", time: "Just now" },
    { type: "schedule", action: "Shortened shift: Jordan Lee (5-7pm)", time: "Just now" },
    { type: "message", action: "SMS sent to Alex Kim (shift cancelled)", time: "Just now" },
    { type: "order", action: "Milk order -5% (reduced from +15%)", time: "Just now" },
    { type: "order", action: "Donuts order -30%", time: "Just now" },
  ],
}

type EventSurgeContextValue = {
  scenario: SurgeScenario | null
  isSurgeActive: boolean
  triggerSurge: () => void
  resetSurge: () => void
}

const EventSurgeContext = createContext<EventSurgeContextValue>({
  scenario: null,
  isSurgeActive: false,
  triggerSurge: () => {},
  resetSurge: () => {},
})

export function EventSurgeProvider({ children }: { children: ReactNode }) {
  const [scenario, setScenario] = useState<SurgeScenario | null>(null)

  const triggerSurge = useCallback(() => {
    setScenario(DROP_SCENARIO)
  }, [])

  const resetSurge = useCallback(() => {
    setScenario(null)
  }, [])

  return (
    <EventSurgeContext.Provider
      value={{
        scenario,
        isSurgeActive: scenario !== null,
        triggerSurge,
        resetSurge,
      }}
    >
      {children}
    </EventSurgeContext.Provider>
  )
}

export function useEventSurge() {
  return useContext(EventSurgeContext)
}
