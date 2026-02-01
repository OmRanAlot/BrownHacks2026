"use client"

import Link from "next/link"

export function HeroSection() {
  return (
    <section className="relative z-10 flex min-h-screen items-center">
      <div className="mx-auto w-full max-w-7xl px-6 pt-20">
        <div className="grid w-full gap-12 lg:grid-cols-2 lg:gap-20">
          {/* Left: Hero text */}
          <div className="flex flex-col justify-center">
            <h1 className="mb-8 scale-105 font-serif text-6xl leading-tight text-foreground md:text-7xl lg:text-8xl [transform-origin:left_top]">
              Cut through <em className="italic"></em>
              <br />
              <span className="text-primary">the noise.</span>
            </h1>

            <p className="mb-10 max-w-md scale-105 text-lg leading-relaxed text-muted-foreground [transform-origin:left_top]">
              Built for small businesses to predict foot traffic, adjust staffing, and manage inventory automatically in real time.
            </p>

            <div className="flex scale-105 items-center gap-6 [transform-origin:left_top]">
              <Link
                href="/dashboard"
                className="rounded-md bg-foreground px-6 py-3.5 text-sm font-medium text-background transition-colors hover:bg-foreground/90"
              >
                View Dashboard
              </Link>
              <Link
                href="/agents"
                className="rounded-md border border-primary/40 bg-transparent px-6 py-3.5 text-sm font-medium text-primary transition-all duration-300 hover:border-primary/60 hover:bg-primary/10 hover:text-primary"
              >
                Launch Agents
              </Link>
            </div>
          </div>

          {/* Right: Decorative spacer for layout balance */}
          <div className="hidden lg:block" />
        </div>
      </div>
    </section>
  )
}
