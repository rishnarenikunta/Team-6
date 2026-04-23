"use client"

import Link from "next/dist/client/link"
import { useMemo, useState, useEffect } from "react"


type Creator = {
  slug: string
  name: string
  // region: "Americas" | "EMEA" | "APAC"
  domain: string
  subscribers: number
  monthlyViews: number
  contentType: "Travel" | "Food" | "Lifestyle/Vlog" | "Wellness" | "Tech" | "Entertainment" | "News"
  videos: { title: string; views: string; img: string; link: string }[]
  commentVolume30d: number
  sentiment: { positive: number; neutral: number; negative: number }
  spotlightComment: string
}

type ApiCreator = {
  channel_id: string,
  name: string,
  subscriber_count: number,
  views: number,
  top_claim: string,
  cluster_size: number,
  computed_at: string
}

type ApiCreatorsResponse = {
  channel_id: string
  creator_name: string
  subscriber_count: number
  views: number
  comment_volume: number
  videos: {
      video_id: string
      title: string
      view_count: number
      like_count: number
      comment_count: number
      webpage_url: string
      upload_date: string
  }[]
}

// const regions = ["All regions", "Americas", "EMEA", "APAC"] as const
const subscriberBuckets = ["Any size", "< 250k", "250k - 1M", "> 1M"] as const
const viewBuckets = ["Any views", "< 5M / mo", "5M - 15M / mo", "> 15M / mo"] as const
const contentTypes = ["All types", "Travel", "Food", "Lifestyle/Vlog", "Wellness", "Tech", "Entertainment", "News"] as const

