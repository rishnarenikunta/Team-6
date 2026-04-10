"use client"
import Link from "next/link"
import { useEffect, useState } from "react"
import { useParams } from "next/navigation"


type ApiContentCreatorResponse = {
  channel_id: string
  creator_name: string
  subscriber_count: number
  views: number
  comment_volume: number
  videos: {
    video_id: string
    title: string
    view_count: number
    like_count: number
    comment_count: number
    webpage_url: string
    upload_date: string
  }[]
  trending_narratives: {
    narrative_id: string
    narrative: string
    cluster_size: number
    video_id: string
    computed_at: string
    total_docs: number
  }[]
  trending_claims: {
    claim_id: string
    claim_text: string
    cluster_size: number
    computed_at: string
    total_docs: number
  }[]
}

const formatNumber = (value: number) =>
  value.toLocaleString("en-US", { notation: "compact", maximumFractionDigits: 1 })

export default function CreatorDetailPage() {
  const params = useParams<{ slug: string }>()
  const slug = params?.slug

  const [creator, setCreator] = useState<ApiContentCreatorResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    if (!slug) return
    async function fetchCreator() {
      try {
        const res = await fetch(`/api/creators/${slug}`, { cache: "no-store" })
        if (!res.ok) throw new Error(`API error ${res.status}`)
        const data: ApiContentCreatorResponse = await res.json()
        if (!cancelled) setCreator(data)
      } catch (err: any) {
        if (!cancelled) setError(err.message ?? "Failed to fetch creator")
        console.error(`Failed to fetch creator ${slug}:`, err)
      }
    }
    fetchCreator()
    return () => {
      cancelled = true
    }
  }, [slug])

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-[#0b0b10] via-[#0f1018] to-[#0b0b10] text-white flex items-center justify-center">
        <p className="text-sm text-gray-300">Error loading creator: {error}</p>
      </div>
    )
  }

  if (!creator) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-[#0b0b10] via-[#0f1018] to-[#0b0b10] text-white flex items-center justify-center">
        <p className="text-sm text-gray-300">Loading creator…</p>
      </div>
    )
  }

  const avatar = "/images/placeholder.jpg"

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0b0b10] via-[#0f1018] to-[#0b0b10] text-white">
      <div className="max-w-6xl mx-auto px-6 pb-16 pt-12 space-y-10">
        <div className="flex items-center gap-2 text-sm text-gray-400">
          <Link href="/creators" className="underline underline-offset-4 decoration-white/30 hover:text-white">
            Creators
          </Link>
          <span className="text-gray-600">/</span>
          <span className="text-gray-200">{creator.creator_name}</span>
        </div>

        <header className="space-y-4">
          <div className="flex items-start gap-4">
            <div className="h-16 w-16 rounded-full border border-white/10 bg-gradient-to-br from-purple-500/30 to-indigo-500/30 overflow-hidden flex items-center justify-center">
              {avatar ? <img src={avatar} alt={creator.creator_name} className="h-full w-full object-cover" /> : <span className="text-xs text-gray-100">YT</span>}
            </div>
            <div className="space-y-3">
              <div className="flex flex-wrap items-center gap-2 text-[11px] uppercase tracking-wide text-gray-200">
                <span className="rounded-full bg-emerald-500/15 text-emerald-200 px-3 py-1">{formatNumber(creator.subscriber_count)} subs</span>
                <span className="rounded-full bg-white/10 px-3 py-1">{formatNumber(creator.views)} views</span>
                <span className="rounded-full bg-white/10 px-3 py-1">{creator.videos.length} videos</span>
                <span className="rounded-full bg-white/10 px-3 py-1">{creator.trending_claims.length} claims</span>
                <span className="rounded-full bg-white/10 px-3 py-1">{creator.trending_narratives.length} narratives</span>
              </div>
              <h1 className="text-4xl font-semibold leading-tight">{creator.creator_name}</h1>
              <p className="text-base text-gray-300 max-w-3xl">{creator.videos.length} recent videos</p>
            </div>
          </div>
        </header>

        <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <MetricCard label="Subscribers" value={formatNumber(creator.subscriber_count)} />
          <MetricCard label="Views" value={formatNumber(creator.views)} />
          <MetricCard label="Comments (30d)" value={formatNumber(creator.comment_volume)} />
          <MetricCard label="Videos" value={`${creator.videos.length}`} />
        </section>

        {/* <section className="space-y-3">
          <div>
            <p className="text-xs uppercase tracking-[0.25em] text-gray-400">Risk & compliance</p>
            <p className="text-sm text-gray-400">Last 12 months of safety signals.</p>
          </div>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {creator.risk.map((risk) => (
              <MetricCard key={risk.riskTitle} label={risk.riskTitle} value={risk.riskDescription} />
            ))}
          </div>
        </section> */}

        {/* <section className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-gray-400">Audience comments & sentiment</p>
              <p className="text-sm text-gray-400">Last 30 days of comment velocity and tone.</p>
            </div>
            <span className="text-xs text-gray-300">{formatNumber(creator.commentVolume30d)} comments</span>
          </div> */}

          {/* <div className="grid gap-4 lg:grid-cols-[2fr_1fr]">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-5 shadow-inner shadow-black/30 space-y-4">
              <div className="space-y-3">
                <SentimentRow label="Positive" value={creator.sentiment.positive} color="from-emerald-400/90 to-emerald-500/80" />
                <SentimentRow label="Neutral" value={creator.sentiment.neutral} color="from-slate-300/90 to-slate-400/70" />
                <SentimentRow label="Negative" value={creator.sentiment.negative} color="from-rose-400/90 to-rose-500/80" />
              </div>

              <div className="grid gap-3 sm:grid-cols-2">
                {creator.highlightedComments.map((comment) => (
                  <div key={comment} className="rounded-xl border border-white/10 bg-[#0f0f18] p-3 text-sm text-gray-200">
                    <p className="text-[11px] uppercase tracking-wide text-gray-400 mb-1">Signal comment</p>
                    <p className="leading-relaxed">“{comment}”</p>
                  </div>
                ))}
              </div>
            </div> */}

            {/* <div className="rounded-2xl border border-white/10 bg-gradient-to-b from-[#1d1524] via-[#14101a] to-[#0b0b10] p-5 shadow-lg shadow-black/40 space-y-3">
              <p className="text-[11px] uppercase tracking-wide text-gray-300">Top themes</p>
              <div className="flex flex-wrap gap-2">
                {creator.topThemes.map((theme) => (
                  <span key={theme} className="rounded-full bg-white/10 px-3 py-1 text-xs text-gray-100">
                    {theme}
                  </span>
                ))}
              </div>
              <p className="text-xs text-gray-400">
                Themes are extracted from high-engagement comments and weighted by recency to surface what the audience asks for next.
              </p>
            </div>
          </div>
        </section> */}

        {/* RECENT VIDEOS SECTION */}
        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-gray-400">Recent videos</p>
              <p className="text-sm text-gray-400">Sample of the creator’s recent uploads.</p>
            </div>
            <span className="text-xs text-gray-400">{creator?.videos.length ?? 0} videos</span>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {creator?.videos?.map((video) => (
              <Link
                key={video.video_id}
                href={video.webpage_url}
                className="group rounded-2xl border border-white/10 bg-gradient-to-b from-[#151525] via-[#11111a] to-[#0c0c12] shadow-lg shadow-black/40 overflow-hidden transition hover:-translate-y-1 hover:border-white/20"
              >
                <div className="h-40 w-full bg-gray-800 overflow-hidden">
                  <div className="h-full w-full bg-[#1f1f2b] flex items-center justify-center text-xs text-gray-400">
                    {video.upload_date || "Recent video"}
                  </div>
                </div>
                <div className="p-4 space-y-2">
                  <p className="text-sm font-semibold text-white line-clamp-2">{video.title}</p>
                  <p className="text-xs text-gray-300">
                    {formatNumber(video.view_count)} views · {formatNumber(video.comment_count)} comments · {formatNumber(video.like_count)} likes
                  </p>
                  <p className="text-[11px] text-gray-400">Uploaded: {video.upload_date || "—"}</p>
                </div>
              </Link>
            ))}
          </div>
        </section>

        {/* TRENDING NARRATIVES */}
        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-gray-400">Trending narratives</p>
              <p className="text-sm text-gray-400">Top narratives linked to this creator.</p>
            </div>
            <span className="text-xs text-gray-400">{creator?.trending_narratives?.length ?? 0} items</span>
          </div>
          <div className="space-y-2">
            {creator?.trending_narratives?.map((narr) => (
              <div key={narr.narrative_id} className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-gray-200">
                <div className="flex justify-between items-center">
                  <Link href={`/narratives/${narr.narrative_id}`} className="font-semibold hover:text-white">
                    {narr.narrative}
                  </Link>
                  <span className="text-[11px] text-gray-400">Cluster {narr.cluster_size}</span>
                </div>
                <p className="text-[11px] text-gray-400">Computed: {narr.computed_at || "—"} · Docs: {narr.total_docs ?? 0}</p>
              </div>
            ))}
          </div>
        </section>

        {/* TRENDING CLAIMS */}
        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-gray-400">Trending claims</p>
              <p className="text-sm text-gray-400">High-signal claims tied to this creator.</p>
            </div>
            <span className="text-xs text-gray-400">{creator?.trending_claims?.length ?? 0} items</span>
          </div>
          <div className="space-y-2">
            {creator?.trending_claims?.map((claim) => (
              <div key={claim.claim_id} className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-gray-200">
                <p className="font-semibold text-white line-clamp-2">{claim.claim_text}</p>
                <p className="text-[11px] text-gray-400">Cluster {claim.cluster_size} · Docs {claim.total_docs ?? 0}</p>
                <p className="text-[11px] text-gray-500">Computed: {claim.computed_at || "—"}</p>
              </div>
            ))}
          </div>
        </section>

        {/* <section className="rounded-2xl border border-white/10 bg-white/5 p-6 shadow-inner shadow-black/30 space-y-3">
          <h3 className="text-sm uppercase tracking-[0.25em] text-gray-400">Collaboration notes</h3>
          <p className="text-gray-200 text-sm">
            This creator demonstrates consistent disclosure, steady month-over-month growth, and strong engagement within their niche.
            Consider bundling mid-roll + community posts for best conversions.
          </p>
          <div className="flex flex-wrap gap-2 text-xs text-gray-300">
            <span className="rounded-full bg-white/10 px-3 py-1">Disclosure: clean</span>
            <span className="rounded-full bg-white/10 px-3 py-1">Formats: long + short</span>
            <span className="rounded-full bg-white/10 px-3 py-1">Requests: open</span>
          </div>
        </section> */}
        
      </div>
    </div>
  )
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-4 shadow-inner shadow-black/30">
      <p className="text-[11px] uppercase tracking-wide text-gray-400">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-white">{value}</p>
    </div>
  )
}

