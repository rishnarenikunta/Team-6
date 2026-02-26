import Link from "next/link"
import { notFound } from "next/navigation"

type Destination = {
  slug: string
  name: string
  country: string
  summary: string
  momentum: string
  risk: string
  sentiment: string
  videos: number
  claims: number
  creators: number
  spotlight: {
    name: string
    avatar: string
    subs: string
    uploads: string
    focus: string
  }[]
  topNarratives: {
    title: string
    slug: string
    sentiment: string
    velocity: string
    blurb: string
  }[]
  highlights: string[]
  questions: string[]
}

const destinations: Destination[] = [
  {
    slug: "kyoto",
    name: "Kyoto",
    country: "Japan",
    summary:
      "Autumn vlogs push slow itineraries, neighborhood food crawls, and local rail passes. Audience hunts for less crowded shrines and coffee alleys.",
    momentum: "Narrative momentum +12% WoW",
    risk: "Low creator risk",
    sentiment: "82% positive",
    videos: 512,
    claims: 22,
    creators: 74,
    spotlight: [
      { name: "NomadNick", avatar: "https://i.pravatar.cc/120?img=14", subs: "1.1M subs", uploads: "3 vids/week", focus: "Food + rail passes" },
      { name: "WonderWithMia", avatar: "https://i.pravatar.cc/120?img=32", subs: "840K subs", uploads: "2 vids/week", focus: "Izakaya hunts, autumn routes" },
      { name: "RailRiderKen", avatar: "https://i.pravatar.cc/120?img=55", subs: "410K subs", uploads: "1 vid/week", focus: "Regional passes & timetables" },
    ],
    topNarratives: [
      { title: "Slow travel in Japan’s countryside", slug: "slow-travel-japan-countryside", sentiment: "positive", velocity: "+18% WoW", blurb: "Rural rail loops, farm-stays, onsen towns beat city rush." },
      { title: "Seoul night markets & K-pop pilgrimages", slug: "seoul-night-markets-kpop", sentiment: "positive", velocity: "+21% WoW", blurb: "Night market hauls and concert routes drive repeat viewing." },
    ],
    highlights: ["culture", "food", "walkable", "rail passes"],
    questions: ["Which shrine routes avoid tour buses?", "Is ICOCA still best for multi-day hops?", "Cafe streets near Nishiki Market?"],
  },
  {
    slug: "lisbon",
    name: "Lisbon",
    country: "Portugal",
    summary:
      "Shoulder-season content emphasizes budget-friendly stays, surf day-trips, and pastel de nata trails. Mixed chatter on rental fatigue and hills accessibility.",
    momentum: "Search interest +8% WoW",
    risk: "Moderate creator risk",
    sentiment: "76% positive",
    videos: 341,
    claims: 18,
    creators: 58,
    spotlight: [
      { name: "PocketPorto", avatar: "https://i.pravatar.cc/120?img=5", subs: "320K subs", uploads: "2 vids/week", focus: "Budget coastal stays" },
      { name: "CoastlineKate", avatar: "https://i.pravatar.cc/120?img=8", subs: "510K subs", uploads: "1–2 vids/week", focus: "Surf day-trips & ferries" },
      { name: "EuroNomad", avatar: "https://i.pravatar.cc/120?img=61", subs: "760K subs", uploads: "weekly", focus: "Shoulder-season itineraries" },
    ],
    topNarratives: [
      { title: "Mediterranean shoulder-season hack", slug: "mediterranean-shoulder-season-hack", sentiment: "positive", velocity: "+11% WoW", blurb: "Crowd-free coastal trips in Oct/Nov with cheaper stays." },
      { title: "Hidden gems in Portugal", slug: "mediterranean-shoulder-season-hack", sentiment: "positive", velocity: "+9% WoW", blurb: "Alentejo slow stays, pastel de nata trails, surf add-ons." },
    ],
    highlights: ["budget", "coast", "nightlife", "surf"],
    questions: ["Best hill routes for mobility?", "Where to base for day-trip surf?", "Is the Lisboa card worth it?"],
  },
  {
    slug: "mexico-city",
    name: "México City",
    country: "Mexico",
    summary:
      "Long-form food series outperform; safety discourse focuses on neighborhoods and late-night transit. Audience asks for metro vs. rideshare comparisons.",
    momentum: "Watch time +15% WoW",
    risk: "Monitor safety advisories",
    sentiment: "64% positive / neutral skew",
    videos: 607,
    claims: 25,
    creators: 92,
    spotlight: [
      { name: "ChilangoCheck", avatar: "https://i.pravatar.cc/120?img=21", subs: "290K subs", uploads: "2 vids/week", focus: "Safety walkthroughs" },
      { name: "NomadNora", avatar: "https://i.pravatar.cc/120?img=44", subs: "610K subs", uploads: "weekly", focus: "Neighborhood guides" },
      { name: "DataDriftCDMX", avatar: "https://i.pravatar.cc/120?img=71", subs: "180K subs", uploads: "biweekly", focus: "Data-led metro tips" },
    ],
    topNarratives: [
      { title: "Mexico City safety discourse", slug: "mexico-city-safety-discourse", sentiment: "neutral", velocity: "+6% WoW", blurb: "Night transit, neighborhood debates, rideshare vs metro." },
      { title: "Hidden taqueria renaissance", slug: "mexico-city-safety-discourse", sentiment: "positive", velocity: "+8% WoW", blurb: "Street food deep-dives, late-night taco crawls." },
    ],
    highlights: ["food", "design", "urban", "nightlife"],
    questions: ["Is Line 3 safe after 10pm?", "Roma vs. Juarez for first-timers?", "Cashless vs. cash at street stands?"],
  },
  {
    slug: "seoul",
    name: "Seoul",
    country: "South Korea",
    summary:
      "Night-market reels, K-pop merch hunts, and cafe crawls dominate; viewers want exact stall maps and after-midnight transit tips.",
    momentum: "Narrative momentum +10% WoW",
    risk: "Low creator risk",
    sentiment: "88% positive",
    videos: 688,
    claims: 27,
    creators: 105,
    spotlight: [
      { name: "SeoulSnacks", avatar: "https://i.pravatar.cc/120?img=53", subs: "920K subs", uploads: "2–3 vids/week", focus: "Night markets" },
      { name: "KWaveKait", avatar: "https://i.pravatar.cc/120?img=46", subs: "1.3M subs", uploads: "weekly", focus: "Merch & concerts" },
      { name: "TransitTae", avatar: "https://i.pravatar.cc/120?img=29", subs: "480K subs", uploads: "weekly", focus: "Late-night transit" },
    ],
    topNarratives: [
      { title: "Seoul night markets & K-pop pilgrimages", slug: "seoul-night-markets-kpop", sentiment: "positive", velocity: "+21% WoW", blurb: "Market hauls, merch streets, concert night transit tips." },
      { title: "Slow travel in Japan’s countryside", slug: "slow-travel-japan-countryside", sentiment: "positive", velocity: "+18% WoW", blurb: "Rural loops and onsen towns as city alternates." },
    ],
    highlights: ["pop culture", "shopping", "night market", "transit"],
    questions: ["Which markets stay open past midnight?", "Best merch streets near Hongdae?", "Late-night bus vs. subway coverage?"],
  },
]

