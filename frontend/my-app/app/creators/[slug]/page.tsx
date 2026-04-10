import Link from "next/link"
import { notFound } from "next/navigation"

type ContentCreator = {
  slug: string
  name: string
  region: "Americas" | "EMEA" | "APAC"
  domain: string
  subscribers: number
  monthlyViews: number
  contentType: "Travel" | "Food" | "Lifestyle/Vlog" | "Wellness" | "Tech" | "Entertainment" | "News"
  videos: { title: string; views: string; img: string; link: string }[]
  profilePhoto?: string
  commentVolume30d: number
  sentiment: { positive: number; neutral: number; negative: number }
  topThemes: string[]
  highlightedComments: string[]
  risk: RiskStats[]
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type RiskStats = {
  riskTitle: string
  riskDescription: string
}

type ApiContentCreator = {
  channel_id: string
  name: string
  subscriber_count: number
  views: number
  join_date?: string
  top_claim?: string | null
  cluster_size?: number | null
  computed_at?: string | null
  claims?: {
    destination: string
    claim_text: string
    claim_risk: string
    date: string
  }[]
}

const creators: ContentCreator[] = []

const formatNumber = (value: number) =>
  value.toLocaleString("en-US", { notation: "compact", maximumFractionDigits: 1 })

type Params = { params: Promise<{ slug: string }> }

export default async function CreatorDetailPage({ params }: Params) {
  const { slug } = await params

  let creator: ContentCreator | undefined

  try {
    const res = await fetch(`${API_BASE}/api/creators/${slug}`, { cache: "no-store" })
    if (res.ok) {
      const apiCreator: ApiContentCreator = await res.json()
      creator = mapApiCreatorToContentCreator(apiCreator)
      console.log("Fetched creator from API:", creator)
    }
  } catch (err) {
    console.error(`Failed to fetch creator ${slug}:`, err)
  }

  // Fallback to static seed data if API is missing
  if (!creator) {
    creator = creators.find((c) => c.slug === slug)
  }

  if (!creator) {
    notFound()
  }

  const avatar = creator.profilePhoto ?? creator.videos[0]?.img ?? ""

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0b0b10] via-[#0f1018] to-[#0b0b10] text-white">
      <div className="max-w-6xl mx-auto px-6 pb-16 pt-12 space-y-10">
        <div className="flex items-center gap-2 text-sm text-gray-400">
          <Link href="/creators" className="underline underline-offset-4 decoration-white/30 hover:text-white">
            Creators
          </Link>
          <span className="text-gray-600">/</span>
          <span className="text-gray-200">{creator.name}</span>
        </div>

        <header className="space-y-4">
          <div className="flex items-start gap-4">
            <div className="h-16 w-16 rounded-full border border-white/10 bg-gradient-to-br from-purple-500/30 to-indigo-500/30 overflow-hidden flex items-center justify-center">
              {avatar ? <img src={avatar} alt={creator.name} className="h-full w-full object-cover" /> : <span className="text-xs text-gray-100">YT</span>}
            </div>
            <div className="space-y-3">
              <div className="flex flex-wrap items-center gap-2 text-[11px] uppercase tracking-wide text-gray-200">
                <span className="rounded-full bg-emerald-500/15 text-emerald-200 px-3 py-1">{creator.region}</span>
                <span className="rounded-full bg-white/10 px-3 py-1">{creator.contentType}</span>
                <span className="rounded-full bg-white/10 px-3 py-1">{formatNumber(creator.subscribers)} subs</span>
                <span className="rounded-full bg-white/10 px-3 py-1">{formatNumber(creator.monthlyViews)} monthly views</span>
                <span className="rounded-full bg-white/10 px-3 py-1">{creator.videos.length} featured videos</span>
              </div>
              <h1 className="text-4xl font-semibold leading-tight">{creator.name}</h1>
              <p className="text-base text-gray-300 max-w-3xl">{creator.domain}</p>
            </div>
          </div>
        </header>

        <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <MetricCard label="Subscribers" value={formatNumber(creator.subscribers)} />
          <MetricCard label="Monthly views" value={formatNumber(creator.monthlyViews)} />
          <MetricCard label="Region" value={creator.region} />
          <MetricCard label="Content type" value={creator.contentType} />
        </section>

        <section className="space-y-3">
          <div>
            <p className="text-xs uppercase tracking-[0.25em] text-gray-400">Risk & compliance</p>
            <p className="text-sm text-gray-400">Last 12 months of safety signals.</p>
          </div>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {creator.risk.map((risk) => (
              <MetricCard key={risk.riskTitle} label={risk.riskTitle} value={risk.riskDescription} />
            ))}
          </div>
        </section>

        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-gray-400">Audience comments & sentiment</p>
              <p className="text-sm text-gray-400">Last 30 days of comment velocity and tone.</p>
            </div>
            <span className="text-xs text-gray-300">{formatNumber(creator.commentVolume30d)} comments</span>
          </div>

          <div className="grid gap-4 lg:grid-cols-[2fr_1fr]">
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
            </div>

            <div className="rounded-2xl border border-white/10 bg-gradient-to-b from-[#1d1524] via-[#14101a] to-[#0b0b10] p-5 shadow-lg shadow-black/40 space-y-3">
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
        </section>

        {/* RECENT VIDEOS SECTION */}
        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-gray-400">Recent videos</p>
              <p className="text-sm text-gray-400">Sample of the creator’s recent uploads.</p>
            </div>
            <span className="text-xs text-gray-400">{creator.videos.length} videos</span>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {creator.videos.map((video) => (
              <Link
                key={video.title}
                href={video.link}
                className="group rounded-2xl border border-white/10 bg-gradient-to-b from-[#151525] via-[#11111a] to-[#0c0c12] shadow-lg shadow-black/40 overflow-hidden transition hover:-translate-y-1 hover:border-white/20"
              >
                <div className="h-40 w-full bg-gray-800 overflow-hidden">
                  <img
                    src={video.img}
                    alt={video.title}
                    className="h-full w-full object-cover transition duration-300 group-hover:scale-105"
                  />
                </div>
                <div className="p-4 space-y-2">
                  <p className="text-sm font-semibold text-white line-clamp-2">{video.title}</p>
                  <p className="text-xs text-gray-300">{video.views}</p>
                  <p className="text-[11px] text-gray-400">Tap to view source</p>
                </div>
              </Link>
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
