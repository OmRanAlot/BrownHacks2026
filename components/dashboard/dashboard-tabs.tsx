"use client"

<<<<<<< HEAD
import { useState, useEffect } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Skeleton } from "@/components/ui/skeleton"
=======
import { useState } from "react"
import { AlertTriangle, X } from "lucide-react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
>>>>>>> 5273387086590736295aa2f16393c6beabd7e6df
import { CitySnapshot } from "@/components/dashboard/city-snapshot"
import { FootTrafficChart } from "@/components/dashboard/foot-traffic-chart"
import { StaffingLineChart } from "@/components/dashboard/staffing-line-chart"
import { InventoryBarChart } from "@/components/dashboard/inventory-bar-chart"
import { CitySignalsPanel } from "@/components/dashboard/city-signals-panel"
import { AgentActionFeed } from "@/components/dashboard/agent-action-feed"
import { StaffingOverview } from "@/components/dashboard/staffing-overview"
<<<<<<< HEAD
import { InventoryOverview as InventoryOverviewDemo } from "@/components/dashboard/inventory-overview-demo"
import { InventoryOverview as InventoryOverviewStandard } from "@/components/dashboard/inventory-overview"
import { BusynessCard } from "@/components/dashboard/busyness-card"
=======
import { InventoryOverview } from "@/components/dashboard/inventory-overview"
import { useEventSurge } from "@/components/event-surge-context"
>>>>>>> 5273387086590736295aa2f16393c6beabd7e6df
import { cn } from "@/lib/utils"

const tabs = [
  { id: "overview", label: "Overview" },
  { id: "staffing", label: "Staffing" },
  { id: "inventory", label: "Inventory" },
] as const

/** Animated ellipsis: ., .., ... then repeat. */
function LoadingDots() {
  const [count, setCount] = useState(0)
  useEffect(() => {
    const id = setInterval(() => setCount((c) => (c + 1) % 3), 400)
    return () => clearInterval(id)
  }, [])
  return <span className="inline-block w-[1.25em] text-left">{".".repeat(count + 1)}</span>
}

export function DashboardTabs() {
  const [activeTab, setActiveTab] = useState("overview")
<<<<<<< HEAD
  const [overviewLoading, setOverviewLoading] = useState(true)
  const [useDemoInventory, setUseDemoInventory] = useState(true)
  const [inventoryRefreshing, setInventoryRefreshing] = useState(false)

  useEffect(() => {
    if (activeTab !== "overview") return
    if (!overviewLoading) return
    const t = setTimeout(() => setOverviewLoading(false), 5000)
    return () => clearTimeout(t)
  }, [activeTab, overviewLoading])

  useEffect(() => {
    if (activeTab !== "inventory") return
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key !== "/") return
      const target = e.target as HTMLElement
      if (target.closest("input") || target.closest("textarea") || target.closest("[contenteditable]")) return
      if (inventoryRefreshing) return
      e.preventDefault()
      setInventoryRefreshing(true)
      setTimeout(() => {
        setUseDemoInventory((prev) => !prev)
        setInventoryRefreshing(false)
      }, 2000)
    }
    window.addEventListener("keydown", onKeyDown)
    return () => window.removeEventListener("keydown", onKeyDown)
  }, [activeTab, inventoryRefreshing])

  const showOverviewLoadingMessage = activeTab === "overview" && overviewLoading
  const showInventoryRefreshingMessage = activeTab === "inventory" && inventoryRefreshing
=======
  const { isSurgeActive, scenario, resetSurge } = useEventSurge()