type Params = { params: Promise<{ slug: string }> }

export default async function DestinationPage({ params }: Params) {
  const { slug } = await params
  const destination = destinations.find((d) => d.slug === slug)
  if (!destination) return notFound()

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0b0b10] via-[#0f1018] to-[#0b0b10] text-white">
      <div className="max-w-6xl mx-auto px-6 pb-16 pt-12 space-y-10">
        <div className="flex items-center gap-4 text-sm text-gray-400">
          <Link href="/discover" className="underline underline-offset-4 decoration-white/30 hover:text-white">
            Discover
          </Link>
          <span>›</span>
          <span className="text-gray-200">{destination.name}</span>
        </div>

        <header className="space-y-4">
          <div className="flex flex-wrap items-center gap-3">
            <span className="rounded-full bg-emerald-500/15 text-emerald-200 px-3 py-1 text-xs border border-emerald-400/30">
              {destination.risk}
            </span>
            <span className="rounded-full bg-white/10 text-gray-200 px-3 py-1 text-xs border border-white/10">
              {destination.momentum}
            </span>
            <span className="rounded-full bg-white/10 text-gray-200 px-3 py-1 text-xs border border-white/10">
              {destination.creators} creators
            </span>
            <span className="rounded-full bg-white/10 text-gray-200 px-3 py-1 text-xs border border-white/10">
              {destination.videos} videos analyzed
            </span>
          </div>

          <div className="bg-[#E4CAFF] rounded-2xl w-full px-10 py-10 font-light mt-10">
            <h1 className="text-4xl font-light leading-tight text-black">
              {destination.name}, <span className="text-black">{destination.country}</span>
            </h1>
            <p className="text-base text-black max-w-3xl pt-5">{destination.summary}</p>
          </div>
        </header>

        <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          <Metric label="Videos analyzed" value={destination.videos.toLocaleString()} />
          <Metric label="Active Narratives" value={destination.claims.toString()} />
          <Metric label="Active creators" value={destination.creators.toString()} />
          <Metric label="Sentiment" value={destination.sentiment} />
        </section>

        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-gray-400">Top narratives here</p>
              <p className="text-sm text-gray-400">Click through to view the full narrative detail.</p>
            </div>
            <span className="text-xs text-gray-400">{destination.topNarratives.length} featured</span>
          </div>
          <div className="flex gap-4 overflow-x-auto pb-2">
            {destination.topNarratives.map((narrative) => (
              <Link
                key={narrative.slug + narrative.title}
                href={`/narratives/${narrative.slug}`}
                className="min-w-[260px] max-w-[280px] rounded-2xl border border-white/10 bg-gradient-to-b from-[#151525] via-[#11111a] to-[#0c0c12] p-4 shadow-lg shadow-black/40 hover:border-white/25 transition"
              >
                <div className="flex items-center justify-between gap-2">
                  <p className="text-sm font-semibold text-white">{narrative.title}</p>
                  <span
                    className={`text-[11px] px-2 py-1 rounded-full border ${
                      narrative.sentiment === "positive"
                        ? "border-emerald-400/40 text-emerald-200 bg-emerald-400/10"
                        : narrative.sentiment === "neutral"
                        ? "border-amber-300/40 text-amber-200 bg-amber-300/10"
                        : "border-rose-300/40 text-rose-200 bg-rose-300/10"
                    }`}
                  >
                    {narrative.sentiment}
                  </span>
                </div>
                <p className="text-xs text-blue-200 mt-2">{narrative.velocity}</p>
                <p className="text-sm text-gray-300 mt-2 line-clamp-3">{narrative.blurb}</p>
              </Link>
            ))}
          </div>
        </section>

        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-gray-400">Creator spotlight</p>
              <p className="text-sm text-gray-400">Channels most influential for this destination.</p>
            </div>
            <span className="text-xs text-gray-400">{destination.spotlight.length} featured</span>
          </div>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {destination.spotlight.map((creator) => (
              <div
                key={creator.name}
                className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/5 p-4 shadow-lg shadow-black/30"
              >
                <img
                  src={creator.avatar}
                  alt={creator.name}
                  className="h-12 w-12 rounded-full border border-white/10 object-cover"
                />
                <div className="space-y-1">
                  <p className="text-sm font-semibold text-white">{creator.name}</p>
                  <p className="text-xs text-gray-300">{creator.subs} • {creator.uploads}</p>
                  <p className="text-xs text-gray-400">{creator.focus}</p>
                </div>
              </div>
            ))}
          </div>
        </section>
        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-gray-400">Highlights</p>
              <p className="text-sm text-gray-400">Top themes driving engagement.</p>
            </div>
            <span className="text-xs text-gray-400">{destination.highlights.length} tags</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {destination.highlights.map((tag) => (
              <span key={tag} className="rounded-full bg-white/5 border border-white/10 px-3 py-2 text-xs text-gray-200">
                {tag}
              </span>
            ))}
          </div>
        </section>
      </div>
    </div>
  )
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-4 shadow-inner shadow-black/30">
      <p className="text-[11px] uppercase tracking-wide text-gray-400">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-white">{value}</p>
    </div>
  )
}