function SentimentRow({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-xs text-gray-300">
        <span>{label}</span>
        <span className="text-gray-100 font-semibold">{value}%</span>
      </div>
      <div className="h-2 rounded-full bg-white/10 overflow-hidden">
        <div className={`h-full bg-gradient-to-r ${color}`} style={{ width: `${Math.min(100, value)}%` }} />
      </div>
    </div>
  )
}

function mapApiCreatorToContentCreator(api: ApiContentCreator): ContentCreator {
  const defaultSentiment = { positive: 60, neutral: 30, negative: 10 }
  const claims = api.claims ?? []
  const topThemes =
    claims.length > 0
      ? Array.from(new Set(claims.map((c) => c.destination || "Travel"))).slice(0, 6)
      : ["Travel"]
  const highlightedComments =
    claims.length > 0
      ? claims.slice(0, 2).map((c) => c.claim_text)
      : ["No highlighted comments."]
  const videos =
    claims.length > 0
      ? claims.slice(0, 3).map((c) => ({
          title: c.claim_text,
          views: `${formatNumber(api.views ?? 0)} views`,
          img: "/images/placeholder.jpg",
          link: "#",
        }))
      : [
          {
            title: api.top_claim || "Recent upload",
            views: `${formatNumber(api.views ?? 0)} views`,
            img: "/images/placeholder.jpg",
            link: "#",
          },
        ]

  return {
    slug: api.channel_id ?? "unknown",
    name: api.name ?? "Unknown creator",
    region: "Americas",
    domain: "Travel creator",
    subscribers: api.subscriber_count ?? 0,
    monthlyViews: api.views ?? 0,
    contentType: "Travel",
    videos: videos.length > 0 ? videos : [],
    profilePhoto: undefined,
    commentVolume30d: api.cluster_size ?? 0,
    sentiment: defaultSentiment,
    topThemes,
    highlightedComments: highlightedComments.length > 0 ? highlightedComments : ["No highlighted comments."],
    risk: [
      { riskTitle: "Avg. Sentiment", riskDescription: "+60% positive" },
      { riskTitle: "Risk Band", riskDescription: "Low" },
    ],
  }
}
