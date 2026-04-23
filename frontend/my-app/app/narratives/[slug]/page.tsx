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
    thumbnail_url?: string
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
  const viewCount = narrative.video_stats?.view_count ?? 0
  const likeCount = narrative.video_stats?.like_count ?? 0
  const commentCount = narrative.video_stats?.comment_count ?? 0
  const likeRate = viewCount ? likeCount / viewCount : 0
  const commentRate = viewCount ? commentCount / viewCount : 0

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
              Views: {viewCount ? viewCount.toLocaleString() : "—"}
            </span>
          </div>
          <h3 className="text-sm uppercase tracking-[0.25em] text-gray-400">Narrative overview</h3>
          <h1 className="text-4xl font-semibold leading-tight">{narrative.narrative_text}</h1>
          <p className="text-base text-gray-300 max-w-3xl">{narrative.destination}</p>
        </header>

        {/* Context + source video */}
        <section className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="rounded-2xl border border-white/10 bg-white/5 p-5 shadow-inner shadow-black/30 space-y-4">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex items-center gap-3">
                <div className="h-12 w-12 rounded-full border border-white/10 bg-white/10 overflow-hidden flex items-center justify-center">
                  {creatorPfp ? (
                    <img src={creatorPfp} alt={creatorName} className="h-full w-full object-cover" />
                  ) : (
                    <span className="text-[11px] text-gray-200">YT</span>
                  )}
                </div>
                <div className="leading-tight">
                  <p className="text-[11px] uppercase tracking-wide text-gray-400">Creator</p>
                  <Link
                    href={`/creators/${narrative.channel_id}`}
                    className="text-sm text-gray-100 hover:underline hover:underline-offset-4"
                  >
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

            {narrative.metadata?.title ? (
              <div className="space-y-1">
                <p className="text-[11px] uppercase tracking-wide text-gray-400">Source video title</p>
                {narrative.metadata.webpage_url ? (
                  <Link
                    href={narrative.metadata.webpage_url}
                    className="text-sm text-gray-100 hover:underline hover:underline-offset-4"
                  >
                    {narrative.metadata.title}
                  </Link>
                ) : (
                  <p className="text-sm text-gray-100">{narrative.metadata.title}</p>
                )}
                <p className="text-xs text-gray-400">
                  Uploaded {narrative.metadata.upload_date ? new Date(narrative.metadata.upload_date).toLocaleDateString() : "—"}
                </p>
              </div>
            ) : null}

            <div className="flex flex-wrap gap-2 text-[11px] uppercase tracking-wide text-gray-200">
              <span className="rounded-full bg-white/10 px-3 py-1">{likeRate ? `${(likeRate * 100).toFixed(1)}%` : "—"} like rate</span>
              <span className="rounded-full bg-white/10 px-3 py-1">{commentRate ? `${(commentRate * 100).toFixed(2)}%` : "—"} comment rate</span>
              <span className="rounded-full bg-white/10 px-3 py-1">{likeCount ? likeCount.toLocaleString() : "—"} likes</span>
              <span className="rounded-full bg-white/10 px-3 py-1">{commentCount ? commentCount.toLocaleString() : "—"} comments</span>
            </div>
          </div>

          <div className="rounded-2xl border border-white/10 bg-gradient-to-b from-[#151525] via-[#11111a] to-[#0c0c12] shadow-lg shadow-black/40 overflow-hidden">
            <div className="h-44 w-full bg-[#1f1f2b] overflow-hidden flex items-center justify-center">
              {narrative.metadata?.thumbnail_url ? (
                <img src={narrative.metadata.thumbnail_url} alt={narrative.metadata.title || "Video thumbnail"} className="h-full w-full object-cover" />
              ) : (
                <span className="text-xs text-gray-400">No thumbnail</span>
              )}
            </div>
            <div className="p-4 space-y-2">
              <p className="text-[11px] uppercase tracking-wide text-gray-400">Source video</p>
              <p className="text-sm text-gray-100 line-clamp-2">{narrative.metadata?.title || "—"}</p>
              {narrative.metadata?.webpage_url ? (
                <Link
                  href={narrative.metadata.webpage_url}
                  className="inline-flex items-center justify-center rounded-xl bg-[#E4CAFF] px-4 py-2 text-sm font-medium text-black hover:bg-white transition"
                >
                  Watch on YouTube
                </Link>
              ) : null}
            </div>
          </div>
        </section>

        {/* Tags + risk callouts */}
        <section className="grid gap-4 lg:grid-cols-2">
          <div className="rounded-2xl border border-white/10 bg-white/5 p-5 shadow-inner shadow-black/30 space-y-3">
            <p className="text-[11px] uppercase tracking-wide text-gray-400">Tags</p>
            {narrative.metadata?.tags?.length ? (
              <div className="flex flex-wrap gap-2">
                {narrative.metadata.tags.slice(0, 18).map((tag) => (
                  <span key={tag} className="rounded-full bg-white/10 px-3 py-1 text-xs text-gray-200">
                    {tag}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-300">No tags available.</p>
            )}
          </div>

          <div className="rounded-2xl border border-white/10 bg-white/5 p-5 shadow-inner shadow-black/30 space-y-3">
            <p className="text-[11px] uppercase tracking-wide text-gray-400">Risk callouts</p>
            {narrative.metadata?.risk_callouts?.length ? (
              <ul className="space-y-2 text-sm text-gray-200">
                {narrative.metadata.risk_callouts.slice(0, 6).map((callout) => (
                  <li key={callout} className="flex gap-3">
                    <span className="mt-2 h-2 w-2 rounded-full bg-amber-300" />
                    <span className="leading-relaxed">{callout}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-gray-300">No risk callouts flagged.</p>
            )}
          </div>
        </section>

        {/* Metrics */}
        <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <MetricCard label="View Count" value={viewCount ? viewCount.toLocaleString() : "—"} />
          <MetricCard label="Active claims" value={narrative.claims.length.toString()} />
          <MetricCard label="Likes" value={likeCount ? likeCount.toLocaleString() : "—"} />
          <MetricCard label="Comments" value={commentCount ? commentCount.toLocaleString() : "—"} />
        </section>

        {/* Claims */}
        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-gray-400">Claims</p>
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
                <span
                  className={`inline-flex items-center rounded-full border px-2.5 py-1 text-[11px] uppercase tracking-wide ${
                    claim.claim_risk === "High"
                      ? "border-rose-300/40 text-rose-200 bg-rose-400/10"
                      : claim.claim_risk === "Low"
                      ? "border-emerald-400/40 text-emerald-200 bg-emerald-400/10"
                      : "border-amber-300/40 text-amber-200 bg-amber-300/10"
                  }`}
                >
                  {claim.claim_risk} risk
                </span>
                <p className="mt-3 text-sm text-gray-200 mb-3">&quot;{claim.claim_text}&quot;</p>
                <div className="text-xs text-gray-400 space-y-1">
                  <p>
                    <span className="text-gray-500">Source:</span>{" "}
                    <Link href={`/creators/${claim.source}`} className="hover:underline hover:underline-offset-4">
                      {creatorMap[claim.source] || claim.source}
                    </Link>
                  </p>
                  <p>
                    <span className="text-gray-500">Date:</span>{" "}
                    {claim.date ? new Date(claim.date).toLocaleDateString() : "—"}
                  </p>
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
