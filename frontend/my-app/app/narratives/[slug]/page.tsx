import Link from "next/link"
import { notFound } from "next/navigation"

type Claim = {
  text: string
  source: string
  views: string
  engagement: string
  growth: string
}

type VideoClaim = {
  title: string
  text: string
  risk: "low" | "medium" | "high"
}

type VideoDetail = {
  title: string
  channel: string
  views: string
  published: string
  claim: string
  thumb: string
  summary: string
  sentiment: "positive" | "neutral" | "negative"
  riskCallouts: string[]
  claims: VideoClaim[]
}

type NarrativeDetail = {
  slug: string
  title: string
  summary: string
  videosAnalyzed: number
  claimsCount: number
  creatorsCount: number
  sentimentScore: string
  velocity: string
  sentiment: "positive" | "neutral" | "negative"
  topCreators: Creator[]
  claims: Claim[]
  videos: VideoDetail[]
}

type Creator = {
  name: string
  slug: string
}



const sentimentChip = (sentiment: NarrativeDetail["sentiment"]) => {
  if (sentiment === "positive") return "text-emerald-300 bg-emerald-400/10"
  if (sentiment === "negative") return "text-rose-300 bg-rose-400/10"
  return "text-amber-200 bg-amber-400/10"
}

type Params = { params: Promise<{ slug: string }> }

export default async function NarrativeDetailPage({ params }: Params) {

  
  const { slug } = await params;
  
  const res = await fetch(`/api/narratives/${slug}`)
  if (!res.ok) {
    console.error(`Failed to fetch detailed narrative ${slug}:`, res.statusText);
    notFound();
  }
  const narrative = await res.json();
  console.log("Fetched narrative detail:", narrative);

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0b0b10] via-[#0f1018] to-[#0b0b10] text-white">
      <div className="max-w-6xl mx-auto px-6 pb-16 pt-12 space-y-10">
        <div className="flex items-center gap-4 text-sm text-gray-400">
          <Link href="/narratives" className="underline underline-offset-4 decoration-white/30 hover:text-white">
            Narratives
          </Link>
          <span>›</span>
          <span className="text-gray-200">{narrative.title}</span>
        </div>

        <header className="space-y-4">
          <div className="flex flex-wrap items-center gap-3">
            {/* <span className={`rounded-full px-3 py-1 text-xs ${sentimentChip(narrative.sentiment)}`}>
              {narrative.sentiment}
            </span> */}
            {/* <span className="rounded-full bg-white/10 text-gray-200 px-3 py-1 text-xs border border-white/10">
              {narrative.velocity}
            </span> */}
            {/* <span className="rounded-full bg-white/10 text-gray-200 px-3 py-1 text-xs border border-white/10">
              {narrative.creatorsCount} creators
            </span> */}
            {/* <span className="rounded-full bg-white/10 text-gray-200 px-3 py-1 text-xs border border-white/10">
              {narrative.videosAnalyzed} videos analyzed
            </span> */}
          </div>
          <h3 className="text-sm uppercase tracking-[0.25em] text-gray-400">Narrative overview</h3>
          <h1 className="text-4xl font-semibold leading-tight">{narrative.text}</h1>
          <p className="text-base text-gray-300 max-w-3xl">{narrative.destination}</p>
        </header>

        {/* <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <MetricCard label="Videos analyzed" value={narrative.videosAnalyzed.toLocaleString()} />
          <MetricCard label="Active claims" value={narrative.claimsCount.toString()} />
          <MetricCard label="Active creators" value={narrative.creatorsCount.toString()} />
          <MetricCard label="Sentiment" value={narrative.sentimentScore} />
        </section> */}

        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-gray-400">Top creators</p>
              <p className="text-sm text-gray-400">Primary channels informing this narrative.</p>
            </div>
            <span className="text-xs text-gray-400">{narrative?.topCreators?.length ?? 0 } highlighted</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {/* {narrative.topCreators.map((creator) => ( */}
              <Link href={`/creators/${narrative.channel_id.slug}`} key={narrative.channel_id.slug} className="hover:underline hover:underline-offset-4">
                <span className="rounded-full bg-white/5 border border-white/10 px-3 py-2 text-xs text-gray-200">
                  {narrative.creator_name}
                </span>
              </Link>
             {/* ))} */}
          </div>
        </section>

        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-gray-400">Claims carousel</p>
              <p className="text-sm text-gray-400">High-signal claims clustered for this narrative.</p>
            </div>
            <span className="text-xs text-gray-400">{narrative?.related_claims?.length ?? 0} shown</span>
          </div>

          <div className="flex gap-4 overflow-x-auto pb-2">
            {narrative.related_claims.map((claim, idx) => (
              <div
                key={idx}
                className="min-w-[240px] max-w-[260px] rounded-2xl border border-white/10 bg-gradient-to-b from-[#151525] via-[#11111a] to-[#0c0c12] p-4 shadow-lg shadow-black/40"
              >
                <p className="text-sm text-gray-200 mb-3">“{claim.claim_text}”</p>
                <div className="text-xs text-gray-400 space-y-1">
                  <p><span className="text-gray-500">Source:</span> {claim.source}</p>
                  <p><span className="text-gray-500">Risk:</span> {claim.claim_risk}</p>
                  <p><span className="text-gray-500">Date:</span> {claim.date}</p>
                  {/* <p><span className="text-gray-500">Engagement:</span> {claim.engagement}</p>
                  <p><span className="text-gray-500">Growth:</span> {claim.growth}</p> */}
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="space-y-3">
            <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-gray-400">Related Videos</p>
              <p className="text-sm text-gray-400">Each video contributed a claim; together they form this narrative.</p>
            </div>
            <span className="text-xs text-gray-400">{narrative?.videos?.length ?? 0} shown</span>
          </div>
          <div className="flex gap-4 overflow-x-auto pb-2">
            {narrative.related_claims.map((claim, idx) => (
              <div
                key={idx}
                className="min-w-[260px] max-w-[280px] rounded-2xl border border-white/10 bg-gradient-to-b from-[#151525] via-[#11111a] to-[#0c0c12] shadow-lg shadow-black/40 overflow-hidden"
              >
                <div className="h-40 w-full bg-gray-800 overflow-hidden">
                  {/* <img src={video.thumb} alt={video.title} className="h-full w-full object-cover" /> */}
                </div>
                <div className="p-4 space-y-2">
                  <p className="text-sm font-semibold text-white line-clamp-2">{claim.claim_text}</p>
                  <p className="text-xs text-gray-300">{claim.claim_risk}</p>
                  <p className="text-[11px] text-gray-400">{claim.date} • {claim.date}</p>
                  <p className="text-xs text-blue-200 line-clamp-2">Claim: {claim.claim_text}</p>
                </div>
              </div>
            ))}
          </div>
        </section>
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
