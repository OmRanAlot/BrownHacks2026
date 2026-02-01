import { HeroSection } from "@/components/landing/hero-section"
import { VisionSection } from "@/components/landing/vision-section"
import { EcosystemSection } from "@/components/landing/ecosystem-section"
import { LandingNav } from "@/components/landing/landing-nav"
import { FixedParallaxBackground } from "@/components/landing/fixed-parallax-background"
import { ScrollToHash } from "@/components/landing/scroll-to-hash"

export default function LandingPage() {
  return (
    <main className="relative min-h-screen">
      <ScrollToHash />
      {/* Fixed city background + vignette - sections scroll over it */}
      <FixedParallaxBackground />

      <LandingNav />

      <HeroSection />
      <VisionSection />
      <EcosystemSection />
    </main>
  )
}
