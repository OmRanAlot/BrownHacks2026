"use client"

import { useEffect } from "react"

export function ScrollToHash() {
  useEffect(() => {
    if (typeof window === "undefined") return
    if (window.location.hash === "#ai-physical-world") {
      const el = document.getElementById("ai-physical-world")
      if (el) {
        el.scrollIntoView({ behavior: "smooth" })
      }
    }
  }, [])
  return null
}
