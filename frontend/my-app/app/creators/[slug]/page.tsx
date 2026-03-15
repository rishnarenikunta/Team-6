import Link from "next/link"

type ContentCreator = {
  slug: string
  name: string
  region: "Americas" | "EMEA" | "APAC"
  domain: string
  subscribers: number
  monthlyViews: number
  contentType: "Travel" | "Food" | "Lifestyle/Vlog" | "Wellness" | "Tech" | "Entertainment" | "News"
  videos: { title: string; views: string; img: string; link: string }[]
  profilePhoto?: string
  commentVolume30d: number
  sentiment: { positive: number; neutral: number; negative: number }
  topThemes: string[]
  highlightedComments: string[]
}

const creators: ContentCreator[] = [
  {
    slug: "trail-theory",
    name: "Nicole Laena",
    region: "EMEA",
    domain: "Day in my life + travel",
    subscribers: 3200000,
    monthlyViews: 18000000,
    contentType: "Travel",
    commentVolume30d: 18400,
    sentiment: { positive: 71, neutral: 23, negative: 6 },
    topThemes: ["italy tourism", "day in my life", "lightweight coffee setups"],
    highlightedComments: [
      "Gear lists are actually realistic—no fluff, just what works on trail.",
      "Appreciate the wet-weather tests before I buy anything.",
    ],
    videos: [
      { title: "3-day loop with a 9lb pack", views: "2.1M views", img: "/images/trail-theory-1.png", link: "https://www.youtube.com/watch?v=w6FylJ9I7M8" },
      { title: "Rain test: budget shells vs Gore-Tex", views: "1.4M views", img: "/images/trail-theory-2.png", link: "/videos/trail-theory-2" },
      { title: "Caffeine & camp stoves showdown", views: "940k views", img: "/images/trail-theory-3.png", link: "/videos/trail-theory-3" },
    ],
    profilePhoto: "/images/trail-theory.png",
  },
  {
    slug: "canyon-coffee",
    name: "Canyon & Coffee",
    region: "Americas",
    domain: "Weekend hikes & campsite coffee rituals",
    subscribers: 420000,
    monthlyViews: 5600000,
    contentType: "Travel",
    commentVolume30d: 7600,
    sentiment: { positive: 64, neutral: 28, negative: 8 },
    topThemes: ["coffee recipes", "budget gear", "beginner routes"],
    highlightedComments: [
      "Love that you include brew temps—helps me replicate the coffee on trail!",
      "Please keep the under-$50 gear recs coming, super helpful.",
    ],
    videos: [
      { title: "Sedona sunrise + AeroPress kit", views: "620k views", img: "/images/canyon-coffee-1.jpg", link: "/videos/canyon-coffee-1" },
      { title: "Overnight pack list under 20 lbs", views: "510k views", img: "/images/canyon-coffee-2.jpg", link: "/videos/canyon-coffee-2" },
      { title: "Budget trail runners vs boots", views: "430k views", img: "/images/canyon-coffee-3.jpg", link: "/videos/canyon-coffee-3" },
    ],
    profilePhoto: "/images/canyon-coffee-1.jpg",
  },
  {
    slug: "metro-bites",
    name: "MetroBites",
    region: "EMEA",
    domain: "City food crawls & night markets",
    subscribers: 980000,
    monthlyViews: 13200000,
    contentType: "Food",
    commentVolume30d: 15200,
    sentiment: { positive: 69, neutral: 21, negative: 10 },
    topThemes: ["maps & price notes", "late-night options", "street food hygiene"],
    highlightedComments: [
      "Maps + prices in the description are clutch for planning trips.",
      "Thanks for including veggie options—super helpful.",
    ],
    videos: [
      { title: "72 hours eating Lisbon", views: "1.1M views", img: "/images/metro-bites-1.jpg", link: "/videos/metro-bites-1" },
      { title: "Late-night kebabs in Berlin", views: "870k views", img: "/images/metro-bites-2.jpg", link: "/videos/metro-bites-2" },
      { title: "Street food price check: Athens", views: "740k views", img: "/images/metro-bites-3.jpg", link: "/videos/metro-bites-3" },
    ],
    profilePhoto: "/images/metro-bites-1.jpg",
  },
  {
    slug: "signal-skyline",
    name: "Signal & Skyline",
    region: "APAC",
    domain: "Drone city guides & skyline walks",
    subscribers: 1560000,
    monthlyViews: 21000000,
    contentType: "Lifestyle/Vlog",
    commentVolume30d: 23800,
    sentiment: { positive: 73, neutral: 19, negative: 8 },
    topThemes: ["route planning", "budget tips", "camera gear"],
    highlightedComments: [
      "These aerial routes made my Seoul trip—followed them step for step!",
      "Please keep adding transit notes, super helpful at night.",
    ],
    videos: [
      { title: "Seoul night markets from above", views: "2.4M views", img: "/images/signal-skyline-1.jpg", link: "/videos/signal-skyline-1" },
      { title: "Tokyo rail loop in 12 minutes", views: "1.9M views", img: "/images/signal-skyline-2.jpg", link: "/videos/signal-skyline-2" },
      { title: "Bangkok rooftops on a budget", views: "1.2M views", img: "/images/signal-skyline-3.jpg", link: "/videos/signal-skyline-3" },
    ],
    profilePhoto: "/images/signal-skyline-1.jpg",
  },
  {
    slug: "carry-on-lab",
    name: "Carry-On Lab",
    region: "EMEA",
    domain: "Carry-on packing science & gear reviews",
    subscribers: 310000,
    monthlyViews: 4100000,
    contentType: "Tech",
    commentVolume30d: 4200,
    sentiment: { positive: 61, neutral: 30, negative: 9 },
    topThemes: ["small-frame fit", "compression tests", "budget picks"],
    highlightedComments: [
      "Finally someone measures fit + straps for smaller frames—instant subscribe.",
      "Compression cube tests were more helpful than most blog posts.",
    ],
    videos: [
      { title: "Backpack stress test: 7 brands", views: "360k views", img: "/images/carry-on-lab-1.jpg", link: "/videos/carry-on-lab-1" },
      { title: "Capsule wardrobe for 10 days", views: "290k views", img: "/images/carry-on-lab-2.jpg", link: "/videos/carry-on-lab-2" },
      { title: "Noise-cancelling showdown", views: "270k views", img: "/images/carry-on-lab-3.jpg", link: "/videos/carry-on-lab-3" },
    ],
    profilePhoto: "/images/carry-on-lab-1.jpg",
  },
  {
    slug: "coastal-signals",
    name: "Coastal Signals",
    region: "APAC",
    domain: "Surf towns, ferries, and coastal routes",
    subscribers: 640000,
    monthlyViews: 9200000,
    contentType: "Travel",
    commentVolume30d: 9800,
    sentiment: { positive: 67, neutral: 24, negative: 9 },
    topThemes: ["ferry timing", "budget stays", "surf conditions"],
    highlightedComments: [
      "Appreciate the ferry schedules + budget hotels in one place—saved so much time.",
      "Clear on surf seasons; helped me move my trip earlier.",
    ],
    videos: [
      { title: "Island-hop Japan by ferry", views: "780k views", img: "/images/coastal-signals-1.jpg", link: "/videos/coastal-signals-1" },
      { title: "Cheap surf week in Taiwan", views: "620k views", img: "/images/coastal-signals-2.jpg", link: "/videos/coastal-signals-2" },
      { title: "Waterproof bags that actually seal", views: "510k views", img: "/images/coastal-signals-3.jpg", link: "/videos/coastal-signals-3" },
    ],
    profilePhoto: "/images/coastal-signals-1.jpg",
  },
]

