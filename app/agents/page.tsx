import Link from "next/link"
import { ArrowLeft } from "lucide-react"
import { OrchestratorPanel } from "@/components/agents/orchestrator-panel"
import { PredictorPanel } from "@/components/agents/predictor-panel"
import { OperatorPanel } from "@/components/agents/operator-panel"

export default function AgentsPage() {
  return (
    <main className="min-h-screen bg-background">
      <header className="sticky top-0 z-50 border-b border-border bg-background/95 backdrop-blur-sm">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-4">
            <Link
              href="/dashboard"
              className="flex h-8 w-8 items-center justify-center rounded-md bg-secondary text-foreground transition-colors hover:bg-secondary/80"
            >
              <ArrowLeft className="h-4 w-4" />
            </Link>
            <div>
              <h1 className="text-lg font-semibold text-foreground">Agent Activity</h1>
              <p className="text-sm text-muted-foreground">Multi-agent system status</p>
            </div>
          </div>
          <div className="flex items-center gap-2 rounded-full bg-accent/10 px-3 py-1.5">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-accent opacity-75" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-accent" />
            </span>
            <span className="text-xs font-medium text-accent">System Online</span>
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-7xl px-6 py-8">
        <div className="mb-8 rounded-xl border border-border bg-card p-6">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <span className="mb-2 inline-block text-xs font-medium text-primary">SYSTEM OVERVIEW</span>
              <h2 className="text-2xl font-bold text-foreground">Autonomous Decision Engine</h2>
              <p className="mt-1 text-muted-foreground">
                Three agents working together: Sense → Decide → Act
              </p>
            </div>
            <div className="flex items-center gap-6">
              <SystemStat label="Decisions Today" value="47" />
              <SystemStat label="Actions Taken" value="23" />
              <SystemStat label="Success Rate" value="98.2%" />
            </div>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <OrchestratorPanel />
          <PredictorPanel />
          <OperatorPanel />
        </div>
      </div>
    </main>
  )
}

function SystemStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="text-center">
      <p className="text-2xl font-bold text-foreground">{value}</p>
      <p className="text-xs text-muted-foreground">{label}</p>
    </div>
  )
}
