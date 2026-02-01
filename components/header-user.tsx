"use client"

import Link from "next/link"
import { useState, useEffect } from "react"

export function HeaderUser() {
  const [username, setUsername] = useState<string | null>(null)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (!mounted) return
    setUsername(typeof window !== "undefined" ? window.localStorage.getItem("username") : null)
  }, [mounted])

  if (!mounted) return null

  if (username) {
    return (
      <span className="text-sm font-medium text-foreground">
        {username}
      </span>
    )
  }

  return (
    <Link
      href="/login"
      className="rounded-md border border-foreground/20 bg-transparent px-5 py-2.5 text-sm font-medium text-foreground transition-colors hover:bg-foreground hover:text-background"
    >
      Login
    </Link>
  )
}
