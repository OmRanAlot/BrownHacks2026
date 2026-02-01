import { DashboardHeader } from "@/components/dashboard/header"
import { DashboardTabs } from "@/components/dashboard/dashboard-tabs"

export default function DashboardPage() {
  return (
    <main className="min-h-screen bg-background">
      <DashboardHeader />
      <div className="mx-auto max-w-7xl px-6 py-8">
        <DashboardTabs />
      </div>
    </main>
  )
}