const formatNumber = (value: number) =>
  value.toLocaleString("en-US", { notation: "compact", maximumFractionDigits: 1 })

type Params = { params: Promise<{ slug: string }> }

export default async function CreatorDetailPage({ params }: Params) {
  const { slug } = await params
  const creator = creators.find((c) => c.slug === slug)
  const avatar = creator?.profilePhoto ?? creator?.videos[0]?.img ?? ""

  if (!creator) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-[#0b0b10] via-[#0f1018] to-[#0b0b10] text-white flex items-center justify-center">
        <p className="text-gray-300">Creator not found.</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0b0b10] via-[#0f1018] to-[#0b0b10] text-white">
      <div className="max-w-6xl mx-auto px-6 pb-16 pt-12 space-y-10">
        <div className="flex items-center gap-2 text-sm text-gray-400">
          <Link href="/creators" className="underline underline-offset-4 decoration-white/30 hover:text-white">
            Creators
          </Link>
          <span className="text-gray-600">/</span>
          <span className="text-gray-200">{creator.name}</span>
        </div>

        <header className="space-y-4">
          <div className="flex items-start gap-4">
            <div className="h-16 w-16 rounded-full border border-white/10 bg-gradient-to-br from-purple-500/30 to-indigo-500/30 overflow-hidden flex items-center justify-center">
              {avatar ? <img src={avatar} alt={creator.name} className="h-full w-full object-cover" /> : <span className="text-xs text-gray-100">YT</span>}
            </div>
            <div className="space-y-3">
              <div className="flex flex-wrap items-center gap-2 text-[11px] uppercase tracking-wide text-gray-200">
                <span className="rounded-full bg-emerald-500/15 text-emerald-200 px-3 py-1">{creator.region}</span>
                <span className="rounded-full bg-white/10 px-3 py-1">{creator.contentType}</span>
                <span className="rounded-full bg-white/10 px-3 py-1">{formatNumber(creator.subscribers)} subs</span>
                <span className="rounded-full bg-white/10 px-3 py-1">{formatNumber(creator.monthlyViews)} monthly views</span>
                <span className="rounded-full bg-white/10 px-3 py-1">{creator.videos.length} featured videos</span>
              </div>
              <h1 className="text-4xl font-semibold leading-tight">{creator.name}</h1>
              <p className="text-base text-gray-300 max-w-3xl">{creator.domain}</p>
            </div>
          </div>
        </header>

        <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <MetricCard label="Subscribers" value={formatNumber(creator.subscribers)} />
          <MetricCard label="Monthly views" value={formatNumber(creator.monthlyViews)} />
          <MetricCard label="Region" value={creator.region} />
          <MetricCard label="Content type" value={creator.contentType} />
        </section>

        <section className="space-y-3">
          <div>
            <p className="text-xs uppercase tracking-[0.25em] text-gray-400">Risk & compliance</p>
            <p className="text-sm text-gray-400">Last 12 months of safety signals.</p>
          </div>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <MetricCard label="Brand safety score" value="92 / 100" />
            <MetricCard label="Disclosure incidents" value="0 in past 12 mo" />
            <MetricCard label="Avg. sentiment" value="+68% positive" />
            <MetricCard label="Risk band" value="Low" />
          </div>
        </section>

        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-gray-400">Audience comments & sentiment</p>
              <p className="text-sm text-gray-400">Last 30 days of comment velocity and tone.</p>
            </div>
            <span className="text-xs text-gray-300">{formatNumber(creator.commentVolume30d)} comments</span>
          </div>

          <div className="grid gap-4 lg:grid-cols-[2fr_1fr]">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-5 shadow-inner shadow-black/30 space-y-4">
              <div className="space-y-3">
                <SentimentRow label="Positive" value={creator.sentiment.positive} color="from-emerald-400/90 to-emerald-500/80" />
                <SentimentRow label="Neutral" value={creator.sentiment.neutral} color="from-slate-300/90 to-slate-400/70" />
                <SentimentRow label="Negative" value={creator.sentiment.negative} color="from-rose-400/90 to-rose-500/80" />
              </div>

              <div className="grid gap-3 sm:grid-cols-2">
                {creator.highlightedComments.map((comment) => (
                  <div key={comment} className="rounded-xl border border-white/10 bg-[#0f0f18] p-3 text-sm text-gray-200">
                    <p className="text-[11px] uppercase tracking-wide text-gray-400 mb-1">Signal comment</p>
                    <p className="leading-relaxed">“{comment}”</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-2xl border border-white/10 bg-gradient-to-b from-[#1d1524] via-[#14101a] to-[#0b0b10] p-5 shadow-lg shadow-black/40 space-y-3">
              <p className="text-[11px] uppercase tracking-wide text-gray-300">Top themes</p>
              <div className="flex flex-wrap gap-2">
                {creator.topThemes.map((theme) => (
                  <span key={theme} className="rounded-full bg-white/10 px-3 py-1 text-xs text-gray-100">
                    {theme}
                  </span>
                ))}
              </div>
              <p className="text-xs text-gray-400">
                Themes are extracted from high-engagement comments and weighted by recency to surface what the audience asks for next.
              </p>
            </div>
          </div>
        </section>

        {/* RECENT VIDEOS SECTION */}
        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-gray-400">Recent videos</p>
              <p className="text-sm text-gray-400">Sample of the creator’s recent uploads.</p>
            </div>
            <span className="text-xs text-gray-400">{creator.videos.length} videos</span>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {creator.videos.map((video) => (
              <Link
                key={video.title}
                href={video.link}
                className="group rounded-2xl border border-white/10 bg-gradient-to-b from-[#151525] via-[#11111a] to-[#0c0c12] shadow-lg shadow-black/40 overflow-hidden transition hover:-translate-y-1 hover:border-white/20"
              >
                <div className="h-40 w-full bg-gray-800 overflow-hidden">
                  <img
                    src={video.img}
                    alt={video.title}
                    className="h-full w-full object-cover transition duration-300 group-hover:scale-105"
                  />
                </div>
                <div className="p-4 space-y-2">
                  <p className="text-sm font-semibold text-white line-clamp-2">{video.title}</p>
                  <p className="text-xs text-gray-300">{video.views}</p>
                  <p className="text-[11px] text-gray-400">Tap to view source</p>
                </div>
              </Link>
            ))}
          </div>
        </section>

        <section className="rounded-2xl border border-white/10 bg-white/5 p-6 shadow-inner shadow-black/30 space-y-3">
          <h3 className="text-sm uppercase tracking-[0.25em] text-gray-400">Collaboration notes</h3>
          <p className="text-gray-200 text-sm">
            This creator demonstrates consistent disclosure, steady month-over-month growth, and strong engagement within their niche.
            Consider bundling mid-roll + community posts for best conversions.
          </p>
          <div className="flex flex-wrap gap-2 text-xs text-gray-300">
            <span className="rounded-full bg-white/10 px-3 py-1">Disclosure: clean</span>
            <span className="rounded-full bg-white/10 px-3 py-1">Formats: long + short</span>
            <span className="rounded-full bg-white/10 px-3 py-1">Requests: open</span>
          </div>
        </section>
      </div>
    </div>
  )
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-4 shadow-inner shadow-black/30">
      <p className="text-[11px] uppercase tracking-wide text-gray-400">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-white">{value}</p>
    </div>
  )
}

function SentimentRow({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-xs text-gray-300">
        <span>{label}</span>
        <span className="text-gray-100 font-semibold">{value}%</span>
      </div>
      <div className="h-2 rounded-full bg-white/10 overflow-hidden">
        <div className={`h-full bg-gradient-to-r ${color}`} style={{ width: `${Math.min(100, value)}%` }} />
      </div>
    </div>
  )
}
