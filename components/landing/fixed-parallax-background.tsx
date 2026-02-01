export function FixedParallaxBackground() {
  return (
    <div
      className="fixed inset-0 z-0 bg-cover bg-center bg-no-repeat"
      style={{
        backgroundImage: `url('https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?q=80&w=2944&auto=format&fit=crop')`,
      }}
    >
      {/* Vignette: darkened edges, clear center */}
      <div
        className="absolute inset-0"
        style={{
          background:
            "radial-gradient(ellipse 80% 70% at 50% 50%, transparent 0%, rgba(0,0,0,0.3) 60%, rgba(0,0,0,0.7) 100%)",
        }}
      />
      {/* Base overlay for text readability - subtle so city remains visible */}
      <div className="absolute inset-0 bg-background/40" />
    </div>
  )
}
