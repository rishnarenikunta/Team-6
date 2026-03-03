const destinations = [
  {
    name: "Kyoto",
    country: "Japan",
    signal: "Narrative momentum +12%",
    risk: "Low creator risk",
    highlights: ["culture", "food", "walkable"],
    blurb:
      "Autumn travel vlogs are spiking; viewers gravitate toward slow itineraries and neighborhood food crawls.",
  },
  {
    name: "Lisbon",
    country: "Portugal",
    signal: "Search interest +8%",
    risk: "Moderate creator risk",
    highlights: ["budget", "coast", "nightlife"],
    blurb:
      "Creators tout shoulder-season bargains and surf day-trips; mixed sentiment on short-term rental fatigue.",
  },
  {
    name: "México City",
    country: "Mexico",
    signal: "Watch time +15%",
    risk: "Monitor safety advisories",
    highlights: ["food", "design", "urban"],
    blurb:
      "Long-form food series are outperforming; audience questions center on neighborhoods and transit safety.",
  },
  {
    name: "Seoul",
    country: "South Korea",
    signal: "Narrative momentum +10%",
    risk: "Low creator risk",
    highlights: ["pop culture", "shopping", "night market"],
    blurb:
      "Short-form hauls and night market reels dominate; viewers want exact shop maps and late-night transit tips.",
  },
]

const quickFilters = ["Asia", "Coastal", "Budget friendly", "Solo travel", "Family", "Remote work"]

export default function DiscoverPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0b0b0e] via-[#101014] to-[#0b0b0e] text-white">
      <div className="max-w-6xl mx-auto px-6 pb-16 pt-10 space-y-10">
        <header className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div className="space-y-2">
            <p className="text-xs uppercase tracking-[0.3em] text-gray-400">Discover</p>
            <h1 className="text-4xl font-semibold leading-tight">Find your next destination faster</h1>
            <p className="text-sm text-gray-400 max-w-2xl">
              Combine creator sentiment, trend velocity, and safety signals before you book. Start with a search or
              pick a quick filter to explore narratives already emerging on YouTube.
            </p>
          </div>

          <form className="w-full md:w-[360px]">
            <label className="sr-only" htmlFor="discover-search">
              Search destinations
            </label>
            <div className="flex gap-2 bg-[#16161e] border border-[#242436] rounded-2xl px-4 py-3 shadow-lg shadow-black/40">
              <input
                id="discover-search"
                type="search"
                placeholder="Search a city, region, or keyword"
                className="flex-1 bg-transparent text-sm focus:outline-none placeholder:text-gray-500"
              />
              <button
                type="button"
                className="rounded-xl bg-white/10 px-4 py-2 text-sm font-medium transition hover:bg-white/20"
              >
                Preview signals
              </button>
            </div>
          </form>
        </header>

        <section className="space-y-3">
          <h2 className="text-sm font-semibold text-gray-300">Quick filters</h2>
          <div className="flex flex-wrap gap-3">
            {quickFilters.map((tag) => (
              <button
                key={tag}
                type="button"
                className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs text-gray-200 transition hover:-translate-y-0.5 hover:border-white/25 hover:bg-white/10"
              >
                {tag}
              </button>
            ))}
          </div>
        </section>

        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-400 uppercase tracking-[0.2em]">Trending destinations</p>
              <p className="text-sm text-gray-400">Signals are refreshed hourly from creator uploads and engagement.</p>
            </div>
            <button
              type="button"
              className="text-xs font-medium text-gray-300 underline underline-offset-4 decoration-white/30 hover:text-white"
            >
              View methodology
            </button>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {destinations.map((city) => (
              <article
                key={city.name}
                className="group relative overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-b from-[#141420] via-[#0f0f17] to-[#0c0c12] p-5 transition hover:-translate-y-1 hover:border-white/25 hover:shadow-2xl hover:shadow-black/50"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-xl font-semibold">{city.name}</h3>
                    <p className="text-sm text-gray-400">{city.country}</p>
                  </div>
                  <span className="rounded-full bg-emerald-500/15 px-3 py-1 text-xs text-emerald-300">
                    {city.risk}
                  </span>
                </div>

                <p className="mt-3 text-sm text-blue-300">{city.signal}</p>
                <p className="mt-2 text-sm text-gray-300">{city.blurb}</p>

                <div className="mt-4 flex flex-wrap gap-2">
                  {city.highlights.map((tag) => (
                    <span
                      key={tag}
                      className="rounded-full bg-white/5 px-3 py-1 text-[11px] uppercase tracking-wide text-gray-300"
                    >
                      {tag}
                    </span>
                  ))}
                </div>

                <div className="mt-6 flex items-center justify-between text-xs text-gray-400">
                  <span className="flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full bg-emerald-400 shadow-[0_0_0_6px_rgba(52,211,153,0.08)]" />
                    Healthy creator mix
                  </span>
                  <button
                    type="button"
                    className="font-medium text-blue-200 underline underline-offset-4 decoration-blue-200/40 transition group-hover:text-white"
                  >
                    Open dashboard
                  </button>
                </div>
              </article>
            ))}
          </div>
        </section>
      </div>
    </div>
  )
}
