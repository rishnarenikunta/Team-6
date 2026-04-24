"use client"
import Link from "next/link"
import { useEffect, useState } from "react"


type Narrative = {
  slug: string
  title: string
  sentiment: "positive" | "neutral" | "negative"
  sentiment_score: number
  creators: string
  date: string
  claim: string
  risk: "low" | "medium" | "high" | "none";
  tags: string[]
  destination?: string
}

// const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const fallbackNarratives: Narrative[] = [
  {
    slug: "fallback",
    title: "Narratives unavailable",
    sentiment: "neutral",
    sentiment_score: 0,
    creators: "N/A",
    date: "—",
    claim: "No narratives could be loaded from the API.",
    risk: "none",
    tags: [],
    destination: "—",
  },
]

const sentimentChip = (sentiment: Narrative["sentiment"]) => {
  if (sentiment === "positive") return "text-emerald-300 bg-emerald-400/10"
  if (sentiment === "negative") return "text-rose-300 bg-rose-400/10"
  return "text-amber-200 bg-amber-400/10"
}

export default function NarrativePage() {

  type ApiNarrativeItem = {
    slug: string;
    narrative_id: string;
    video_id: string;
    destination: string;
    channel_id: string;
    narrative_text: string;
    narrative_risk: "low" | "medium" | "high" | "none";
    date: string;
    claims: { claim_text?: string; claim_risk?: string }[];
    metadata: {
      tags: string[];
      sentiment_score: number | null;
      sentiment: "positive" | "neutral" | "negative" | null;
      title: string;
      upload_date: string;
      webpage_url: string;
    };
  };

  type ApiNarrativesResponse = ApiNarrativeItem[];

const [narratives, setNarratives] = useState<Narrative[]>([]);
const [loading, setLoading] = useState(true);
const [error, setError] = useState<string | null>(null);
const [page, setPage] = useState(0);
const [searchTerm, setSearchTerm] = useState("");
const pageSize = 6;

useEffect(() => {
  let cancelled = false;

  async function fetchNarratives() {
    try {
      setError(null);

      const [narrativesRes, creatorsRes] = await Promise.all([
        fetch(`/api/narratives/enriched`),
        fetch(`/api/creators`),
      ]);

      if (!narrativesRes.ok) throw new Error(`API error ${narrativesRes.status}`);
      if (!creatorsRes.ok) throw new Error(`API error ${creatorsRes.status}`);

      const data: ApiNarrativesResponse = await narrativesRes.json();
      const creatorsData: { channel_id: string; creator_name: string }[] = await creatorsRes.json();

      // Build a channel_id → creator_name map
      const creatorMap: Record<string, string> = {};
      for (const c of creatorsData) {
        creatorMap[c.channel_id] = c.creator_name;
      }

      console.log("Fetched narratives:", data);

      const mapped: Narrative[] = data.map((item) => ({
        slug: item.slug || item.narrative_id,
        title: item.narrative_text,
        sentiment: item.metadata.sentiment || "neutral",
        sentiment_score: item.metadata.sentiment_score || 0,
        creators: creatorMap[item.channel_id] || item.channel_id || "Unknown creator",
        date: item.date
          ? new Date(item.date).toLocaleString()
          : item.metadata.upload_date
            ? new Date(item.metadata.upload_date).toLocaleDateString()
            : "Unknown date",
        claim: item.claims.length > 0
          ? (item.claims[0].claim_text || "No claim text")
          : "No claims identified",
        risk: item.narrative_risk,
        tags: item.metadata.tags || [],
        destination: item.destination || "Unknown destination",
      }));

      if (!cancelled) setNarratives(mapped.length ? mapped : fallbackNarratives);
    } catch (err) {
      if (!cancelled) {
        setError("Failed to fetch narratives");
        setNarratives(fallbackNarratives);
      }
      console.error(err);
    } finally {
      if (!cancelled) setLoading(false);
    }
  }

  fetchNarratives();
  return () => { cancelled = true; };
}, []);

  const filtered = narratives.filter((n) => {
    const term = searchTerm.trim().toLowerCase();
    if (!term) return true;
    return (
      n.title.toLowerCase().includes(term)
    );
  });
  const start = page * pageSize;
  const visible = filtered.slice(start, start + pageSize);

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0c0c12] via-[#130f18] to-[#0c0c12] text-white">
      <div className="max-w-6xl mx-auto px-6 pb-16 pt-12 space-y-10">
        <header className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div className="space-y-3">
            <p className="text-xs uppercase tracking-[0.3em] text-gray-400">Narratives</p>
            <h1 className="text-4xl font-semibold leading-tight">Monitor emerging travel narratives</h1>
            <p className="text-sm text-gray-400 max-w-2xl">
              Compare sentiment, velocity, and creator mix across destinations. Start from popular themes or drill into
              a specific storyline before it shapes bookings and brand safety.
            </p>
          </div>

          <form
            className="w-full md:w-[360px]"
            onSubmit={(e) => {
              e.preventDefault();
              setPage(0);
            }}
          >
            <label htmlFor="narrative-search" className="sr-only">
              Search narratives
            </label>
            <div className="flex gap-2 bg-[#16161e] border border-[#242436] rounded-2xl px-4 py-3 shadow-lg shadow-black/40">
              <input
                id="narrative-search"
                type="search"
                placeholder="Search a destination / region"
                className="flex-1 bg-transparent text-sm focus:outline-none placeholder:text-gray-500"
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value);
                  setPage(0);
                }}
              />
              <button
                type="button"
                className="rounded-xl bg-white/10 px-4 py-2 text-sm font-medium transition hover:bg-white/20"
                onClick={() => setPage(0)}
              >
                Analyze
              </button>
            </div>
          </form>
        </header>

        <section className="space-y-3">
          <div className="flex items-center gap-3 text-xs text-gray-300">
            <span className="rounded-full bg-emerald-400/15 px-3 py-1">Positive</span>
            <span className="rounded-full bg-amber-400/15 px-3 py-1">Neutral</span>
            <span className="rounded-full bg-rose-400/15 px-3 py-1">Negative</span>
            <span className="ml-auto text-[11px] text-gray-400">
              Signals refreshed hourly from YouTube upload velocity & engagement.
            </span>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            {visible.map((narrative) => (
              <Link key={narrative.slug} href={`/narratives/${narrative.slug}`} className="block group">
                <article className="relative overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-b from-[#1d1525] via-[#10101a] to-[#0c0c12] p-5 transition hover:-translate-y-1 hover:border-white/25 hover:shadow-2xl hover:shadow-black/50">
                  <div className="flex items-start justify-between gap-3">
                    <div className="space-y-1">
                      <h3 className="text-xl font-semibold group-hover:text-white">{narrative.title}</h3>
                      <p className="text-sm text-gray-400">Narrative Destination: {narrative.destination}</p>
                    </div>  
                    <span className={`rounded-full px-3 py-1 text-xs ${sentimentChip(narrative.sentiment)}`}>
                      {narrative.sentiment}
                    </span>
                  </div>

                  <div className="mt-3 space-y-2">
                    <div className="flex items-center gap-3 text-xs text-gray-300">
                      <span className="uppercase tracking-[0.12em] text-[11px] text-gray-400">Sentiment score</span>
                      <div className="flex-1 h-2 rounded-full bg-white/10 overflow-hidden">
                        <div
                          className="h-full transition-all"
                          style={{
                            width: `${Math.min(100, Math.max(0, narrative.sentiment_score * 100)).toFixed(0)}%`,
                            background:
                              narrative.sentiment === "positive"
                                ? "linear-gradient(90deg, #34d399, #10b981)"
                                : narrative.sentiment === "negative"
                                  ? "linear-gradient(90deg, #fb7185, #f43f5e)"
                                  : "linear-gradient(90deg, #facc15, #fbbf24)",
                          }}
                        />
                      </div>
                      <span className="text-sm font-semibold text-white">
                        {narrative.sentiment_score.toFixed(2)}
                      </span>
                    </div>

                    <div className="rounded-xl border border-white/10 bg-white/5 px-4 py-3 shadow-inner shadow-black/30">
                      <div className="flex items-center justify-between text-xs text-gray-400">
                        <span className="uppercase tracking-[0.15em]">Lead claim</span>
                        <span className="rounded-full bg-white/10 px-2 py-0.5 text-[10px] text-gray-200">
                          {narrative.risk || "—"}
                        </span>
                      </div>
                      <p className="mt-2 text-sm text-gray-100 leading-relaxed">“{narrative.claim}”</p>
                    </div>
                  </div>

                  <div className="mt-4 flex flex-wrap gap-2 text-[11px] uppercase tracking-wide text-gray-300">
                    {narrative.tags.map((tag) => (
                      <span key={tag} className="rounded-full bg-white/5 px-3 py-1">
                        {tag}
                      </span>
                    ))}
                  </div>

                  <div className="mt-5 grid grid-cols-2 gap-3 text-xs text-gray-300">
                    <div className="rounded-xl bg-white/5 px-3 py-2 border border-white/10">
                      <p className="text-[10px] uppercase tracking-wide text-gray-400">Creator Name</p>
                      <p className="font-medium">{narrative.creators}</p>
                    </div>
                    <div className="rounded-xl bg-white/5 px-3 py-2 border border-white/10">
                      <p className="text-[10px] uppercase tracking-wide text-gray-400">Date</p>
                      <p className="font-medium">{narrative.date}</p>
                    </div>
                    <div className="rounded-xl bg-white/5 px-3 py-2 border border-white/10">
                      <p className="text-[10px] uppercase tracking-wide text-gray-400">Risk</p>
                      <p className="font-medium">{narrative.risk}</p>
                    </div>
                    <div className="rounded-xl bg-white/5 px-3 py-2 border border-white/10">
                      <p className="text-[10px] uppercase tracking-wide text-gray-400">Action</p>
                      <p className="font-medium text-blue-200 underline underline-offset-4 decoration-blue-200/40 transition group-hover:text-white">
                        Open narrative
                      </p>
                    </div>
                  </div>
                </article>
              </Link>
            ))}
          </div>

          <div className="mt-6 flex items-center justify-between">
            <button
              type="button"
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={page === 0}
              className="rounded-xl border border-white/15 bg-white/5 px-4 py-2 text-sm text-white disabled:opacity-40 disabled:cursor-not-allowed hover:border-white/30 hover:bg-white/10 transition"
            >
              ← Previous
            </button>
            <button
              type="button"
              onClick={() =>
                setPage((p) => (start + pageSize >= narratives.length ? p : p + 1))
              }
              disabled={start + pageSize >= filtered.length}
              className="rounded-xl border border-white/15 bg-white/5 px-4 py-2 text-sm text-white disabled:opacity-40 disabled:cursor-not-allowed hover:border-white/30 hover:bg-white/10 transition"
            >
              Next →
            </button>
          </div>
        </section>
      </div>
    </div>
  )
}