>>>>>>> 5273387086590736295aa2f16393c6beabd7e6df

  return (
    <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v)}>
      {isSurgeActive && scenario && (
        <div className="mb-4 flex items-center justify-between gap-4 rounded-lg border border-amber-500/30 bg-amber-500/10 px-4 py-3">
          <div className="flex items-center gap-3">
            <AlertTriangle className="h-5 w-5 shrink-0 text-amber-600 dark:text-amber-400" />
            <div>
              <p className="font-medium text-amber-800 dark:text-amber-200">
                Simulated event surge: {scenario.footTrafficDropPercent}% foot traffic drop
              </p>
              <p className="text-sm text-amber-700 dark:text-amber-300">{scenario.reason}</p>
            </div>
          </div>
          <Button variant="ghost" size="sm" onClick={resetSurge} className="shrink-0 text-amber-700 hover:bg-amber-500/20 dark:text-amber-300">
            <X className="h-4 w-4" /> Dismiss
          </Button>
        </div>
      )}
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">
            {tabs.find((t) => t.id === activeTab)?.label ?? "Overview"}
          </h1>
          {showOverviewLoadingMessage && (
            <p className="mt-1 text-sm text-muted-foreground">
              Retrieving Data<LoadingDots />
            </p>
          )}
          {showInventoryRefreshingMessage && (
            <p className="mt-1 text-sm text-muted-foreground">
              Refreshing Data<LoadingDots />
            </p>
          )}
        </div>
        <TabsList className="h-auto w-fit rounded-none border-0 bg-transparent p-0">
          {tabs.map((tab) => (
            <TabsTrigger
              key={tab.id}
              value={tab.id}
              className={cn(
                "relative rounded-none border-0 bg-transparent px-4 py-2 text-muted-foreground shadow-none transition-colors hover:text-foreground data-[state=active]:bg-transparent data-[state=active]:text-foreground data-[state=active]:shadow-none",
                "data-[state=active]:after:absolute data-[state=active]:after:bottom-0 data-[state=active]:after:left-0 data-[state=active]:after:right-0 data-[state=active]:after:h-0.5 data-[state=active]:after:bg-primary data-[state=active]:after:content-['']"
              )}
            >
              {tab.label}
            </TabsTrigger>
          ))}
        </TabsList>
      </div>

      <TabsContent value="overview" className="mt-0">
        <OverviewContent loading={overviewLoading} />
      </TabsContent>
      <TabsContent value="staffing" className="mt-0">
        <StaffingContent />
      </TabsContent>
      <TabsContent value="inventory" className="mt-0">
        <InventoryContent loading={inventoryRefreshing} useDemo={useDemoInventory} />
      </TabsContent>
    </Tabs>
  )
}

function OverviewContent({ loading }: { loading: boolean }) {
  if (loading) {
    return (
      <>
        <Skeleton className="h-24 w-full rounded-xl" />
        <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-[4.5rem] rounded-lg" />
          ))}
        </div>
        <div className="mt-8 grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2 space-y-6">
            <Skeleton className="h-64 w-full rounded-xl" />
            <Skeleton className="h-48 w-full rounded-xl" />
          </div>
          <div className="space-y-6">
            <Skeleton className="h-48 w-full rounded-xl" />
            <Skeleton className="h-64 w-full rounded-xl" />
          </div>
        </div>
      </>
    )
  }
  return (
    <>
      <BusynessCard busynessRating={3.3} />
      <div className="mt-4">
        <CitySnapshot />
      </div>
      <div className="mt-8 grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <FootTrafficChart />
          <div className="mt-6">
            <StaffingOverview />
          </div>
        </div>
        <div className="space-y-6">
          <CitySignalsPanel />
          <AgentActionFeed variant="overview" />
        </div>
      </div>
    </>
  )
}

function StaffingContent() {
  return (
    <>
      <CitySnapshot />
      <div className="mt-8 grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <StaffingLineChart />
          <div className="mt-6">
            <StaffingOverview showPrintButton />
          </div>
        </div>
        <div className="space-y-6">
          <CitySignalsPanel />
          <AgentActionFeed variant="staffing" />
        </div>
      </div>
    </>
  )
}

function InventoryContent({
  loading,
  useDemo,
}: {
  loading: boolean
  useDemo: boolean
}) {
  if (loading) {
    return (
      <>
        <Skeleton className="h-[4.5rem] w-full rounded-lg sm:hidden" />
        <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-[4.5rem] rounded-lg" />
          ))}
        </div>
        <div className="mt-8 grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2 space-y-6">
            <Skeleton className="h-64 w-full rounded-xl" />
            <Skeleton className="h-48 w-full rounded-xl" />
          </div>
          <div className="space-y-6">
            <Skeleton className="h-48 w-full rounded-xl" />
            <Skeleton className="h-64 w-full rounded-xl" />
          </div>
        </div>
      </>
    )
  }
  const InventoryOverviewComponent = useDemo ? InventoryOverviewDemo : InventoryOverviewStandard
  return (
    <>
      <CitySnapshot />
      <div className="mt-8 grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <InventoryBarChart useDemo={useDemo} />
          <div className="mt-6">
            <InventoryOverviewComponent />
          </div>
        </div>
        <div className="space-y-6">
          <CitySignalsPanel />
          <AgentActionFeed variant="inventory" />
        </div>
      </div>
    </>
  )
}
