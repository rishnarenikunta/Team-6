"use client"

import Link from "next/link"
import { useEffect, useState } from "react"
import { useParams } from "next/navigation"

interface Claim {
  claim_title: string
  source: string
  source_id?: string
  claim_risk: string
  claim_risk_extra_info?: string | null
  date: string | null
}

interface TopClaim {
  claim_text: string
  cluster_size: number | null
  computed_at: string | null
  total_docs: number
}

interface TopNarrative {
  narrative: string
  narrative_id?: string | null
  video_id?: string | null
  destination?: string
  cluster_size: number | null
  computed_at: string | null
  total_docs: number
  source?: string
  creator_name?: string
}

interface OverviewNarrativeItem {
  id: string
  narrative_id: string
  text: string
  destination: string
  date: string | null
  source: string
  creator_name: string
  video: {
    video_id: string
    title: string
    webpage_url: string
    upload_date: string | null
    view_count?: number
    like_count?: number
    comment_count?: number
  }
}

interface DestinationOverview {
  destination: string
  videos_analyzed: number
  total_claims: number
  total_narratives: number
  top_narrative: TopNarrative | null
  narratives: OverviewNarrativeItem[]
  top_claim: TopClaim | null
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

function claimRiskClassification(claim: Claim): Claim {
  const riskText = (claim.claim_risk ?? "").toLowerCase().trim()
  const risk =
    riskText.includes("low")
      ? "low"
      : riskText.includes("high")
      ? "high"
      : riskText.includes("none") || riskText.includes("unknown")
      ? "none"
      : "medium"

  const extraInfo = riskText
    .replace("unknown", "")
    .replace(risk, "")
    .replace(/\brisk\b/g, "")
    .replace(/^[\s;:,-]+|[\s;:,-]+$/g, "")
    .trim() || null

  return {
    ...claim,
    claim_risk: risk,
    claim_risk_extra_info: extraInfo,
  }
}

export default function DestinationPage() {
  const { slug } = useParams() as { slug: string }
  const [destination, setDestination] = useState<Destination | null>(null)
  const [loading, setLoading] = useState(true)
  const [notFound, setNotFound] = useState(false)
  const [topClaim, setTopClaim] = useState<TopClaim | null>(null)
  const [videoAnalyzed, setVideoAnalyzed] = useState<number | null>(null) //is a number of videos analyzed for the destination
  const [topNarrative, setTopNarrative] = useState<TopNarrative | null>(null)
  const [overviewNarratives, setOverviewNarratives] = useState<OverviewNarrativeItem[]>([])
  const [overviewTotals, setOverviewTotals] = useState<{ total_claims: number; total_narratives: number } | null>(null)


  useEffect(() => {
  async function fetchDestination() {
    try {
      const decoded = decodeURIComponent(slug)
      const [res, overviewRes, creatorsRes] = await Promise.all([
        fetch(`/api/destinations/${decoded}`),
        fetch(`/api/destinations/${decoded}/overview`),
        fetch(`/api/creators`),
      ])
      if (res.status === 404) { setNotFound(true); return }
      if (!res.ok) throw new Error(`API ${res.status}`)
      const data: Destination = await res.json()
      data.claims = (data.claims ?? []).map(claimRiskClassification)

      if (overviewRes.ok) {
        const overview: DestinationOverview = await overviewRes.json()
        setTopClaim(overview.top_claim)
        setVideoAnalyzed(overview.videos_analyzed)
        setTopNarrative(overview.top_narrative)
        setOverviewNarratives(overview.narratives ?? [])
        setOverviewTotals({ total_claims: overview.total_claims, total_narratives: overview.total_narratives })
      } else {
        setTopClaim(null)
        setVideoAnalyzed(null)
        setTopNarrative(null)
        setOverviewNarratives([])
        setOverviewTotals(null)
      }

      // Build creator map and enrich claims
      if (creatorsRes.ok) {
        const creatorsData: { channel_id: string; creator_name: string }[] = await creatorsRes.json()
        const creatorMap: Record<string, string> = {}
        for (const c of creatorsData) creatorMap[c.channel_id] = c.creator_name
        data.claims = data.claims.map(claim => ({
          ...claim,
          source_id: claim.source,
          source: creatorMap[claim.source] || claim.source,
        }))
      }

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
          <p className="text-gray-400">We don&apos;t have data for &quot;{slug}&quot; yet.</p>
          <Link href="/" className="inline-block mt-4 underline underline-offset-4 text-purple-300 hover:text-white">
            Back to dashboard
          </Link>
        </div>
      </div>
    )
  }

  const riskCounts = { low: 0, medium: 0, high: 0, none: 0 }
  destination.claims.forEach(c => {
    const r = (c.claim_risk ?? "").toLowerCase()
    if (r === "low") riskCounts.low++
    else if (r === "high") riskCounts.high++
    else if (r === "none") riskCounts.none++
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
              {(overviewTotals?.total_claims ?? destination.claims.length).toString()} claims analyzed
            </span>
            {videoAnalyzed ? (
              <span className="rounded-full bg-white/10 text-gray-200 px-3 py-1 text-xs border border-white/10">
                {videoAnalyzed} videos analyzed
              </span>
            ) : null}
            {(topNarrative?.cluster_size ?? destination.cluster_size) ? (
              <span className="rounded-full bg-purple-500/15 text-purple-200 px-3 py-1 text-xs border border-purple-400/30">
                {topNarrative?.cluster_size ?? destination.cluster_size} clustered narratives
              </span>
            ) : null}
            {(topNarrative?.computed_at || destination.computed_at) ? (
              <span className="rounded-full bg-white/10 text-gray-200 px-3 py-1 text-xs border border-white/10">
                Updated {new Date(topNarrative?.computed_at ?? destination.computed_at ?? "").toLocaleDateString()}
              </span>
            ) : null}
          </div>

          <div className="bg-[#E4CAFF] rounded-2xl w-full px-10 py-10 font-light mt-10">
            <h1 className="text-4xl font-light leading-tight text-black">{destination.name}</h1>
            <p className="text-base text-black max-w-3xl pt-5">
              {destination.blurb || "No summary available yet for this destination."}
            </p>
          </div>
        </header>

        {/* Metrics */}
        <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-7">
          <Metric label="Claims analyzed" value={(overviewTotals?.total_claims ?? destination.claims.length).toString()} />
          <Metric label="Narratives" value={(overviewTotals?.total_narratives ?? 0).toString()} />
          <Metric label="Videos analyzed" value={(videoAnalyzed ?? 0).toString()} />
          <Metric label="Low risk claims" value={riskCounts.low.toString()} />
          <Metric label="Medium risk claims" value={riskCounts.medium.toString()} />
          <Metric label="High risk claims" value={riskCounts.high.toString()} />
          <Metric label="No risk claims" value={riskCounts.none.toString()} />
        </section>

        {/* Top claim */}
        {(topClaim?.claim_text || destination.top_claim) && (
          <section className="space-y-3">
            <p className="text-xs uppercase tracking-[0.25em] text-gray-400">Top claim</p>
            <div className="rounded-2xl border border-purple-400/20 bg-purple-500/10 p-6 space-y-2">
              <p className="text-white text-base leading-relaxed">&quot;{topClaim?.claim_text ?? destination.top_claim}&quot;</p>
              {topClaim ? (
                <p className="text-xs text-gray-400">
                  Cluster {topClaim.cluster_size ?? 0} · Docs {topClaim.total_docs ?? 0}
                  {topClaim.computed_at ? ` · Updated ${new Date(topClaim.computed_at).toLocaleDateString()}` : ""}
                </p>
              ) : null}
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
                const isHigh = risk === "high"
                const isLow = risk === "low"
                const isNone = risk === "none"
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
                        : isNone
                        ? "border-slate-300/40 text-slate-200 bg-slate-300/10"
                        : "border-amber-300/40 text-amber-200 bg-amber-300/10"
                    }`}>
                      Risk: {claim.claim_risk || "unknown risk"}
                    </span>
                    {claim.claim_risk_extra_info ? (
                      <p className="text-xs text-gray-400">risk details: {claim.claim_risk_extra_info}</p>
                    ) : null}
                    <p className="text-sm text-gray-100 leading-snug">&quot;{claim.claim_title}&quot;</p>
                    <p className="text-xs text-gray-500 mt-auto">
                      {claim.source_id ? (
                        <Link href={`/creators/${claim.source_id}`} className="underline underline-offset-4 decoration-white/20 hover:text-gray-200">
                          {claim.source}
                        </Link>
                      ) : (
                        claim.source
                      )}
                      {claim.date ? ` · ${new Date(claim.date).toLocaleDateString()}` : ""}
                    </p>
                  </div>
                )
              })}
            </div>
          </section>
        )}

        {/* Narratives */}
        {topNarrative || overviewNarratives.length > 0 ? (
          <section className="space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.25em] text-gray-400">Narratives</p>
                <p className="text-sm text-gray-400">Recent narrative mentions from {destination.name}.</p>
              </div>
              <span className="text-xs text-gray-400">{overviewNarratives.length} shown</span>
            </div>

            <div className="relative">
              <div className="flex flex-col gap-4">
                {overviewNarratives.slice(0, 10).map((narr) => (
                  <div
                    key={narr.id}
                    className="rounded-2xl border border-white/10 bg-gradient-to-b from-[#151525] via-[#11111a] to-[#0c0c12] p-4 shadow-lg shadow-black/40"
                  >
                    <p className="text-sm text-gray-100 leading-snug">&quot;{narr.text}&quot;</p>
                    <div className="mt-3 flex flex-wrap items-center gap-2 text-[11px] text-gray-400">
                      <Link href={`/creators/${narr.source}`} className="rounded-full bg-white/10 px-2.5 py-1 hover:bg-white/15">
                        {narr.creator_name || narr.source}
                      </Link>
                      {narr.date ? (
                        <span className="rounded-full bg-white/5 px-2.5 py-1">{new Date(narr.date).toLocaleDateString()}</span>
                      ) : null}
                      {narr.video?.webpage_url ? (
                        <Link
                          href={narr.video.webpage_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="rounded-full bg-white/5 px-2.5 py-1 underline underline-offset-4 decoration-white/20 hover:text-white"
                        >
                          Source video
                        </Link>
                      ) : null}
                    </div>
                  </div>
                ))}
              </div>

              {/* TOP NARRATIVE (under list) */}
              {topNarrative ? (
                <div className="mt-8 bg-purple-300 text-black rounded-3xl p-8 shadow-2xl border border-black/10">
                  <div className="flex items-start justify-between gap-4">
                    <div className="space-y-1">
                      <p className="text-[11px] uppercase tracking-[0.25em] text-gray-700">Top Narrative</p>
                      <h2 className="text-2xl italic mb-0 leading-snug">&quot;{topNarrative.narrative}&quot;</h2>
                    </div>
                    <span className="shrink-0 rounded-full bg-black/10 px-3 py-1 text-[11px] uppercase tracking-wide text-gray-800">
                      Spotlight
                    </span>
                  </div>

                  <p className="text-sm mb-6 text-gray-700 pt-4">{topNarrative.destination ?? destination.name}</p>

                  <div className="grid grid-cols-2 gap-6 text-lg">
                    <div>
                      <div className="text-3xl font-bold">{topNarrative.cluster_size ?? 0}</div>
                      <div className="text-sm">Similar Narratives</div>
                    </div>

                    <div>
                      <div className="text-3xl font-bold">{videoAnalyzed ?? 0}</div>
                      <div className="text-sm">Videos Analyzed</div>
                    </div>

                    <div>
                      <div className="text-3xl font-bold truncate">
                        {topNarrative.source ? (
                          <Link href={`/creators/${topNarrative.source}`} className="underline underline-offset-4 decoration-black/20 hover:text-black/80">
                            {topNarrative.creator_name || topNarrative.source}
                          </Link>
                        ) : (
                          topNarrative.creator_name || "—"
                        )}
                      </div>
                      <div className="text-sm">Top Creator</div>
                    </div>

                    <div>
                      <div className="text-3xl font-bold">
                        {topNarrative.computed_at ? new Date(topNarrative.computed_at).toLocaleDateString() : "—"}
                      </div>
                      <div className="text-sm">Last Updated</div>
                    </div>
                  </div>

                  <p className="pt-6 text-sm text-gray-700">
                    <span className="font-semibold">{topNarrative.total_docs}</span> total narratives in this destination cluster.
                  </p>
                </div>
              ) : null}
            </div>
          </section>
        ) : null}
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
