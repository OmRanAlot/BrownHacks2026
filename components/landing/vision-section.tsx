"use client"

export function VisionSection() {
  return (
    <section className="relative border-t border-border py-32">
      <div className="mx-auto max-w-7xl px-6">
        <div className="grid gap-16 lg:grid-cols-2 lg:gap-24">
          {/* Left: Content */}
          <div>
            <span className="mb-6 block font-mono text-xs tracking-[0.3em] text-primary">
              PREDICTIVE AI
            </span>
            
            <h2 className="mb-8 font-serif text-4xl leading-tight text-foreground md:text-5xl">
              AI for the <em className="italic">Physical</em> World
            </h2>
            
            <p className="mb-12 text-lg leading-relaxed text-muted-foreground">
              Turn chaotic city signals into structured operational data. Our AI sees what humans 
              miss, tracking every trend and pattern in real-time.
            </p>
            
            <div className="space-y-0">
              <FeatureItem
                title="Signal Aggregation"
                description="Automatically detect and track weather, events, and maps data. No manual setup required."
              />
              <FeatureItem
                title="Demand Prediction"
                description="Real-time demand forecasting with 94.7% accuracy. Know exactly when surges will happen."
              />
              <FeatureItem
                title="State Classification"
                description="Instant classification of business states: busy, slow, rush-hour. Eliminate guesswork."
              />
            </div>
          </div>
          
          {/* Right: Floor plan mockup */}
          <div className="flex items-center justify-center">
            <div className="w-full max-w-md rounded-sm border border-border bg-card p-1">
              {/* Window chrome */}
              <div className="mb-4 flex items-center gap-2 px-3 pt-3">
                <span className="h-3 w-3 rounded-full bg-destructive" />
                <span className="h-3 w-3 rounded-full bg-warning" />
                <span className="h-3 w-3 rounded-full bg-chart-2" />
              </div>
              
              <div className="p-4">
                <div className="mb-6 flex items-center justify-between">
                  <span className="font-mono text-xs tracking-widest text-muted-foreground">
                    ZONE 1 • MAIN AREA
                  </span>
                  <span className="flex items-center gap-2 text-xs text-chart-2">
                    <span className="h-2 w-2 rounded-full bg-chart-2" />
                    LIVE
                  </span>
                </div>
                
                {/* Grid of zones */}
                <div className="grid grid-cols-4 gap-2">
                  {[
                    { id: "01", status: "empty" },
                    { id: "02", status: "occupied" },
                    { id: "03", status: "occupied" },
                    { id: "04", status: "occupied" },
                    { id: "05", status: "empty" },
                    { id: "06", status: "warning" },
                    { id: "07", status: "occupied" },
                    { id: "08", status: "empty" },
                  ].map((zone) => (
                    <ZoneCard key={zone.id} {...zone} />
                  ))}
                </div>
                
                {/* Legend */}
                <div className="mt-6 flex items-center gap-6">
                  <LegendItem color="bg-chart-2" label="Available" />
                  <LegendItem color="bg-destructive" label="Busy" />
                  <LegendItem color="bg-warning" label="Peak Soon" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

function FeatureItem({ title, description }: { title: string; description: string }) {
  return (
    <div className="border-t border-border py-6">
      <h3 className="mb-2 text-base font-semibold text-foreground">{title}</h3>
      <p className="text-sm leading-relaxed text-muted-foreground">{description}</p>
    </div>
  )
}

function ZoneCard({ id, status }: { id: string; status: string }) {
  const statusColors: Record<string, string> = {
    empty: "bg-chart-2",
    occupied: "bg-destructive",
    warning: "bg-warning",
  }
  
  return (
    <div className="relative aspect-square rounded-sm border border-border bg-secondary/50">
      <span className="absolute left-2 top-2 font-mono text-xs italic text-muted-foreground">
        {id}
      </span>
      <span className={`absolute bottom-2 right-2 h-2 w-2 rounded-full ${statusColors[status]}`} />
    </div>
  )
}

function LegendItem({ color, label }: { color: string; label: string }) {
  return (
    <div className="flex items-center gap-2">
      <span className={`h-2 w-2 rounded-full ${color}`} />
      <span className="text-xs text-muted-foreground">{label}</span>
    </div>
  )
}
