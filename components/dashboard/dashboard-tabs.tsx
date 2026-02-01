"use client"

import { useState } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { CitySnapshot } from "@/components/dashboard/city-snapshot"
import { FootTrafficChart } from "@/components/dashboard/foot-traffic-chart"
import { StaffingLineChart } from "@/components/dashboard/staffing-line-chart"
import { InventoryBarChart } from "@/components/dashboard/inventory-bar-chart"
import { CitySignalsPanel } from "@/components/dashboard/city-signals-panel"
import { AgentActionFeed } from "@/components/dashboard/agent-action-feed"
import { StaffingOverview } from "@/components/dashboard/staffing-overview"
import { InventoryOverview } from "@/components/dashboard/inventory-overview"
import { cn } from "@/lib/utils"

const tabs = [
  { id: "overview", label: "Overview" },
  { id: "staffing", label: "Staffing" },
  { id: "inventory", label: "Inventory" },
] as const

export function DashboardTabs() {
  const [activeTab, setActiveTab] = useState("overview")

  return (
    <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v)}>
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <h1 className="text-2xl font-bold text-foreground">
          {tabs.find((t) => t.id === activeTab)?.label ?? "Overview"}
        </h1>
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
        <OverviewContent />
      </TabsContent>
      <TabsContent value="staffing" className="mt-0">
        <StaffingContent />
      </TabsContent>
      <TabsContent value="inventory" className="mt-0">
        <InventoryContent />
      </TabsContent>
    </Tabs>
  )
}

function OverviewContent() {
  return (
    <>
      <CitySnapshot />
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

function InventoryContent() {
  return (
    <>
      <CitySnapshot />
      <div className="mt-8 grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <InventoryBarChart />
          <div className="mt-6">
            <InventoryOverview />
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
