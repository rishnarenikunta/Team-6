
import Link from "next/link"
import react from "react"


const destinations = [
  {
    slug: "hiking",
    name: "Hiking",
    country: "Keyword",
    signal: "Outdoor watch time +17%",
    risk: "Low brand safety risk",
    highlights: ["outdoors", "gear", "safety"],
    blurb:
      "Trail vlogs, pack breakdowns, and national park itineraries are accelerating; audiences seek gear links and safety notes.",
  },
  {
    slug: "kyoto",
    name: "Kyoto",
    country: "Japan",
    signal: "Narrative momentum +12%",
    risk: "Low creator risk",
    highlights: ["culture", "food", "walkable"],
    blurb:
      "Autumn travel vlogs are spiking; viewers gravitate toward slow itineraries and neighborhood food crawls.",
  },
  {
    slug: "lisbon",
    name: "Lisbon",
    country: "Portugal",
    signal: "Search interest +8%",
    risk: "Moderate creator risk",
    highlights: ["budget", "coast", "nightlife"],
    blurb:
      "Creators tout shoulder-season bargains and surf day-trips; mixed sentiment on short-term rental fatigue.",
  },
  {
    slug: "mexico-city",
    name: "México City",
    country: "Mexico",
    signal: "Watch time +15%",
    risk: "Monitor safety advisories",
    highlights: ["food", "design", "urban"],
    blurb:
      "Long-form food series are outperforming; audience questions center on neighborhoods and transit safety.",
  },
  {
    slug: "seoul",
    name: "Seoul",
    country: "South Korea",
    signal: "Narrative momentum +10%",
    risk: "Low creator risk",
    highlights: ["pop culture", "shopping", "night market"],
    blurb:
      "Short-form hauls and night market reels dominate; viewers want exact shop maps and late-night transit tips.",
  },
]


const TopCountries = () => {
    return (
        <div className="w-full mt-10 h-fit">
          <h2 className="text-2xl font-semibold text-white tracking-tight mb-2">
            Trending Countries
          </h2>
          <p className="text-sm text-neutral-400 border-b border-neutral-800 pb-4 mb-4">
            Trending countries represent top travel destinations gaining momentum across creator content and audience engagement.
            </p>


        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {destinations.map((city) => (
                <Link
                key={city.slug}
                href={`/discover/${city.slug}`}
                className="group relative overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-b from-[#1c1420] via-[#140f17] to-[#0c0c12] p-5 transition hover:-translate-y-1 hover:border-white/25 hover:shadow-2xl hover:shadow-black/50"
                >
                <div className="flex items-center justify-between">
                    <div>
                    <h3 className="text-xl font-semibold group-hover:text-white">{city.name}</h3>
                    <p className="text-sm text-gray-400">{city.country}</p>
                    </div>
                    <span className="rounded-full bg-purple-500/15 px-3 py-1 text-xs text-purple-300">
                    {city.risk}
                    </span>
                </div>

                <p className="mt-3 text-sm text-purple-300">{city.signal}</p>
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
                    <span className="font-medium text-purple-200 underline underline-offset-4 decoration-blue-200/40 transition group-hover:text-white">
                    Open dashboard
                    </span>
                </div>
                </Link>
            ))}
            </div>
            </div>
    );
};

export default TopCountries;
