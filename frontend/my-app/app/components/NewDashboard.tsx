'use client'

import { useRouter } from "next/dist/client/components/navigation"
import { useEffect, useState } from "react"
import { TypeAnimation } from "react-type-animation"
import TrendingTopics from "./TrendingTopics"
import { TrendingClaims } from "../sections/TrendingClaims"
import TrendingLocations from "../sections/TrendingLocations"
import TopCountries from "./TopCountries"
import TrendingNarratives from "../sections/TrendingNarratives"
import StatsMain from "../sections/StatsMain"


export default function NewDashboard() {
    const [searchTerm, setSearchTerm] = useState("")
    const [isTyping, setIsTyping] = useState(true)
    const [matches, setMatches] = useState<any[]>([])
    const [searching, setSearching] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"
    const router = useRouter()

    useEffect(() => {
      if (!searchTerm.trim()) {
        setMatches([])
        setError(null)
        return
      }

      const id = setTimeout(async () => {
        try {
          setSearching(true)
          setError(null)
          const res = await fetch(`${API_BASE}/api/destinations/${encodeURIComponent(searchTerm)}`)
          if (!res.ok) throw new Error(`API ${res.status}`)
          const data = await res.json()
          // normalize to array
          setMatches(Array.isArray(data) ? data : [data])
        } catch (err) {
          setError("No matches found")
          setMatches([])
        } finally {
          setSearching(false)
        }
      }, 300)

      return () => clearTimeout(id)
    }, [API_BASE, searchTerm])


  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0c0c12] via-[#130f18] to-[#0c0c12] text-white">
      <div className="max-w-6xl mx-auto px-6 pb-16 pt-12 space-y-10">
        <header className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div className="space-y-3">
            <p className="text-xs uppercase tracking-[0.3em] text-gray-400">Dashboard</p>
            <h1 className="text-4xl font-semibold leading-tight">YouTravel</h1>
            <p className="text-sm text-gray-400 max-w-2xl">
              Combine creator sentiment, trend velocity, and safety signals before you book. Start with a search or
              pick a quick filter to explore narratives already emerging on YouTube.
            </p>
          </div>
        </header>

        <section className="space-y-3">
            <form
              onSubmit={(e) => {
                e.preventDefault()
                if (searchTerm.trim()) {
                  router.push(`/discover/${searchTerm.toLowerCase()}`)
                }
              }}
            >
                <label className="sr-only" htmlFor="discover-search">
                    Search destinations
                </label>
                <div className="relative flex gap-2 bg-[#16161e] border border-[#242436] rounded-2xl px-4 py-2 shadow-lg shadow-black/40">
                    <input
                        id="discover-search"
                        type="search"
                        placeholder="search your next travel destination"
                        className="flex-1 bg-transparent text-sm text-white focus:outline-none placeholder:text-transparent"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        onFocus={() => setIsTyping(false)}
                        onBlur={() => {
                            if (!searchTerm) setIsTyping(true)
                        }}
                    />
                    {isTyping && !searchTerm && (
                        <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-sm text-gray-500">
                            <TypeAnimation sequence={["search your next travel destination"]} />
                        </span>
                    )}
                    {searching && (
                        <span className="absolute right-24 top-1/2 -translate-y-1/2 text-xs text-gray-400">
                            Searching…
                        </span>
                    )}
                    <button
                      type="button"
                      className="rounded-xl bg-white/10 px-4 py-2 text-sm font-medium transition hover:bg-white/20"
                      onClick={() => {
                        if (searchTerm.trim()) {
                          router.push(`/discover/${searchTerm.toLowerCase()}`)
                        }
                      }}
                    >
                      Search
                    </button>
                    {!searching && matches.length > 0 && (
                        <div className="absolute left-0 top-full mt-2 w-full rounded-xl border border-white/10 bg-[#16161e] shadow-xl backdrop-blur-sm max-h-64 overflow-y-auto z-20">
                            {matches.map((dest) => {
                                const name = dest.name ?? dest.destination ?? searchTerm
                                return (
                                    <button
                                        key={dest.id ?? name}
                                        type="button"
                                        onMouseDown={(e) => {
                                          e.preventDefault()
                                          router.push(`/discover/${encodeURIComponent(name.toLowerCase())}`)
                                        }}
                                        className="w-full text-left px-4 py-3 hover:bg-white/10 transition"
                                    >
                                        <p className="text-sm text-white">{name}</p>
                                        {dest.blurb && <p className="text-xs text-gray-400 line-clamp-2">{dest.blurb}</p>}
                                    </button>
                                )
                            })}
                        </div>
                    )}
                    {error && !searching && searchTerm && (
                        <div className="absolute left-0 top-full mt-2 w-full rounded-xl border border-red-500/30 bg-red-900/70 px-4 py-2 text-xs text-red-100 z-20">
                            {error}
                        </div>
                    )}
                </div>
            </form>
            <TrendingTopics />
            <StatsMain />
            <TrendingNarratives />
            <TopCountries />
            <TrendingLocations />
            <TrendingClaims />
    
        </section>
      </div>
    </div>
  )
}
