import Link from "next/link"
import { notFound } from "next/navigation"

const API_BASE = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

// ── Types ─────────────────────────────────────────────────────────────────────

type ApiNarrativesResponse = {
  slug: string
  narrative_id: string
  video_id: string
  destination: string
  channel_id: string
  narrative_text: string
  date: string
  claims: {
    claim_text: string
    claim_risk: "Low" | "Medium" | "High"
    source: string
    date: string
  }[]
  metadata: {
    tags: string[]
    sentiment_score: number | null
    sentiment: "positive" | "neutral" | "negative" | null
    title: string
    upload_date: string
    webpage_url: string
    risk_callouts: string[]
  }
  video_stats: {
    view_count: number | null
    like_count: number | null
    comment_count: number | null
  }
}

type Params = { params: Promise<{ slug: string }> }

// ── Helpers ───────────────────────────────────────────────────────────────────

const sentimentChip = (sentiment: "positive" | "neutral" | "negative" | null) => {
  if (sentiment === "positive") return "text-emerald-300 bg-emerald-400/10"
  if (sentiment === "negative") return "text-rose-300 bg-rose-400/10"
  return "text-amber-200 bg-amber-400/10"
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default async function NarrativeDetailPage({ params }: Params) {
  const { slug } = await params;

  const [res, creatorsRes] = await Promise.all([
    fetch(`${API_BASE}/api/narratives/enriched/video_details/${slug}`, { cache: "no-store" }),
    fetch(`${API_BASE}/api/creators`, { cache: "no-store" }),
  ]);

  if (!res.ok) {
    console.error(`Failed to fetch detailed narrative ${slug}:`, res.statusText);
    notFound();
  }

  const narrative: ApiNarrativesResponse = await res.json();
  console.log("Fetched narrative detail:", narrative);

  // Build creator map
  const creatorMap: Record<string, string> = {};
  if (creatorsRes.ok) {
    const creatorsData: { channel_id: string; creator_name: string }[] = await creatorsRes.json();
    for (const c of creatorsData) {
      creatorMap[c.channel_id] = c.creator_name;
    }
  }

  const creatorName = creatorMap[narrative.channel_id] || narrative.channel_id;

  const pfpRes = await fetch(`${API_BASE}/api/creators/${narrative.channel_id}/pfp`, { cache: "no-store" })
  const creatorPfp = pfpRes.ok ? (await pfpRes.json())?.pfp_url ?? null : null
  console.log(`Fetched creator PFP for ${creatorName} (${narrative.channel_id}):`, creatorPfp);

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0b0b10] via-[#0f1018] to-[#0b0b10] text-white">
      <div className="max-w-6xl mx-auto px-6 pb-16 pt-12 space-y-10">

        {/* Breadcrumb */}
        <div className="flex items-center gap-4 text-sm text-gray-400">
          <Link href="/narratives" className="underline underline-offset-4 decoration-white/30 hover:text-white">
            Narratives
          </Link>
          <span>›</span>
          <span className="text-gray-200">{narrative.narrative_text}</span>
        </div>

        {/* Header */}
        <header className="space-y-4">
          <div className="flex flex-wrap items-center gap-3">
            <span className={`rounded-full px-3 py-1 text-xs ${sentimentChip(narrative.metadata?.sentiment ?? null)}`}>
              {narrative.metadata?.sentiment ?? "neutral"}
            </span>
            <span className="rounded-full bg-white/10 text-gray-200 px-3 py-1 text-xs border border-white/10">
              Sentiment score: {narrative.metadata?.sentiment_score ?? "—"}
            </span>
            <span className="rounded-full bg-white/10 text-gray-200 px-3 py-1 text-xs border border-white/10">
              Views: {narrative.video_stats?.view_count?.toLocaleString() ?? "—"}
            </span>
          </div>
          <h3 className="text-sm uppercase tracking-[0.25em] text-gray-400">Narrative overview</h3>
          <h1 className="text-4xl font-semibold leading-tight">{narrative.narrative_text}</h1>
          <p className="text-base text-gray-300 max-w-3xl">{narrative.destination}</p>

          <div className="rounded-2xl border border-white/10 bg-white/5 p-4 shadow-inner shadow-black/30">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex items-center gap-3">
                <div className="h-11 w-11 rounded-full border border-white/10 bg-white/10 overflow-hidden flex items-center justify-center">
                  {creatorPfp ? (
                    <img src={creatorPfp} alt={creatorName} className="h-full w-full object-cover" />
                  ) : (
                    <span className="text-[11px] text-gray-200">YT</span>
                  )}
                </div>
                <div className="leading-tight">
                  <p className="text-[11px] uppercase tracking-wide text-gray-400">Creator</p>
                  <Link href={`/creators/${narrative.channel_id}`} className="text-sm text-gray-100 hover:underline hover:underline-offset-4">
                    {creatorName}
                  </Link>
                </div>
              </div>

              <div className="sm:text-right">
                <p className="text-[11px] uppercase tracking-wide text-gray-400">Narrative date</p>
                <p className="text-lg font-semibold text-white">
                  {narrative.date ? new Date(narrative.date).toLocaleString() : "—"}
                </p>
              </div>
            </div>
          </div>
        </header>

        {/* Metrics */}
        <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <MetricCard label="View Count" value={narrative.video_stats?.view_count?.toLocaleString() || "0"} />
          <MetricCard label="Active claims" value={narrative.claims.length.toString()} />
          <MetricCard label="Video Like Count" value={narrative.video_stats?.like_count?.toLocaleString() || "0"} />
          <MetricCard label="Sentiment" value={narrative.metadata.sentiment_score?.toString() || "Not available"} />
        </section>

        {/* Creator */}
        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-gray-400">Narrative Creators</p>
              <p className="text-sm text-gray-400">Channel informing this narrative.</p>
            </div>
            <span className="text-xs text-gray-400">1 highlighted</span>
          </div>
          <Link
            href={`/creators/${narrative.channel_id}`}
            className="group flex items-center gap-3 rounded-2xl border border-white/10 bg-gradient-to-b from-[#151525] via-[#11111a] to-[#0c0c12] p-4 shadow-lg shadow-black/40 hover:-translate-y-0.5 transition"
          >
            <div className="h-12 w-12 rounded-full border border-white/10 bg-white/10 overflow-hidden flex items-center justify-center">
              {creatorPfp ? (
                <img src={creatorPfp} alt={creatorName} className="h-full w-full object-cover" />
              ) : (
                <span className="text-[11px] text-gray-200">YT</span>
              )}
            </div>
            <div className="min-w-0">
              <p className="text-sm font-semibold text-white truncate group-hover:text-[#E4CAFF]">
                {creatorName}
              </p>
              <p className="text-xs text-gray-400 truncate">{narrative.channel_id}</p>
            </div>
          </Link>
        </section>

        {/* Claims */}
        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-gray-400">Claims carousel</p>
              <p className="text-sm text-gray-400">High-signal claims clustered for this narrative.</p>
            </div>
            <span className="text-xs text-gray-400">{narrative?.claims?.length ?? 0} shown</span>
          </div>
          <div className="flex gap-4 overflow-x-auto pb-2">
            {narrative.claims.map((claim, idx) => (
              <div
                key={idx}
                className="min-w-[240px] max-w-[260px] rounded-2xl border border-white/10 bg-gradient-to-b from-[#151525] via-[#11111a] to-[#0c0c12] p-4 shadow-lg shadow-black/40"
              >
                <p className="text-sm text-gray-200 mb-3">"{claim.claim_text}"</p>
                <div className="text-xs text-gray-400 space-y-1">
                  <p><span className="text-gray-500">Source:</span> {creatorMap[claim.source] || claim.source}</p>
                  <p><span className="text-gray-500">Risk:</span> {claim.claim_risk}</p>
                  <p><span className="text-gray-500">Date:</span> {claim.date}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

      </div>
    </div>
  )
}

// ── Sub-components ────────────────────────────────────────────────────────────

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-4 shadow-inner shadow-black/30">
      <p className="text-[11px] uppercase tracking-wide text-gray-400">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-white">{value}</p>
    </div>
  )
}
