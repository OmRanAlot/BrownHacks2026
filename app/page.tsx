import Link from "next/link"
import { HeroSection } from "@/components/landing/hero-section"
import { VisionSection } from "@/components/landing/vision-section"
import { EcosystemSection } from "@/components/landing/ecosystem-section"
import { Footer } from "@/components/landing/footer"

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-sm">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
          <Link href="/" className="font-serif text-xl font-bold tracking-wide text-foreground">
            CITYFOOTFALL
          </Link>
          <div className="hidden items-center gap-10 md:flex">
            <Link href="/agents" className="text-sm text-muted-foreground transition-colors hover:text-foreground">
              Agents
            </Link>
            <Link href="/dashboard" className="text-sm text-muted-foreground transition-colors hover:text-foreground">
              Dashboard
            </Link>
            <Link href="#about" className="text-sm text-muted-foreground transition-colors hover:text-foreground">
              About
            </Link>
          </div>
          <Link
            href="/dashboard"
            className="rounded-sm border border-foreground/20 bg-transparent px-5 py-2.5 text-sm font-medium text-foreground transition-colors hover:bg-foreground hover:text-background"
          >
            Get Started
          </Link>
        </div>
      </nav>
      
      <HeroSection />
      <VisionSection />
      <EcosystemSection />
      <Footer />
    </main>
  )
}
