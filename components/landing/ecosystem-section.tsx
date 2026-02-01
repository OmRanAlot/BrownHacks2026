"use client"

import React from "react"

export function EcosystemSection() {
  return (
    <section className="relative z-10 border-t border-border bg-background/80 py-32 backdrop-blur-[2px]">
      <div className="mx-auto max-w-7xl px-6">
        <div className="mb-20 text-center">
          <span className="mb-6 block font-mono text-xs tracking-[0.3em] text-primary">
            THE ECOSYSTEM
          </span>
          <h2 className="font-serif text-4xl leading-tight text-foreground md:text-5xl lg:text-6xl">
            One Platform for <em className="italic text-primary">All</em> Businesses
          </h2>
        </div>
        
        {/* Abstract visualization - particle grid */}
        <div className="relative mx-auto mb-20 h-96 max-w-2xl">
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="relative h-full w-64">
              {/* Vertical particle lines */}
              {Array.from({ length: 12 }).map((_, i) => (
                <div
                  key={i}
                  className="absolute top-0 h-full"
                  style={{ left: `${(i / 11) * 100}%` }}
                >
                  {Array.from({ length: 20 }).map((_, j) => (
                    <span
                      key={j}
                      className="absolute h-1 w-1 rounded-full bg-primary"
                      style={{
                        top: `${(j / 19) * 100}%`,
                        opacity: 0.3 + Math.random() * 0.7,
                        transform: `translateX(${Math.sin((i + j) * 0.5) * 20}px)`,
                      }}
                    />
                  ))}
                </div>
              ))}
              {/* Top arc */}
              <div className="absolute -top-4 left-1/2 h-20 w-48 -translate-x-1/2 rounded-t-full border-t-2 border-primary/40" />
              <div className="absolute -top-8 left-1/2 h-24 w-56 -translate-x-1/2 rounded-t-full border-t border-primary/20" />
            </div>
          </div>
          
          {/* Floating capability cards - spaced further apart horizontally and vertically */}
          <div className="absolute left-0 top-[10%] -translate-x-8 lg:-translate-x-16">
            <CapabilityCard category="VISION AI" title="City Awareness" />
          </div>
          <div className="absolute right-0 top-[10%] translate-x-8 lg:translate-x-16">
            <CapabilityCard category="ANALYTICS" title="Demand Forecast" />
          </div>
          <div className="absolute bottom-[10%] left-0 -translate-x-8 lg:-translate-x-16">
            <CapabilityCard category="OPERATIONS" title="Staff Efficiency" />
          </div>
          <div className="absolute bottom-[10%] right-0 translate-x-8 lg:translate-x-16">
            <CapabilityCard category="REVENUE" title="Optimization" />
          </div>
        </div>
      </div>
    </section>
  )
}

function CapabilityCard({ category, title }: { category: string; title: string }) {
  return (
    <div className="w-44 rounded-sm border border-border bg-card/80 p-5 backdrop-blur-sm">
      <span className="mb-2 block font-mono text-[10px] tracking-[0.2em] text-primary">
        {category}
      </span>
      <span className="text-base font-medium text-foreground">{title}</span>
    </div>
  )
}

