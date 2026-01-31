"use client"

import Link from "next/link"

export function HeroSection() {
  return (
    <section className="relative min-h-screen overflow-hidden">
      {/* Background image with overlay */}
      <div 
        className="absolute inset-0 bg-cover bg-center bg-no-repeat"
        style={{
          backgroundImage: `url('https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?q=80&w=2944&auto=format&fit=crop')`,
        }}
      />
      <div className="absolute inset-0 bg-background/70" />
      
      <div className="relative z-10 mx-auto flex min-h-screen max-w-7xl items-center px-6 pt-20">
        <div className="grid w-full gap-12 lg:grid-cols-2 lg:gap-20">
          {/* Left: Hero text */}
          <div className="flex flex-col justify-center">
            <h1 className="mb-8 font-serif text-5xl leading-tight text-foreground md:text-6xl lg:text-7xl">
              See <em className="italic">through</em>
              <br />
              <span className="text-primary">the noise.</span>
            </h1>
            
            <p className="mb-10 max-w-md text-lg leading-relaxed text-muted-foreground">
              Turn city chaos into staffing clarity. The first AI platform designed to predict 
              foot traffic and automatically optimize operations in real-time.
            </p>
            
            <div className="flex items-center gap-6">
              <Link
                href="/dashboard"
                className="rounded-sm bg-foreground px-6 py-3.5 text-sm font-medium text-background transition-colors hover:bg-foreground/90"
              >
                View Dashboard
              </Link>
              <Link
                href="/agents"
                className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
              >
                Launch Agents
              </Link>
            </div>
          </div>
          
          {/* Right: Camera feed mockup */}
          <div className="flex items-center justify-center lg:justify-end">
            <div className="grid w-full max-w-lg gap-3">
              <div className="grid grid-cols-2 gap-3">
                <CameraFeed label="SIGNAL 1" active />
                <CameraFeed label="SIGNAL 2" active />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <CameraFeed label="SIGNAL 3" active />
                <CameraFeed label="SIGNAL 4" active />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

function CameraFeed({ label, active }: { label: string; active?: boolean }) {
  return (
    <div className="relative aspect-[4/3] rounded-sm border border-border/50 bg-card/80 backdrop-blur-sm">
      <div className="absolute inset-x-0 top-0 flex items-center justify-between p-3">
        <span className="font-mono text-[10px] tracking-widest text-muted-foreground">{label}</span>
        {active && (
          <span className="h-2 w-2 rounded-full bg-chart-2" />
        )}
      </div>
    </div>
  )
}
