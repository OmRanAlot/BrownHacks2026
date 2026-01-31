import { DashboardHeader } from "@/components/dashboard/header"
import { CitySnapshot } from "@/components/dashboard/city-snapshot"
import { FootTrafficChart } from "@/components/dashboard/foot-traffic-chart"
import { CitySignalsPanel } from "@/components/dashboard/city-signals-panel"
import { AgentActionFeed } from "@/components/dashboard/agent-action-feed"
import { StaffingOverview } from "@/components/dashboard/staffing-overview"

export default function DashboardPage() {
  return (
    <main className="min-h-screen bg-background">
      <DashboardHeader />
      <div className="mx-auto max-w-7xl px-6 py-8">
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
            <AgentActionFeed />
          </div>
        </div>
      </div>
    </main>
  )
}
