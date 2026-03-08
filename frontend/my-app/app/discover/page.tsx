import Link from "next/link"
import DiscoverBar from "../components/DiscoverBar"
import StatsMain from "../sections/StatsMain"
import TrendingLocations from "../sections/TrendingLocations"
import TrendingNarratives from "../sections/TrendingNarratives"
import { TrendingClaims } from "../sections/TrendingClaims"
import TopCountries from "../components/TopCountries"

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
                className="rounded-xl bg-[#E4CAFF] text-black px-4 py-2 text-sm font-medium transition hover:bg-white/20"
              >
                Search
              </button>
            </div>
          </form>
        </header>

        <section className="space-y-3">
          <h2 className="text-sm font-semibold text-gray-300">Quick searches</h2>
          <div className="flex flex-wrap gap-3">
            {quickFilters.map((tag) => (
              <button
                key={tag}
                type="button"
                className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs text-gray-200 transition hover:-translate-y-0.5 hover:border-white/25 hover:bg-[#E4CAFF] hover:text-[#1c1b22]"
              >
                {tag}
              </button>
            ))}
          </div>
        </section>

        <StatsMain />
        <TrendingLocations />
        <TrendingNarratives/>
        <TrendingClaims />



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
        </section>
      </div>
    </div>
  )
}