export default function CreatorsPage() {

  const [creators, setCreators] = useState<ApiCreatorsResponse[]>([]);

  useEffect(() => {
    async function fetchCreators() {
      try {
        const res = await fetch(`/api/creators`);
        if (!res.ok) throw new Error(`API error ${res.status}`);
        const data: ApiCreatorsResponse[] = await res.json();
        console.log("Raw API creator data:", data);
        // const mapped: Creator[] = data.map((item) => ({
        //   slug: item.channel_id ?? "unknown",
        //   name: item.name ?? "Unknown creator",
        //   // region: "Americas",                     // default until API supplies region
        //   domain: "Travel creator",               // default domain
        //   subscribers: item.subscriber_count ?? 0,
        //   monthlyViews: item.views ?? 0,
        //   contentType: "Travel",                  // default content type
        //   videos: [
        //     {
        //       title: item.top_claim || "Recent claim unavailable",
        //       views: `${formatNumber(item.views ?? 0)} views`,
        //       img: "/images/placeholder.jpg",
        //       link: "#",
        //     },
        //   ],
        //   commentVolume30d: item.cluster_size ?? 0,
        //   sentiment: { positive: 60, neutral: 30, negative: 10 }, // placeholder split
        //   spotlightComment: item.top_claim || "No spotlight comment available.",
        // }));
        setCreators(data);
        console.log("Fetched creators:", data);
      } catch (err) {
        console.error("Fetch error:", err);
      }
    }
    fetchCreators();
  }, []);

  
  // const [region, setRegion] = useState<(typeof regions)[number]>("All regions")
  const [subs, setSubs] = useState<(typeof subscriberBuckets)[number]>("Any size")
  const [views, setViews] = useState<(typeof viewBuckets)[number]>("Any views")
  const [type, setType] = useState<(typeof contentTypes)[number]>("All types")
  // const [rankingRegion, setRankingRegion] = useState<Creator["region"]>("Americas")

  const filtered = useMemo(() => {
    return creators.filter((creator) => {
      // const regionOk = region === "All regions" || creator.region === region
      // const typeOk = type === "All types" || creator.contentType === type
      const subsOk =
        subs === "Any size" ||
        (subs === "< 250k" && creator.subscriber_count < 250000) ||
        (subs === "250k - 1M" && creator.subscriber_count >= 250000 && creator.subscriber_count <= 1000000) ||
        (subs === "> 1M" && creator.subscriber_count > 1000000)
      const viewsOk =
        views === "Any views" ||
        (views === "< 5M / mo" && creator.views < 5000000) ||
        (views === "5M - 15M / mo" && creator.views >= 5000000 && creator.views <= 15000000) ||
        (views === "> 15M / mo" && creator.views > 15000000)

      return subsOk && viewsOk
    })
  }, [creators, subs, type, views])

  // const regionalRankings = useMemo(() => {
  //   const groups: Record<string, Creator[]> = { Americas: [], EMEA: [], APAC: [] }
  //   creators.forEach((c) => {
  //     groups[c.region].push(c)
  //   })
  //   return (Object.entries(groups) as [Creator["region"], Creator[]][])
  //     .map(([reg, list]) => ({
  //       region: reg,
  //       top: [...list].sort((a, b) => b.subscribers - a.subscribers).slice(0, 5),
  //     }))
  // }, [creators])


  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0b0b0e] via-[#0f1018] to-[#0b0b0e] text-white">
      <div className="mx-auto max-w-6xl px-6 pb-16 pt-10 space-y-10">
        <header className="space-y-3">
          <p className="text-xs uppercase tracking-[0.3em] text-gray-400">Creators</p>
          <h1 className="text-4xl font-semibold leading-tight">Find creators to sponsor</h1>
          <p className="text-sm text-gray-300 max-w-3xl">
            Filter by audience size and format to spot creators with strong disclosure history and brand-safe
            audiences.
          </p>
        </header>

        <section className="rounded-2xl border border-white/10 bg-[#0f0f17] p-5 shadow-none">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 shadow-none">
            {/* <FilterSelect label="Region" value={region} options={regions} onChange={setRegion} /> */}
            <FilterSelect label="Subscribers" value={subs} options={subscriberBuckets} onChange={setSubs} />
            <FilterSelect label="Monthly views" value={views} options={viewBuckets} onChange={setViews} />
            <FilterSelect label="Content type" value={type} options={contentTypes} onChange={setType} />
          </div>
          <p className="mt-4 text-xs text-gray-400">
            Showing {filtered.length} of {creators.length} creators · Filters update instantly.
          </p>
        </section>

        <section className="grid gap-6 lg:grid-cols-[2fr_1fr]">
          <div className="grid gap-4 md:grid-cols-2">
            {filtered.map((creator) => (
              <Link key={creator.creator_name} href={`/creators/${creator.channel_id}`} className="block">
            <article
              key={creator.creator_name}
              className="rounded-2xl border border-white/10 p-5 shadow-2xl shadow-black/50"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="space-y-1">
                  <h2 className="text-xl font-semibold text-white">{creator.creator_name}</h2>
                  {/* <p className="text-sm text-gray-400">{creator.}</p> */}
                  {/* <p className="text-xs text-gray-500">{creator.region}</p> */}
                </div>
                <span className="rounded-full bg-emerald-400/15 px-3 py-1 text-[11px] uppercase tracking-wide text-emerald-200">
                  Brand safe
                </span>
              </div>

              {/* STATS SECTION */}
              <div className="mt-4 grid grid-cols-2 gap-3 text-xs text-gray-300">
                <Stat label="Subscribers" value={formatNumber(creator.subscriber_count)} />
                {/* <Stat label="Typical CPM" value="$18–$26" /> */}
              </div>

              {/* RECENT VIDEOS SECTION */}
              <div className="mt-4 space-y-2">
                <p className="text-xs uppercase tracking-[0.18em] text-gray-400">Recent Videos</p>
                <div className="space-y-2 text-sm text-gray-200">
                  {creator.videos.length === 0 ? (
                    <div className="rounded-xl border border-dashed border-white/10 bg-white/5 px-3 py-3 text-xs text-gray-400">
                      No recent videos found for this channel. Check back soon.
                    </div>
                  ) : (
                    creator.videos.slice(0, 5).map((video) => (
                      <div
                        key={video.title}
                        className="grid grid-cols-[1fr_auto] gap-2 items-center rounded-xl border border-white/5 bg-white/5 px-3 py-2 hover:border-white/15 transition"
                      >
                        <div className="space-y-1">
                          <Link href={video.webpage_url}>
                            <span className="line-clamp-2 font-medium hover:text-white">{video.title}</span>
                          </Link>
                          <div className="flex flex-wrap gap-2 text-[11px] text-gray-400">
                            <span>{video.upload_date || "Date n/a"}</span>
                            {/* <span className="rounded-full bg-white/10 px-2 py-0.5">
                              {formatNumber(video.view_count)} views
                            </span> */}
                            <span className="rounded-full bg-white/10 px-2 py-0.5">
                              {formatNumber(video.like_count)} likes
                            </span>
                            <span className="rounded-full bg-white/10 px-2 py-0.5">
                              {formatNumber(video.comment_count)} comments
                            </span>
                          </div>
                        </div>
                        <span className="text-[11px] uppercase tracking-wide text-emerald-200 bg-emerald-400/10 px-2 py-1 rounded">
                          New
                        </span>
                      </div>
                    ))
                  )}
                </div>
              </div>

              {/* COMMENT SENTIMENT SECTION */}
              {/* <div className="mt-4 space-y-2">
                <p className="text-xs uppercase tracking-[0.18em] text-gray-400">Comment Sentiment</p>
                <div className="flex items-center gap-1 mt-1">
                  <div className="flex-1 bg-white/5 rounded-full h-3 overflow-hidden">
                    <div
                      className="h-full bg-[#E4CAFF]"
                      style={{ width: `${creator.sentiment.positive}%` }}
                    />
                  </div>
                  <span className="text-xs text-gray-400">{creator.sentiment.positive}% positive</span>
                </div>
              </div> */}
            </article>
            </Link>
            ))}
          </div>

          {/* REGIONAL RANKING SECTION */}
          <aside className="rounded-2xl bg-[#E4CAFF] p-5 space-y-4 h-fit lg:sticky lg:top-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.25em] text-gray-900">Top ranking</p>
                <p className="text-sm text-gray-800">Leaders by subscribers.</p>
              </div>
            </div>
            <div className="space-y-2">
              {[...creators].sort((a, b) => b.subscriber_count - a.subscriber_count).slice(0, 5).map((c, idx) => (
                <div key={c.channel_id} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-gray-800">
                  <div className="flex items-center gap-2">
                    <span className="text-[11px] text-gray-800">{idx + 1}.</span>
                    <Link href={`/creators/${c.channel_id}`} className="hover:text-white font-semibold">{c.creator_name}</Link>
                  </div>
                  <span className="text-xs text-gray-800">{c.subscriber_count.toLocaleString()} subs</span>
                </div>
              ))}
            </div>
          </aside>
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
        className="w-full rounded-lg border border-white/15 bg-[#0c0c14] px-4 py-3 text-sm text-gray-100 focus:border-purple-300 focus:outline-none focus:ring-2 focus:ring-purple-500/30 shadow-none"
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
