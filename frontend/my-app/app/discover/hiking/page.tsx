import Link from "next/link"

const stats = [
  { label: "Active creators (30d)", value: "210", note: "steady upward trend" },
  { label: "Watch time (30d)", value: "12.4M hrs", note: "+17% vs prior 30d" },
  { label: "Avg engagement", value: "6.8%", note: "high comments on gear lists" },
  { label: "Brand safety", value: "Low risk", note: "family-friendly, gear-focused" },
]

const creators = [
  {
    name: "Trail Theory",
    region: "US West",
    reach: "1.2M subs · 4.1% ER",
    focus: "Ultralight tips, thru-hike prep, pack shakedowns",
    formats: ["10-15 min YT", "Shorts", "IG Reels"],
  },
  {
    name: "Summit Signals",
    region: "DACH",
    reach: "640k subs · 7.4% ER",
    focus: "Alpine routes, avalanche safety explainers, winter gear",
    formats: ["Long-form", "Gear reviews", "Guides"],
  },
  {
    name: "Canyon & Coffee",
    region: "US Southwest",
    reach: "420k subs · 5.9% ER",
    focus: "Weekend loop itineraries, sunrise photosets, campsite coffee",
    formats: ["B-roll heavy", "TikTok", "Photo carousels"],
  },
]

const regions = [
  { name: "US National Parks", trend: "+12% uploads", note: "Zion, Yosemite, Glacier in shoulder season" },
  { name: "Alps (FR/CH/AT)", trend: "+9% uploads", note: "Via ferrata + hut-to-hut demand" },
  { name: "Patagonia", trend: "+7% uploads", note: "Torres del Paine W trek planning season" },
]

