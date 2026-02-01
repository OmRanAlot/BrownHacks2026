import Link from "next/link"
import Image from "next/image"
import { HeaderUser } from "@/components/header-user"

export default function AboutPage() {
  return (
    <main className="min-h-screen bg-background">
      <nav className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-sm">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
          <Link href="/" className="flex items-center">
            <Image
              src="/clarity-logo.png"
              alt="Clarity"
              width={120}
              height={40}
              className="h-10 w-auto object-contain"
              priority
            />
          </Link>
          <div className="hidden items-center gap-10 md:flex">
            <Link href="/agents" className="text-sm text-muted-foreground transition-colors hover:text-foreground">
              Agents
            </Link>
            <Link href="/dashboard" className="text-sm text-muted-foreground transition-colors hover:text-foreground">
              Dashboard
            </Link>
          </div>
          <HeaderUser />
        </div>
      </nav>

      <section id="about" className="border-t border-border py-32 pt-32">
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
      </section>
    </main>
  )
}
