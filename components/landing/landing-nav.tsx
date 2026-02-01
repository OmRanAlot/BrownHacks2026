"use client"

import Link from "next/link"
import Image from "next/image"
import { useRouter } from "next/navigation"
import { useState, useEffect } from "react"
import { cn } from "@/lib/utils"

export function LandingNav() {
  const [scrolled, setScrolled] = useState(false)
  const [username, setUsername] = useState<string | null>(null)
  const [mounted, setMounted] = useState(false)
  const router = useRouter()

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener("scroll", handleScroll, { passive: true })
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  useEffect(() => {
    if (!mounted) return
    setUsername(typeof window !== "undefined" ? window.localStorage.getItem("username") : null)
  }, [mounted])

  const scrollToAbout = () => {
    document.getElementById("ai-physical-world")?.scrollIntoView({ behavior: "smooth" })
  }

  const handleLogout = () => {
    if (typeof window !== "undefined") {
      window.localStorage.removeItem("username")
      setUsername(null)
      router.refresh()
    }
  }

  return (
    <nav className="fixed top-0 left-0 right-0 z-50">
      {/* Fading solid background with soft bottom edge */}
      <div
        className={cn(
          "absolute inset-0 backdrop-blur-sm transition-opacity duration-[1200ms] ease-out",
          scrolled ? "opacity-80" : "opacity-0"
        )}
        style={{
          backgroundColor: "var(--background)",
          boxShadow: "0 12px 40px -8px rgba(0,0,0,0.5)",
        }}
        aria-hidden
      />
      <div className="relative z-10 mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
        <Link href="/" className="flex min-w-0 shrink-0 items-center scale-105 origin-left">
<Image
              src="/logo.png"
              alt="Clarity"
              width={30}
              height={10}
              className="h-40 w-auto object-contain sm:h-48"
              priority
            />
        </Link>
        <div className="absolute left-1/2 hidden -translate-x-1/2 items-center gap-10 md:flex">
          <Link
            href="/agents"
            className="scale-105 shrink-0 text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            Agents
          </Link>
          <Link
            href="/dashboard"
            className="scale-105 shrink-0 text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            Dashboard
          </Link>
          <button
            type="button"
            onClick={scrollToAbout}
            className="scale-105 shrink-0 cursor-pointer text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            About
          </button>
        </div>
        <div className="flex min-w-0 shrink-0 items-center justify-end gap-3">
            {username ? (
              <>
                <span className="scale-105 max-w-[180px] truncate text-sm font-medium text-foreground" title={username}>
                  {username}
                </span>
                <button
                  type="button"
                  onClick={handleLogout}
                  className="scale-105 rounded-md border border-foreground/20 bg-transparent px-4 py-2 text-sm font-medium text-foreground transition-colors hover:bg-foreground/10"
                >
                  Logout
                </button>
              </>
            ) : (
              <Link
                href="/login"
                className="scale-105 rounded-md border border-foreground/20 bg-transparent px-5 py-2.5 text-sm font-medium text-foreground transition-colors hover:bg-foreground hover:text-background"
              >
                Login
              </Link>
            )}
          </div>
      </div>
    </nav>
  )
}
