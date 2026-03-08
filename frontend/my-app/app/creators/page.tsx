"use client"

import { useMemo, useState } from "react"

type Creator = {
  name: string
  region: "Americas" | "EMEA" | "APAC"
  domain: string
  subscribers: number
  monthlyViews: number
  contentType: "Travel" | "Food" | "Lifestyle/Vlog" | "Wellness" | "Tech" | "Entertainment" | "News"
  videos: { title: string; views: string; img: string; link: string }[]
}

const creators: Creator[] = [
  {
    name: "Trail Theory",
    region: "Americas",
    domain: "Backpacking & ultralight gear",
    subscribers: 1200000,
    monthlyViews: 18000000,
    contentType: "Travel",
    videos: [
      { title: "3-day loop with a 9lb pack", views: "2.1M views", img: "/images/trail-theory-1.jpg", link: "/videos/trail-theory-1" },
      { title: "Rain test: budget shells vs Gore-Tex", views: "1.4M views", img: "/images/trail-theory-2.jpg", link: "/videos/trail-theory-2" },
      { title: "Caffeine & camp stoves showdown", views: "940k views", img: "/images/trail-theory-3.jpg", link: "/videos/trail-theory-3" },
    ],
  },
  {
    name: "Canyon & Coffee",
    region: "Americas",
    domain: "Weekend hikes & campsite coffee rituals",
    subscribers: 420000,
    monthlyViews: 5600000,
    contentType: "Travel",
    videos: [
      { title: "Sedona sunrise + AeroPress kit", views: "620k views", img: "/images/canyon-coffee-1.jpg", link: "/videos/canyon-coffee-1" },
      { title: "Overnight pack list under 20 lbs", views: "510k views", img: "/images/canyon-coffee-2.jpg", link: "/videos/canyon-coffee-2" },
      { title: "Budget trail runners vs boots", views: "430k views", img: "/images/canyon-coffee-3.jpg", link: "/videos/canyon-coffee-3" },
    ],
  },
  {
    name: "MetroBites",
    region: "EMEA",
    domain: "City food crawls & night markets",
    subscribers: 980000,
    monthlyViews: 13200000,
    contentType: "Food",
    videos: [
      { title: "72 hours eating Lisbon", views: "1.1M views", img: "/images/metro-bites-1.jpg", link: "/videos/metro-bites-1" },
      { title: "Late-night kebabs in Berlin", views: "870k views", img: "/images/metro-bites-2.jpg", link: "/videos/metro-bites-2" },
      { title: "Street food price check: Athens", views: "740k views", img: "/images/metro-bites-3.jpg", link: "/videos/metro-bites-3" },
    ],
  },
  {
    name: "Signal & Skyline",
    region: "APAC",
    domain: "Drone city guides & skyline walks",
    subscribers: 1560000,
    monthlyViews: 21000000,
    contentType: "Lifestyle/Vlog",
    videos: [
      { title: "Seoul night markets from above", views: "2.4M views", img: "/images/signal-skyline-1.jpg", link: "/videos/signal-skyline-1" },
      { title: "Tokyo rail loop in 12 minutes", views: "1.9M views", img: "/images/signal-skyline-2.jpg", link: "/videos/signal-skyline-2" },
      { title: "Bangkok rooftops on a budget", views: "1.2M views", img: "/images/signal-skyline-3.jpg", link: "/videos/signal-skyline-3" },
    ],
  },
  {
    name: "Carry-On Lab",
    region: "EMEA",
    domain: "Carry-on packing science & gear reviews",
    subscribers: 310000,
    monthlyViews: 4100000,
    contentType: "Tech",
    videos: [
      { title: "Backpack stress test: 7 brands", views: "360k views", img: "/images/carry-on-lab-1.jpg", link: "/videos/carry-on-lab-1" },
      { title: "Capsule wardrobe for 10 days", views: "290k views", img: "/images/carry-on-lab-2.jpg", link: "/videos/carry-on-lab-2" },
      { title: "Noise-cancelling showdown", views: "270k views", img: "/images/carry-on-lab-3.jpg", link: "/videos/carry-on-lab-3" },
    ],
  },
  {
    name: "Coastal Signals",
    region: "APAC",
    domain: "Surf towns, ferries, and coastal routes",
    subscribers: 640000,
    monthlyViews: 9200000,
    contentType: "Travel",
    videos: [
      { title: "Island-hop Japan by ferry", views: "780k views", img: "/images/coastal-signals-1.jpg", link: "/videos/coastal-signals-1" },
      { title: "Cheap surf week in Taiwan", views: "620k views", img: "/images/coastal-signals-2.jpg", link: "/videos/coastal-signals-2" },
      { title: "Waterproof bags that actually seal", views: "510k views", img: "/images/coastal-signals-3.jpg", link: "/videos/coastal-signals-3" },
    ],
  },
]

const regions = ["All regions", "Americas", "EMEA", "APAC"] as const
const subscriberBuckets = ["Any size", "< 250k", "250k - 1M", "> 1M"] as const
const viewBuckets = ["Any views", "< 5M / mo", "5M - 15M / mo", "> 15M / mo"] as const
const contentTypes = ["All types", "Travel", "Food", "Lifestyle/Vlog", "Wellness", "Tech", "Entertainment", "News"] as const

