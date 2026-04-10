"use client"

import Link from "next/link"
import { useEffect, useState } from "react"
import { useParams } from "next/navigation"

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

interface Claim {
  claim_text: string
  source: string
  claim_risk: string
  date: string | null
}

interface Destination {
  id: string
  name: string
  blurb: string
  cluster_size: number | null
  computed_at: string | null
  top_claim: string | null
  claims: Claim[]
}

export default function DestinationPage() {
  const { slug } = useParams() as { slug: string }
  const [destination, setDestination] = useState<Destination | null>(null)
  const [loading, setLoading] = useState(true)
  const [notFound, setNotFound] = useState(false)

  useEffect(() => {
    async function fetchDestination() {
      try {
        const decoded = decodeURIComponent(slug)
        const res = await fetch(`${API_BASE}/api/destinations/${decoded}`)      
        if (res.status === 404) { setNotFound(true); return }
        if (!res.ok) throw new Error(`API ${res.status}`)
        const data: Destination = await res.json()
        setDestination(data)
      } catch (err) {
        console.error("Failed to fetch destination:", err)
        setNotFound(true)
      } finally {
        setLoading(false)
      }
    }
    fetchDestination()
  }, [slug])

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-[#0b0b10] via-[#0f1018] to-[#0b0b10] text-white">
        <div className="max-w-6xl mx-auto px-6 pt-12 space-y-6">
          <div className="h-10 w-48 rounded-xl bg-white/10 animate-pulse" />
          <div className="h-40 rounded-2xl bg-white/10 animate-pulse" />
          <div className="grid grid-cols-3 gap-4">
            {[1,2,3].map(n => <div key={n} className="h-24 rounded-2xl bg-white/10 animate-pulse" />)}
          </div>
        </div>
      </div>
    )
  }

  if (notFound || !destination) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-[#0b0b10] via-[#0f1018] to-[#0b0b10] text-white flex items-center justify-center">
        <div className="text-center space-y-4">
          <h1 className="text-3xl font-semibold">Destination not found</h1>
          <p className="text-gray-400">We don't have data for "{slug}" yet.</p>
          <Link href="/" className="inline-block mt-4 underline underline-offset-4 text-purple-300 hover:text-white">
            Back to dashboard
          </Link>
        </div>
      </div>
    )
  }

  const riskCounts = { low: 0, medium: 0, high: 0 }
  destination.claims.forEach(c => {
    const r = (c.claim_risk ?? "").toLowerCase()
    if (r.includes("low")) riskCounts.low++
    else if (r.includes("high")) riskCounts.high++
    else riskCounts.medium++
  })

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0b0b10] via-[#0f1018] to-[#0b0b10] text-white">
      <div className="max-w-6xl mx-auto px-6 pb-16 pt-12 space-y-10">

        {/* Breadcrumb */}
        <div className="flex items-center gap-4 text-sm text-gray-400">
          <Link href="/" className="underline underline-offset-4 decoration-white/30 hover:text-white">
            Dashboard
          </Link>
          <span>›</span>
          <span className="text-gray-200">{destination.name}</span>
        </div>

        {/* Header */}
        <header className="space-y-4">
          <div className="flex flex-wrap items-center gap-3">
            <span className="rounded-full bg-white/10 text-gray-200 px-3 py-1 text-xs border border-white/10">
              {destination.claims.length} claims analyzed
            </span>
            {destination.cluster_size && (
              <span className="rounded-full bg-purple-500/15 text-purple-200 px-3 py-1 text-xs border border-purple-400/30">
                {destination.cluster_size} clustered narratives
              </span>
            )}
            {destination.computed_at && (
              <span className="rounded-full bg-white/10 text-gray-200 px-3 py-1 text-xs border border-white/10">
                Updated {new Date(destination.computed_at).toLocaleDateString()}
              </span>
            )}
          </div>

          <div className="bg-[#E4CAFF] rounded-2xl w-full px-10 py-10 font-light mt-10">
            <h1 className="text-4xl font-light leading-tight text-black">{destination.name}</h1>
            <p className="text-base text-black max-w-3xl pt-5">
              {destination.blurb || "No summary available yet for this destination."}
            </p>
          </div>
        </header>

        {/* Metrics */}
        <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Metric label="Claims analyzed" value={destination.claims.length.toString()} />
          <Metric label="Low risk claims" value={riskCounts.low.toString()} />
          <Metric label="Medium risk claims" value={riskCounts.medium.toString()} />
          <Metric label="High risk claims" value={riskCounts.high.toString()} />
        </section>

        {/* Top claim */}
        {destination.top_claim && (
          <section className="space-y-3">
            <p className="text-xs uppercase tracking-[0.25em] text-gray-400">Top Narrative</p>
            <div className="rounded-2xl border border-purple-400/20 bg-purple-500/10 p-6">
              <p className="text-white text-base leading-relaxed">"{destination.top_claim}"</p>
            </div>
          </section>
        )}

        {/* Claims list */}
        {destination.claims.length > 0 && (
          <section className="space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.25em] text-gray-400">Claims</p>
                <p className="text-sm text-gray-400">What creators are saying about {destination.name}.</p>
              </div>
              <span className="text-xs text-gray-400">{destination.claims.length} total</span>
            </div>
            <div className="flex gap-4 overflow-x-auto pb-2">
              {destination.claims.map((claim, i) => {
                const risk = (claim.claim_risk ?? "").toLowerCase()
                const isHigh = risk.includes("high")
                const isLow = risk.includes("low")
                return (
                  <div
                    key={i}
                    className="min-w-[260px] max-w-[280px] rounded-2xl border border-white/10 bg-gradient-to-b from-[#151525] via-[#11111a] to-[#0c0c12] p-4 shadow-lg shadow-black/40 flex flex-col gap-2"
                  >
                    <span className={`self-start text-[11px] px-2 py-1 rounded-full border ${
                      isHigh
                        ? "border-rose-300/40 text-rose-200 bg-rose-400/10"
                        : isLow
                        ? "border-emerald-400/40 text-emerald-200 bg-emerald-400/10"
                        : "border-amber-300/40 text-amber-200 bg-amber-300/10"
                    }`}>
                      {claim.claim_risk || "unknown risk"}
                    </span>
                    <p className="text-sm text-gray-100 leading-snug">"{claim.claim_text}"</p>
                    <p className="text-xs text-gray-500 mt-auto">
                      {claim.source}
                      {claim.date ? ` · ${new Date(claim.date).toLocaleDateString()}` : ""}
                    </p>
                  </div>
                )
              })}
            </div>
          </section>
        )}
      </div>
    </div>
  )
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-4 shadow-inner shadow-black/30">
      <p className="text-[11px] uppercase tracking-wide text-gray-400">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-white">{value}</p>
    </div>
  )
}
