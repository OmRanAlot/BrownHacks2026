import Link from "next/link"

export function Footer() {
  return (
    <footer id="about" className="border-t border-border py-16">
      <div className="mx-auto max-w-7xl px-6">
        <div className="flex flex-col items-center justify-between gap-8 md:flex-row">
          <div>
            <Link href="/" className="font-serif text-lg font-bold tracking-wide text-foreground">
              CITYFOOTFALL
            </Link>
            <p className="mt-2 text-sm text-muted-foreground">
              Autonomous AI for smarter urban operations.
            </p>
          </div>
          
          <div className="flex items-center gap-8">
            <Link href="/dashboard" className="text-sm text-muted-foreground transition-colors hover:text-foreground">
              Dashboard
            </Link>
            <Link href="/agents" className="text-sm text-muted-foreground transition-colors hover:text-foreground">
              Agents
            </Link>
            <Link href="#" className="text-sm text-muted-foreground transition-colors hover:text-foreground">
              API Docs
            </Link>
          </div>
        </div>
        
        <div className="mt-12 border-t border-border pt-8 text-center">
          <p className="text-xs text-muted-foreground">
            Built with FastAPI + React. MCP Compatible.
          </p>
        </div>
      </div>
    </footer>
  )
}