export default function CreatorsPage() {
  const [region, setRegion] = useState<(typeof regions)[number]>("All regions")
  const [subs, setSubs] = useState<(typeof subscriberBuckets)[number]>("Any size")
  const [views, setViews] = useState<(typeof viewBuckets)[number]>("Any views")
  const [type, setType] = useState<(typeof contentTypes)[number]>("All types")

  const filtered = useMemo(() => {
    return creators.filter((creator) => {
      const regionOk = region === "All regions" || creator.region === region
      const typeOk = type === "All types" || creator.contentType === type
      const subsOk =
        subs === "Any size" ||
        (subs === "< 250k" && creator.subscribers < 250000) ||
        (subs === "250k - 1M" && creator.subscribers >= 250000 && creator.subscribers <= 1000000) ||
        (subs === "> 1M" && creator.subscribers > 1000000)
      const viewsOk =
        views === "Any views" ||
        (views === "< 5M / mo" && creator.monthlyViews < 5000000) ||
        (views === "5M - 15M / mo" && creator.monthlyViews >= 5000000 && creator.monthlyViews <= 15000000) ||
        (views === "> 15M / mo" && creator.monthlyViews > 15000000)

      return regionOk && typeOk && subsOk && viewsOk
    })
  }, [region, subs, type, views])

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0b0b0e] via-[#0f1018] to-[#0b0b0e] text-white">
      <div className="mx-auto max-w-6xl px-6 pb-16 pt-10 space-y-10">
        <header className="space-y-3">
          <p className="text-xs uppercase tracking-[0.3em] text-gray-400">Creators</p>
          <h1 className="text-4xl font-semibold leading-tight">Find creators to sponsor</h1>
          <p className="text-sm text-gray-300 max-w-3xl">
            Filter by region, audience size, and format to spot creators with strong disclosure history and brand-safe
            audiences.
          </p>
        </header>

        <section className="rounded-2xl border border-white/10 bg-gradient-to-b from-[#141420] via-[#10101a] to-[#0c0c12] p-5 shadow-xl shadow-black/40">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <FilterSelect label="Region" value={region} options={regions} onChange={setRegion} />
            <FilterSelect label="Subscribers" value={subs} options={subscriberBuckets} onChange={setSubs} />
            <FilterSelect label="Monthly views" value={views} options={viewBuckets} onChange={setViews} />
            <FilterSelect label="Content type" value={type} options={contentTypes} onChange={setType} />
          </div>
          <p className="mt-4 text-xs text-gray-400">
            Showing {filtered.length} of {creators.length} creators · Filters update instantly.
          </p>
        </section>

        <section className="grid gap-4 md:grid-cols-2">
          {filtered.map((creator) => (
            <article
              key={creator.name}
              className="rounded-2xl border border-white/10 bg-gradient-to-b from-[#1c1420] via-[#140f17] to-[#0c0c12] p-5 shadow-2xl shadow-black/50"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="space-y-1">
                  <h2 className="text-xl font-semibold text-white">{creator.name}</h2>
                  <p className="text-sm text-gray-400">{creator.domain}</p>
                  <p className="text-xs text-gray-500">{creator.region}</p>
                </div>
                <span className="rounded-full bg-emerald-400/15 px-3 py-1 text-[11px] uppercase tracking-wide text-emerald-200">
                  Brand safe
                </span>
              </div>

              <div className="mt-4 grid grid-cols-2 gap-3 text-xs text-gray-300">
                <Stat label="Subscribers" value={formatNumber(creator.subscribers)} />
                <Stat label="Monthly views" value={formatNumber(creator.monthlyViews)} />
                <Stat label="Content type" value={creator.contentType} />
                <Stat label="Typical CPM" value="$18–$26" />
              </div>

              <div className="mt-4 space-y-2">
                <p className="text-xs uppercase tracking-[0.18em] text-gray-400">Recent videos</p>
                <div className="space-y-2 text-sm text-gray-200">
                  {creator.videos.map((video) => (
                    <div
                      key={video.title}
                      className="flex items-center justify-between rounded-xl border border-white/5 bg-white/5 px-3 py-2"
                    >
                      <span className="line-clamp-1">{video.title}</span>
                      <span className="text-xs text-gray-400">{video.views}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="mt-4 flex flex-wrap gap-2 text-[11px] uppercase tracking-wide text-gray-200">
                <span className="rounded-full bg-white/10 px-3 py-1">Disclosure: clean</span>
                <span className="rounded-full bg-white/10 px-3 py-1">Formats: long + short</span>
                <span className="rounded-full bg-white/10 px-3 py-1">Requests: open</span>
              </div>
            </article>
          ))}
        </section>
      </div>
    </div>
  )
}

type FilterProps<T extends readonly string[]> = {
  label: string
  value: T[number]
  options: T
  onChange: (value: T[number]) => void
}

function FilterSelect<T extends readonly string[]>({ label, value, options, onChange }: FilterProps<T>) {
  return (
    <label className="space-y-2 text-sm font-medium text-gray-200">
      <span className="block text-xs uppercase tracking-[0.18em] text-gray-400">{label}</span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value as T[number])}
        className="w-full rounded-xl border border-white/10 bg-[#16161e] px-4 py-3 text-sm text-gray-100 shadow-inner shadow-black/30 focus:border-white/25 focus:outline-none"
      >
        {options.map((option) => (
          <option key={option}>{option}</option>
        ))}
      </select>
    </label>
  )
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/5 px-3 py-2">
      <p className="text-[10px] uppercase tracking-wide text-gray-400">{label}</p>
      <p className="text-sm font-semibold text-white">{value}</p>
    </div>
  )
}

function formatNumber(value: number) {
  if (value >= 1000000) return `${(value / 1000000).toFixed(1).replace(/\.0$/, "")}M`
  if (value >= 1000) return `${Math.round(value / 1000)}k`
  return value.toString()
}
