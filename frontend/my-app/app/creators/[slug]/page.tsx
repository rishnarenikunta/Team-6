"use client"
import Link from "next/link"
import { useEffect, useState } from "react"
import { useParams } from "next/navigation"


type ApiContentCreatorResponse = {
  channel_id: string
  creator_name: string
  subscriber_count: number
  views: number
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

const formatPercent = (value: number) =>
  new Intl.NumberFormat("en-US", { style: "percent", maximumFractionDigits: 1 }).format(value)

function parseDateSafe(value: string): Date | null {
  const parsed = new Date(value)
  return Number.isNaN(parsed.getTime()) ? null : parsed
}

function getYouTubeVideoId(webpageUrl: string): string | null {
  try {
    const url = new URL(webpageUrl)
    const host = url.hostname.replace(/^www\./, "")

    if (host === "youtu.be") {
      const id = url.pathname.split("/").filter(Boolean)[0]
      return id || null
    }

    if (host.endsWith("youtube.com")) {
      const watchId = url.searchParams.get("v")
      if (watchId) return watchId

      const pathParts = url.pathname.split("/").filter(Boolean)
      // /shorts/<id>, /embed/<id>, /live/<id>
      const candidates = ["shorts", "embed", "live"]
      const markerIndex = pathParts.findIndex((part) => candidates.includes(part))
      if (markerIndex !== -1) return pathParts[markerIndex + 1] || null

      // fallback: /<id> (rare)
      if (pathParts.length === 1) return pathParts[0] || null
    }

    return null
  } catch {
    return null
  }
}

function getYouTubeThumbnailUrl(webpageUrl: string): string | null {
  const videoId = getYouTubeVideoId(webpageUrl)
  return videoId ? `https://i.ytimg.com/vi/${videoId}/hqdefault.jpg` : null
}

export default function CreatorDetailPage() {
  const params = useParams<{ slug: string }>()
  const slug = params?.slug

  const [creator, setCreator] = useState<ApiContentCreatorResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [pfp, setPfp] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    if (!slug) return
    async function fetchCreator() {
      try {
        const res = await fetch(`/api/creators/${slug}`, { cache: "no-store" })
        if (!res.ok) throw new Error(`API error ${res.status}`)
        const data: ApiContentCreatorResponse = await res.json()
        if (!cancelled) setCreator(data)
        console.log("Fetched creator data:", data)
        const pfpRes = await fetch(`/api/${data.channel_id}/pfp`, { cache: "no-store" })
        if (pfpRes.ok) {
          const pfpData = await pfpRes.json()
          if (!cancelled) setPfp(pfpData.pfp_url)
        }
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : "Failed to fetch creator"
        if (!cancelled) setError(message)
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

  const avatar = pfp || (creator.videos.length > 0 ? `https://i.ytimg.com/vi/${creator.videos[0].video_id}/hqdefault.jpg` : null)
  const recentVideoViews = creator.videos.reduce((sum, video) => sum + (Number.isFinite(video.view_count) ? video.view_count : 0), 0)
  const recentVideoLikes = creator.videos.reduce((sum, video) => sum + (Number.isFinite(video.like_count) ? video.like_count : 0), 0)
  const recentVideoComments = creator.videos.reduce((sum, video) => sum + (Number.isFinite(video.comment_count) ? video.comment_count : 0), 0)
  const avgViewsPerVideo = creator.videos.length ? recentVideoViews / creator.videos.length : 0
  const engagementRate = recentVideoViews ? (recentVideoLikes + recentVideoComments) / recentVideoViews : 0
  const likeRate = recentVideoViews ? recentVideoLikes / recentVideoViews : 0
  const commentRate = recentVideoViews ? recentVideoComments / recentVideoViews : 0
  const topVideo = creator.videos.reduce<(typeof creator.videos)[number] | null>(
    (best, current) => (best && best.view_count >= current.view_count ? best : current),
    creator.videos[0] ?? null,
  )
  const uploadDates = creator.videos
    .map((video) => parseDateSafe(video.upload_date))
    .filter((date): date is Date => Boolean(date))
  const latestUpload = uploadDates.length ? new Date(Math.max(...uploadDates.map((date) => date.getTime()))) : null
  const oldestUpload = uploadDates.length ? new Date(Math.min(...uploadDates.map((date) => date.getTime()))) : null
  const latestUploadDaysAgo = latestUpload ? Math.max(0, Math.floor((Date.now() - latestUpload.getTime()) / 86_400_000)) : null
  const creatorViews = creator.views > 0 ? creator.views : recentVideoViews
  const viewsLabel = creator.views > 0 ? "Views" : "Views (recent)"
  const viewsTitle = creator.views > 0 ? "Total views from API" : "API returned 0; showing sum of recent video views"

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
                <span title={viewsTitle} className="rounded-full bg-white/10 px-3 py-1">{formatNumber(creatorViews)} views</span>
                <span className="rounded-full bg-white/10 px-3 py-1">{creator.videos.length} videos</span>
                {/* <span className="rounded-full bg-white/10 px-3 py-1">{creator.trending_claims.length} claims</span> */}
                {/* <span className="rounded-full bg-white/10 px-3 py-1">{creator.trending_narratives.length} narratives</span> */}
              </div>
              <h1 className="text-4xl font-semibold leading-tight">{creator.creator_name}</h1>
              <p className="text-base text-gray-300 max-w-3xl">{creator.videos.length} recent videos</p>
            </div>
          </div>
        </header>

        <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          <MetricCard label="Subscribers" value={formatNumber(creator.subscriber_count)} />
          <MetricCard label={viewsLabel} value={formatNumber(creatorViews)} />
          <MetricCard label="Videos" value={`${creator.videos.length}`} />
          <MetricCard label="Avg views/video" value={formatNumber(Math.round(avgViewsPerVideo))} />
          <MetricCard label="Engagement (recent)" value={formatPercent(engagementRate)} />
        </section>

        <section className="grid gap-4 lg:grid-cols-2">
          <div className="rounded-2xl border border-white/10 bg-white/5 p-5 shadow-inner shadow-black/30 space-y-2">
            <p className="text-[11px] uppercase tracking-wide text-gray-400">Recent engagement</p>
            <div className="flex flex-wrap gap-2 text-[11px] uppercase tracking-wide text-gray-200">
              <span className="rounded-full bg-white/10 px-3 py-1">{formatNumber(recentVideoLikes)} likes</span>
              <span className="rounded-full bg-white/10 px-3 py-1">{formatNumber(recentVideoComments)} comments</span>
            </div>
            <p className="text-sm text-gray-300">
              Like rate {formatPercent(likeRate)} · Comment rate {formatPercent(commentRate)}
            </p>
            <p className="text-[11px] text-gray-500">Rates are computed from the recent videos list on this page.</p>
          </div>

          <div className="rounded-2xl border border-white/10 bg-white/5 p-5 shadow-inner shadow-black/30 space-y-2">
            <p className="text-[11px] uppercase tracking-wide text-gray-400">Upload cadence (recent)</p>
            <div className="flex flex-wrap gap-2 text-[11px] uppercase tracking-wide text-gray-200">
              <span className="rounded-full bg-white/10 px-3 py-1">
                Last upload {latestUploadDaysAgo === null ? "—" : `${latestUploadDaysAgo}d ago`}
              </span>
              <span className="rounded-full bg-white/10 px-3 py-1">
                Window{" "}
                {oldestUpload && latestUpload
                  ? `${oldestUpload.toLocaleDateString()} – ${latestUpload.toLocaleDateString()}`
                  : "—"}
              </span>
            </div>
            {topVideo ? (
              <p className="text-sm text-gray-300">
                Top recent video:{" "}
                <Link href={topVideo.webpage_url} className="underline underline-offset-4 decoration-white/30 hover:text-white">
                  {topVideo.title}
                </Link>{" "}
                · {formatNumber(topVideo.view_count)} views
              </p>
            ) : (
              <p className="text-sm text-gray-300">Top recent video: —</p>
            )}
            <p className="text-[11px] text-gray-500">Dates reflect the recent videos list on this page.</p>
          </div>
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

        {/* TRENDING NARRATIVES */}
        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-gray-400">Trending narratives</p>
              <p className="text-sm text-gray-400">Top narratives linked to this creator.</p>
            </div>
            <span className="text-xs text-gray-400">{creator?.trending_narratives?.length ?? 0} items</span>
          </div>
          {creator?.trending_narratives?.length ? (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {creator.trending_narratives.map((narr) => (
                <Link
                  key={narr.narrative_id}
                  href={`/narratives/${narr.narrative_id}`}
                  className="group rounded-2xl border border-white/10 bg-gradient-to-b from-[#151525] via-[#11111a] to-[#0c0c12] p-4 shadow-lg shadow-black/40 transition hover:-translate-y-0.5 hover:border-white/20"
                >
                  <div className="flex items-start justify-between gap-3">
                    <p className="text-sm font-semibold text-white leading-snug line-clamp-3 group-hover:text-[#E4CAFF]">
                      {narr.narrative}
                    </p>
                    <span className="shrink-0 rounded-full bg-white/10 px-2.5 py-1 text-[11px] text-gray-200">
                      Cluster {narr.cluster_size}
                    </span>
                  </div>
                  <div className="mt-3 flex flex-wrap gap-2 text-[11px] text-gray-400">
                    <span className="rounded-full bg-white/5 px-2.5 py-1">Docs {narr.total_docs ?? 0}</span>
                    <span className="rounded-full bg-white/5 px-2.5 py-1">
                      Computed {narr.computed_at || "—"}
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <div className="rounded-2xl border border-dashed border-white/15 bg-white/5 px-4 py-3 text-sm text-gray-300">
              No trending narratives available yet.
            </div>
          )}
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
          {creator?.trending_claims?.length ? (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {creator.trending_claims.map((claim) => (
                <div
                  key={claim.claim_id}
                  className="rounded-2xl border border-white/10 bg-gradient-to-b from-[#151525] via-[#11111a] to-[#0c0c12] p-4 shadow-lg shadow-black/40 transition hover:-translate-y-0.5 hover:border-white/20"
                >
                  <p className="text-sm font-semibold text-white leading-snug line-clamp-3">“{claim.claim_text}”</p>
                  <div className="mt-3 flex flex-wrap gap-2 text-[11px] text-gray-400">
                    <span className="rounded-full bg-white/10 px-2.5 py-1">Cluster {claim.cluster_size}</span>
                    <span className="rounded-full bg-white/10 px-2.5 py-1">Docs {claim.total_docs ?? 0}</span>
                    <span className="rounded-full bg-white/5 px-2.5 py-1">Computed {claim.computed_at || "—"}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="rounded-2xl border border-dashed border-white/15 bg-white/5 px-4 py-3 text-sm text-gray-300">
              No trending claims available yet.
            </div>
          )}
        </section>

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
            {creator?.videos?.map((video) => {
              const thumbnailUrl = getYouTubeThumbnailUrl(video.webpage_url)
              return (
                <Link
                  key={video.video_id}
                  href={video.webpage_url}
                  className="group rounded-2xl border border-white/10 bg-gradient-to-b from-[#151525] via-[#11111a] to-[#0c0c12] shadow-lg shadow-black/40 overflow-hidden transition hover:-translate-y-1 hover:border-white/20"
                >
                  <div className="h-40 w-full bg-gray-800 overflow-hidden">
                    {thumbnailUrl ? (
                      <img
                        src={thumbnailUrl}
                        alt={video.title}
                        className="h-full w-full object-cover transition duration-300 group-hover:scale-[1.02]"
                        loading="lazy"
                      />
                    ) : (
                      <div className="h-full w-full bg-[#1f1f2b] flex items-center justify-center text-xs text-gray-400">
                        {video.upload_date || "Recent video"}
                      </div>
                    )}
                  </div>
                  <div className="p-4 space-y-2">
                    <p className="text-sm font-semibold text-white line-clamp-2">{video.title}</p>
                    <p className="text-xs text-gray-300">
                      {formatNumber(video.view_count)} views · {formatNumber(video.comment_count)} comments ·{" "}
                      {formatNumber(video.like_count)} likes
                    </p>
                    <p className="text-[11px] text-gray-400">Uploaded: {video.upload_date || "—"}</p>
                  </div>
                </Link>
              )
            })}
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

// function mapApiCreatorToContentCreator(api: ApiContentCreator): ContentCreator {
//   const defaultSentiment = { positive: 60, neutral: 30, negative: 10 }
//   const claims = api.claims ?? []
//   const topThemes =
//     claims.length > 0
//       ? Array.from(new Set(claims.map((c) => c.destination || "Travel"))).slice(0, 6)
//       : ["Travel"]
//   const highlightedComments =
//     claims.length > 0
//       ? claims.slice(0, 2).map((c) => c.claim_text)
//       : ["No highlighted comments."]
//   const videos =
//     claims.length > 0
//       ? claims.slice(0, 3).map((c) => ({
//           title: c.claim_text,
//           views: `${formatNumber(api.views ?? 0)} views`,
//           img: "/images/placeholder.jpg",
//           link: "#",
//         }))
//       : [
//           {
//             title: api.top_claim || "Recent upload",
//             views: `${formatNumber(api.views ?? 0)} views`,
//             img: "/images/placeholder.jpg",
//             link: "#",
//           },
//         ]

//   return {
//     slug: api.channel_id ?? "unknown",
//     name: api.name ?? "Unknown creator",
//     region: "Americas",
//     domain: "Travel creator",
//     subscribers: api.subscriber_count ?? 0,
//     monthlyViews: api.views ?? 0,
//     contentType: "Travel",
//     videos: videos.length > 0 ? videos : [],
//     profilePhoto: undefined,
//     commentVolume30d: api.cluster_size ?? 0,
//     sentiment: defaultSentiment,
//     topThemes,
//     highlightedComments: highlightedComments.length > 0 ? highlightedComments : ["No highlighted comments."],
//     risk: [
//       { riskTitle: "Avg. Sentiment", riskDescription: "+60% positive" },
//       { riskTitle: "Risk Band", riskDescription: "Low" },
//     ],
//   }
// }
