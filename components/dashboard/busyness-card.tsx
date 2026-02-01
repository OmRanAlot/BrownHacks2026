"use client"

import { Star } from "lucide-react"
import { cn } from "@/lib/utils"

const STAR_COUNT = 5

function clampRating(value: number): number {
  return Math.min(Math.max(value, 0), STAR_COUNT)
}

export function getBusynessMessage(rating: number): string {
  const r = clampRating(rating)
  if (r <= 1.0) return "Not busy today"
  if (r <= 2.0) return "Light crowd today"
  if (r <= 3.0) return "Moderately busy today"
  if (r <= 4.0) return "Busy today"
  return "Extremely busy today"
}

export interface BusynessCardProps {
  /** Rating from 0.0 to 5.0 (clamped). */
  busynessRating?: number
  className?: string
}

/** Per-star fill: clamp(rating - starIndex, 0, 1). Ensures each 0.1 change is visible on one star. */
function starFillAmount(rating: number, starIndex: number): number {
  return Math.min(1, Math.max(0, rating - starIndex))
}

export function BusynessCard({ busynessRating = 3, className }: BusynessCardProps) {
  const rating = clampRating(busynessRating)
  const message = getBusynessMessage(rating)

  return (
    <div
      className={cn(
        "rounded-xl border border-border bg-card p-6",
        "min-h-[theme(spacing.24)] flex flex-col justify-center sm:min-h-0",
        className
      )}
    >
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between sm:gap-6">
        {/* Left: label + stars (per-star fill so each 0.1 step is clearly visible) */}
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:gap-4">
          <span className="text-xs font-medium text-muted-foreground">Busyness</span>
          <div className="flex items-center gap-0.5" aria-label={`Busyness: ${rating} out of 5`}>
            {Array.from({ length: STAR_COUNT }, (_, i) => {
              const fill = starFillAmount(rating, i)
              return (
                <div key={i} className="relative h-5 w-5 shrink-0">
                  {/* Empty (outline) star - base */}
                  <Star
                    className="absolute inset-0 h-5 w-5 text-muted-foreground/60 stroke-[1.5]"
                    strokeWidth={1.5}
                    fill="none"
                    aria-hidden
                  />
                  {/* Filled portion - clipped to this star only (left-to-right by tenths) */}
                  <div
                    className="absolute inset-0 overflow-hidden"
                    style={{ width: `${fill * 100}%` }}
                  >
                    <Star
                      className="h-5 w-5 fill-primary stroke-primary"
                      strokeWidth={0}
                      aria-hidden
                    />
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Right: message */}
        <p className="text-sm text-foreground sm:text-right min-w-0 flex-1 sm:flex-initial">
          {message}
        </p>
      </div>
    </div>
  )
}
