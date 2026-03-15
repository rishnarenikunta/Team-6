import Link from "next/link"

type Narrative = {
  slug: string
  title: string
  region: string
  sentiment: "positive" | "neutral" | "negative"
  velocity: string
  creators: string
  watchtime: string
  claim: string
  risk: string
  tags: string[]
}

const narratives: Narrative[] = [
  {
    slug: "slow-travel-japan-countryside",
    title: "Slow travel in Japan’s countryside",
    region: "APAC",
    sentiment: "positive",
    velocity: "+18% week-over-week",
    creators: "72 active creators",
    watchtime: "3.4M hrs past 30d",
    claim: "Rural rail passes and farm-stays are beating city itineraries for engagement.",
    risk: "Low creator risk",
    tags: ["slow travel", "rail", "food", "autumn"],
  },
  {
    slug: "mediterranean-shoulder-season-hack",
    title: "Mediterranean shoulder-season hack",
    region: "EMEA",
    sentiment: "positive",
    velocity: "+11% week-over-week",
    creators: "46 active creators",
    watchtime: "1.9M hrs past 30d",
    claim: "Creators push October/November trips to dodge crowds while keeping beach weather.",
    risk: "Moderate: pricing & over-tourism mentions",
    tags: ["budget", "beaches", "couples", "off-peak"],
  },
  {
    slug: "mexico-city-safety-discourse",
    title: "Mexico City safety discourse",
    region: "AMER",
    sentiment: "neutral",
    velocity: "+6% week-over-week",
    creators: "58 active creators",
    watchtime: "2.7M hrs past 30d",
    claim: "Newcomer vlogs debate neighborhood safety and transit at night; comments split.",
    risk: "Monitor: safety + gentrification narrative",
    tags: ["safety", "nightlife", "urban", "tips"],
  },
  {
    slug: "balkan-road-trip-loop",
    title: "Balkan road-trip loop",
    region: "EMEA",
    sentiment: "positive",
    velocity: "+14% week-over-week",
    creators: "33 active creators",
    watchtime: "1.1M hrs past 30d",
    claim: "Vanlife channels spotlight cheap ferries, castle towns, and lake campsites.",
    risk: "Low creator risk",
    tags: ["road trip", "budget", "nature", "vanlife"],
  },
  {
    slug: "seoul-night-markets-kpop",
    title: "Seoul night markets & K-pop pilgrimages",
    region: "APAC",
    sentiment: "positive",
    velocity: "+21% week-over-week",
    creators: "97 active creators",
    watchtime: "4.6M hrs past 30d",
    claim: "Short-form hauls and concert vlogs drive repeat viewing; viewers request exact shop maps.",
    risk: "Low creator risk",
    tags: ["shopping", "night market", "music", "food"],
  },
  {
    slug: "us-national-parks-winter-playbook",
    title: "US national parks winter playbook",
    region: "AMER",
    sentiment: "positive",
    velocity: "+9% week-over-week",
    creators: "29 active creators",
    watchtime: "900k hrs past 30d",
    claim: "Creators pivot to winter hiking, photography, and crowd-free itineraries.",
    risk: "Monitor: safety/weather disclaimers",
    tags: ["parks", "winter", "hiking", "photography"],
  },
]

const sentimentChip = (sentiment: Narrative["sentiment"]) => {
  if (sentiment === "positive") return "text-emerald-300 bg-emerald-400/10"
  if (sentiment === "negative") return "text-rose-300 bg-rose-400/10"
  return "text-amber-200 bg-amber-400/10"
}

export default function NarrativePage() {
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

          <form className="w-full md:w-[360px]">
            <label htmlFor="narrative-search" className="sr-only">
              Search narratives
            </label>
            <div className="flex gap-2 bg-[#16161e] border border-[#242436] rounded-2xl px-4 py-3 shadow-lg shadow-black/40">
              <input
                id="narrative-search"
                type="search"
                placeholder="Search a keyword, city, or creator"
                className="flex-1 bg-transparent text-sm focus:outline-none placeholder:text-gray-500"
              />
              <button
                type="button"
                className="rounded-xl bg-white/10 px-4 py-2 text-sm font-medium transition hover:bg-white/20"
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
            {narratives.map((narrative) => (
              <Link key={narrative.title} href={`/narratives/${narrative.slug}`} className="block group">
                <article className="relative overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-b from-[#1d1525] via-[#10101a] to-[#0c0c12] p-5 transition hover:-translate-y-1 hover:border-white/25 hover:shadow-2xl hover:shadow-black/50">
                  <div className="flex items-start justify-between gap-3">
                    <div className="space-y-1">
                      <h3 className="text-xl font-semibold group-hover:text-white">{narrative.title}</h3>
                      <p className="text-sm text-gray-400">{narrative.region}</p>
                    </div>  
                    <span className={`rounded-full px-3 py-1 text-xs ${sentimentChip(narrative.sentiment)}`}>
                      {narrative.sentiment}
                    </span>
                  </div>

                  <p className="mt-3 text-sm text-blue-200">{narrative.velocity}</p>
                  <p className="mt-2 text-sm text-gray-200">{narrative.claim}</p>

                  <div className="mt-4 flex flex-wrap gap-2 text-[11px] uppercase tracking-wide text-gray-300">
                    {narrative.tags.map((tag) => (
                      <span key={tag} className="rounded-full bg-white/5 px-3 py-1">
                        {tag}
                      </span>
                    ))}
                  </div>

                  <div className="mt-5 grid grid-cols-2 gap-3 text-xs text-gray-300">
                    <div className="rounded-xl bg-white/5 px-3 py-2 border border-white/10">
                      <p className="text-[10px] uppercase tracking-wide text-gray-400">Creator mix</p>
                      <p className="font-medium">{narrative.creators}</p>
                    </div>
                    <div className="rounded-xl bg-white/5 px-3 py-2 border border-white/10">
                      <p className="text-[10px] uppercase tracking-wide text-gray-400">Watchtime</p>
                      <p className="font-medium">{narrative.watchtime}</p>
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
        </section>
      </div>
    </div>
  )
}
