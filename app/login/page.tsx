"use client"

import { useState } from "react"
import Link from "next/link"
import Image from "next/image"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { HeaderUser } from "@/components/header-user"

export default function LoginPage() {
  const [usernameInput, setUsernameInput] = useState("")
  const router = useRouter()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const name = usernameInput.trim() || "Guest"
    if (typeof window !== "undefined") {
      window.localStorage.setItem("username", name)
    }
    router.push("/")
  }

  return (
    <main className="min-h-screen bg-background">
      <nav className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-sm">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
          <Link href="/" className="flex items-center">
            <Image
              src="/logo.png"
              alt="Clarity"
              width={120}
              height={40}
              className="h-40 w-auto object-contain sm:h-48"
              priority
            />
          </Link>
          <div className="hidden items-center gap-10 md:flex">
            <Link href="/agents" className="text-sm text-muted-foreground transition-colors hover:text-foreground">
              Agents
            </Link>
            <Link href="/dashboard" className="text-sm text-muted-foreground transition-colors hover:text-foreground">
              Dashboard
            </Link>
            <Link
              href="/#ai-physical-world"
              className="cursor-pointer text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              About
            </Link>
          </div>
          <HeaderUser />
        </div>
      </nav>

      <div className="flex min-h-screen items-center justify-center pt-20">
        <div className="w-full max-w-md rounded-sm border border-border bg-card px-10 py-12 sm:max-w-lg sm:px-12 sm:py-14">
          <h1 className="mb-8 font-serif text-2xl font-bold text-foreground">Login</h1>
          <form className="space-y-5" onSubmit={handleSubmit}>
            <div className="space-y-2">
              <Label htmlFor="username">Username</Label>
              <Input
                id="username"
                type="text"
                placeholder="Enter username"
                className="w-full border-2"
                value={usernameInput}
                onChange={(e) => setUsernameInput(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="Enter password"
                className="w-full border-2"
              />
            </div>
            <div>
              <button
                type="button"
                className="text-sm text-muted-foreground transition-colors hover:text-foreground hover:underline"
              >
                Forgot password?
              </button>
            </div>
            <Button type="submit" className="w-full">
              Submit
            </Button>
          </form>
        </div>
      </div>
    </main>
  )
}