export default function HikingKeywordPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0b0b0e] via-[#0f1018] to-[#0b0b0e] text-white">
      <div className="mx-auto max-w-6xl px-6 pb-16 pt-10 space-y-10">
        <div className="flex items-center gap-3 text-sm text-gray-400">
          <Link href="/discover" className="underline underline-offset-4 decoration-white/30 hover:text-white">
            Discover
          </Link>
          <span className="text-gray-600">/</span>
          <span className="text-white">Hiking</span>
        </div>

        <header className="space-y-3">
          <p className="text-xs uppercase tracking-[0.3em] text-gray-400">Keyword</p>
          <h1 className="text-4xl font-semibold leading-tight">Hiking creators & sponsorship prospects</h1>
          <p className="text-sm text-gray-300 max-w-3xl">
            Real-time view of hiking content velocity, regions that are peaking, and creator lanes ready for brand
            partnerships. Built for outdoor, apparel, hydration, and energy brands looking to sponsor credible guides.
          </p>
        </header>

        <section className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {stats.map((stat) => (
            <div
              key={stat.label}
              className="rounded-2xl border border-white/10 bg-gradient-to-b from-[#161623] via-[#12121b] to-[#0c0c12] p-4 shadow-lg shadow-black/40"
            >
              <p className="text-xs uppercase tracking-[0.18em] text-gray-400">{stat.label}</p>
              <p className="mt-2 text-2xl font-semibold text-white">{stat.value}</p>
              <p className="text-xs text-gray-400">{stat.note}</p>
            </div>
          ))}
        </section>

        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-gray-400">Creator short list</p>
              <p className="text-sm text-gray-300">Pre-filtered for safety, disclosure history, and recent engagement.</p>
            </div>
            <button className="rounded-xl bg-[#E4CAFF] px-4 py-2 text-sm font-medium text-black transition hover:bg-white">
              Build sponsor brief
            </button>
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            {creators.map((creator) => (
              <article
                key={creator.name}
                className="rounded-2xl border border-white/10 bg-gradient-to-b from-[#1b1722] via-[#14121c] to-[#0c0c12] p-5 shadow-xl shadow-black/40"
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h3 className="text-lg font-semibold text-white">{creator.name}</h3>
                    <p className="text-xs text-gray-400">{creator.region}</p>
                  </div>
                  <span className="rounded-full bg-emerald-400/15 px-3 py-1 text-[11px] uppercase tracking-wide text-emerald-200">
                    Brand safe
                  </span>
                </div>
                <p className="mt-3 text-sm text-gray-200">{creator.focus}</p>
                <p className="mt-3 text-sm font-medium text-blue-200">{creator.reach}</p>
                <div className="mt-4 flex flex-wrap gap-2 text-[11px] uppercase tracking-wide text-gray-200">
                  {creator.formats.map((format) => (
                    <span key={format} className="rounded-full bg-white/5 px-3 py-1">
                      {format}
                    </span>
                  ))}
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="grid gap-6 lg:grid-cols-2">
          <div className="rounded-2xl border border-white/10 bg-gradient-to-b from-[#161623] via-[#12121b] to-[#0c0c12] p-5 shadow-lg shadow-black/40 space-y-4">
            <h2 className="text-lg font-semibold text-white">Audience signals</h2>
            <ul className="space-y-3 text-sm text-gray-200">
              <li className="flex gap-3">
                <span className="h-2 w-2 mt-2 rounded-full bg-emerald-400" />
                Gear haul videos with affiliate links are converting 2.1x better than itineraries.
              </li>
              <li className="flex gap-3">
                <span className="h-2 w-2 mt-2 rounded-full bg-blue-300" />
                Safety and Leave No Trace checklists drive the longest watch time and highest save rates.
              </li>
              <li className="flex gap-3">
                <span className="h-2 w-2 mt-2 rounded-full bg-amber-300" />
                Sunrise/coffee rituals and lightweight cooking gear skew female 25-34, coastal US + UK.
              </li>
            </ul>
            <div className="flex flex-wrap gap-2 text-[11px] uppercase tracking-wide text-gray-200">
              {["packs", "hydration", "trail runners", "action cams", "nutrition"].map((tag) => (
                <span key={tag} className="rounded-full bg-white/5 px-3 py-1">
                  {tag}
                </span>
              ))}
            </div>
          </div>

          <div className="rounded-2xl border border-white/10 bg-gradient-to-b from-[#161623] via-[#12121b] to-[#0c0c12] p-5 shadow-lg shadow-black/40 space-y-4">
            <h2 className="text-lg font-semibold text-white">Regional hotspots</h2>
            <div className="space-y-3">
              {regions.map((region) => (
                <div key={region.name} className="rounded-xl border border-white/10 bg-white/5 px-4 py-3">
                  <p className="text-sm font-semibold text-white">{region.name}</p>
                  <p className="text-xs text-blue-200">{region.trend}</p>
                  <p className="text-xs text-gray-400">{region.note}</p>
                </div>
              ))}
            </div>
            <p className="text-xs text-gray-400">
              Signals aggregate uploads, comments mentioning specific trails, and creator location tags over the last 30
              days.
            </p>
          </div>
        </section>

        <section className="rounded-2xl border border-white/10 bg-gradient-to-r from-[#24162d] via-[#1a1422] to-[#0f1018] p-6 shadow-2xl shadow-black/50">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div className="space-y-2">
              <p className="text-xs uppercase tracking-[0.2em] text-gray-300">Sponsor playbook</p>
              <h3 className="text-xl font-semibold text-white">Ready-to-run sponsorship angles</h3>
              <p className="text-sm text-gray-300">
                Ship a sample brief and get a matched list of creators with pricing bands, disclosure history, and first
                available mid-roll slots.
              </p>
            </div>
            <div className="flex gap-2">
              <button className="rounded-xl bg-white/10 px-4 py-2 text-sm font-medium text-white transition hover:bg-white/20">
                Preview brief
              </button>
              <button className="rounded-xl bg-[#E4CAFF] px-4 py-2 text-sm font-medium text-black transition hover:bg-white">
                Start matching
              </button>
            </div>
          </div>
        </section>
      </div>
    </div>
  )
}
