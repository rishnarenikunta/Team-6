import Link from "next/link"
import { notFound } from "next/navigation"

type Claim = {
  text: string
  source: string
  views: string
  engagement: string
  growth: string
}

type VideoClaim = {
  title: string
  text: string
  risk: "low" | "medium" | "high"
}

type VideoDetail = {
  title: string
  channel: string
  views: string
  published: string
  claim: string
  thumb: string
  summary: string
  sentiment: "positive" | "neutral" | "negative"
  riskCallouts: string[]
  claims: VideoClaim[]
}

type NarrativeDetail = {
  slug: string
  title: string
  summary: string
  videosAnalyzed: number
  claimsCount: number
  creatorsCount: number
  sentimentScore: string
  velocity: string
  sentiment: "positive" | "neutral" | "negative"
  topCreators: string[]
  claims: Claim[]
  videos: VideoDetail[]
}

const narratives: NarrativeDetail[] = [
  {
    slug: "slow-travel-japan-countryside",
    title: "Slow travel in Japan’s countryside",
    summary:
      "Creators shift from Tokyo/Osaka highlights to rural rail loops, farm-stays, and onsen towns. Viewers want slower itineraries, food crawls, and local passes that cut transit costs.",
    videosAnalyzed: 428,
    claimsCount: 22,
    creatorsCount: 72,
    sentimentScore: "82% positive",
    velocity: "+18% week-over-week",
    sentiment: "positive",
    topCreators: ["NomadNick", "WonderWithMia", "TravelTomo", "WanderNina", "RailRiderKen", "AutumnAtlas"],
    claims: [
      { text: "Rural rail passes are cheaper than city subway passes over 5+ days.", source: "NomadNick", views: "1.2M", engagement: "11.2%", growth: "+42%" },
      { text: "You can eat in small-town izakayas for under $10 a meal.", source: "WonderWithMia", views: "842K", engagement: "9.8%", growth: "+37%" },
      { text: "Countryside onsen towns are less crowded than Kyoto but as scenic.", source: "TravelTomo", views: "620K", engagement: "8.1%", growth: "+21%" },
      { text: "Local buses + trains cover most rural loops without renting a car.", source: "WanderNina", views: "540K", engagement: "7.5%", growth: "+18%" },
    ],
    videos: [
      {
        title: "5-Day Rural Rail Loop in Kansai",
        channel: "NomadNick",
        views: "1.2M",
        published: "2 weeks ago",
        claim: "Rural passes beat city passes on cost.",
        thumb: "https://images.unsplash.com/photo-1528164344705-47542687000d?auto=format&fit=crop&w=600&q=60",
        summary: "Nick rides local lines and countryside buses to show a 5-day loop that avoids Tokyo crowds.",
        sentiment: "positive",
        riskCallouts: ["Rail pass prices vary by season", "Local buses run less frequently after 21:00"],
        claims: [
          { title: "Cheaper than subway passes", text: "Regional passes cover unlimited rides for ~$40/day.", risk: "low" },
          { title: "Walkable towns", text: "Most onsen towns are compact enough to skip car rentals.", risk: "medium" },
        ],
      },
      {
        title: "Izakaya Crawl in Small-Town Japan",
        channel: "WonderWithMia",
        views: "842K",
        published: "1 month ago",
        claim: "$10 meals outside the big cities.",
        thumb: "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=600&q=60",
        summary: "Mia compares izakaya pricing between Osaka and rural stops, highlighting budget meals.",
        sentiment: "positive",
        riskCallouts: ["Menu pricing can change with seasonal fish", "Cash-only shops common"],
        claims: [
          { title: "Budget meals", text: "You can find full meals under $10 USD in small towns.", risk: "low" },
          { title: "Cash heavy", text: "70% of shops preferred cash; cards were spotty.", risk: "medium" },
        ],
      },
      {
        title: "Onsen Towns vs Kyoto Crowds",
        channel: "TravelTomo",
        views: "620K",
        published: "3 weeks ago",
        claim: "Less-crowded onsen towns equal scenery.",
        thumb: "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=600&q=60",
        summary: "Tomo contrasts visitor density and scenery between Kyoto and smaller onsen towns.",
        sentiment: "positive",
        riskCallouts: ["Some towns close shops by 21:30", "Bath etiquette rules vary"],
        claims: [
          { title: "Lower crowds", text: "Weeknight visits had ~60% fewer tourists than Kyoto.", risk: "low" },
          { title: "Transit tradeoff", text: "Fewer late-night buses after 22:00; plan returns earlier.", risk: "medium" },
        ],
      },
      {
        title: "No-Car Countryside Itinerary",
        channel: "WanderNina",
        views: "540K",
        published: "10 days ago",
        claim: "Loop by bus + train without renting a car.",
        thumb: "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=600&q=60",
        summary: "Nina proves you can do the Kansai countryside loop with buses and JR lines only.",
        sentiment: "positive",
        riskCallouts: ["Winter weather may cancel rural buses", "Accessibility varies by station"],
        claims: [
          { title: "No car needed", text: "Loop completed with public transit only.", risk: "low" },
          { title: "Check bus timings", text: "Gaps of 60–90 mins on some rural routes.", risk: "medium" },
        ],
      },
    ],
  },
  {
    slug: "mediterranean-shoulder-season-hack",
    title: "Mediterranean shoulder-season hack",
    summary:
      "Mid-October to mid-November trips to coastal Europe are framed as crowd-free and cheaper while keeping warm weather. Creators recommend flexible ferries and bundle flights.",
    videosAnalyzed: 312,
    claimsCount: 18,
    creatorsCount: 46,
    sentimentScore: "76% positive",
    velocity: "+11% week-over-week",
    sentiment: "positive",
    topCreators: ["PocketPorto", "EuroNomad", "SailWithSami", "BudgetBalearic", "CoastlineKate"],
    claims: [
      { text: "Sea temps in October stay swimmable from Lisbon to Malta.", source: "SailWithSami", views: "410K", engagement: "6.9%", growth: "+12%" },
      { text: "Bundle ferry + train passes cut island-hop costs by ~20%.", source: "PocketPorto", views: "355K", engagement: "7.2%", growth: "+15%" },
      { text: "Short-term rentals drop 15-25% after October 10th.", source: "EuroNomad", views: "502K", engagement: "8.4%", growth: "+19%" },
    ],
    videos: [
      {
        title: "Shoulder Season in Algarve",
        channel: "PocketPorto",
        views: "355K",
        published: "3 weeks ago",
        claim: "Bundle ferry+train to save 20%.",
        thumb: "https://images.unsplash.com/photo-1505761671935-60b3a7427bad?auto=format&fit=crop&w=600&q=60",
        summary: "Porto shows how combining ferries and regional trains trims costs in October.",
        sentiment: "positive",
        riskCallouts: ["Weather can swing rainy", "Some ferries reduce frequency mid-week"],
        claims: [
          { title: "20% savings", text: "Mixing ferries and trains lowered island-hop costs by ~20%.", risk: "low" },
          { title: "Flexible days", text: "Savings require shifting legs to mid-week sailings.", risk: "medium" },
        ],
      },
      {
        title: "Lisbon to Malta on a Budget",
        channel: "EuroNomad",
        views: "502K",
        published: "1 month ago",
        claim: "Rentals drop 15-25% after Oct 10.",
        thumb: "https://images.unsplash.com/photo-1505764706515-aa95265c5abc?auto=format&fit=crop&w=600&q=60",
        summary: "Breakdown of airfare bundles and short-stay pricing once peak season ends.",
        sentiment: "positive",
        riskCallouts: ["Prices rebound around local holidays", "Fewer direct flights after November"],
        claims: [
          { title: "Rental drop", text: "Listings in Lisbon and Malta fell 15–25% after Oct 10.", risk: "low" },
          { title: "Flight caveat", text: "Direct flights thin out; connections may add 3–5 hrs.", risk: "medium" },
        ],
      },
      {
        title: "Sea Temps in October",
        channel: "SailWithSami",
        views: "410K",
        published: "2 weeks ago",
        claim: "Still swimmable mid-October.",
        thumb: "https://images.unsplash.com/photo-1505761671935-60b3a7427bad?auto=format&fit=crop&w=600&q=60",
        summary: "Sami charts water temps across the Med and shows where swimming stays comfortable.",
        sentiment: "positive",
        riskCallouts: ["Weather volatility in late October", "Jellyfish spikes after storms"],
        claims: [
          { title: "Warm water pockets", text: "Sea temps stayed 20–23°C through late October.", risk: "low" },
          { title: "Storm caveat", text: "Early storms briefly cooled bays by 1–2°C.", risk: "medium" },
        ],
      },
    ],
  },
  {
    slug: "mexico-city-safety-discourse",
    title: "Mexico City safety discourse",
    summary:
      "Narrative focuses on night transit, neighborhood choices, and theft anecdotes. Comments split between alarmist shorts and data-based walk-throughs; engagement stays high.",
    videosAnalyzed: 379,
    claimsCount: 25,
    creatorsCount: 58,
    sentimentScore: "64% positive / neutral skew",
    velocity: "+6% week-over-week",
    sentiment: "neutral",
    topCreators: ["NomadNora", "ChilangoCheck", "DataDriftCDMX", "LateNightLeo", "MetroMaven"],
    claims: [
      { text: "Ride-hail costs ~$5 USD cross-city after 11pm vs. $2 metro.", source: "ChilangoCheck", views: "288K", engagement: "6.1%", growth: "+9%" },
      { text: "Pickpocketing most common on Line 3 and 5 during rush hour.", source: "DataDriftCDMX", views: "331K", engagement: "7.8%", growth: "+14%" },
      { text: "Neighborhood split: Roma/Condesa safer but pricier; Juarez rising.", source: "NomadNora", views: "476K", engagement: "8.6%", growth: "+17%" },
    ],
    videos: [
      {
        title: "CDMX Metro After Dark",
        channel: "ChilangoCheck",
        views: "288K",
        published: "5 days ago",
        claim: "$5 ride-hail vs $2 metro at night.",
        thumb: "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=600&q=60",
        summary: "Nighttime metro vs ride-hail comparison with cost and safety anecdotes.",
        sentiment: "neutral",
        riskCallouts: ["Crowding spikes on Line 3/5", "Ride-hail surge after concerts"],
        claims: [
          { title: "Ride-hail cost", text: "Cross-city rides average ~$5 USD after 11pm.", risk: "medium" },
          { title: "Metro tradeoff", text: "Cheaper at $2 but higher pickpocket risk on Line 3/5.", risk: "high" },
        ],
      },
      {
        title: "Where Pickpockets Strike",
        channel: "DataDriftCDMX",
        views: "331K",
        published: "2 weeks ago",
        claim: "Line 3 & 5 worst at rush hour.",
        thumb: "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=600&q=60",
        summary: "Data-driven look at incident heatmaps across metro lines.",
        sentiment: "neutral",
        riskCallouts: ["Data lags by 2–3 weeks", "Police presence varies nightly"],
        claims: [
          { title: "Hot lines", text: "Lines 3 and 5 log most reports 7–9am and 6–9pm.", risk: "high" },
          { title: "Safer windows", text: "Midday rides see far fewer incidents.", risk: "medium" },
        ],
      },
      {
        title: "Choosing a CDMX Neighborhood",
        channel: "NomadNora",
        views: "476K",
        published: "1 month ago",
        claim: "Roma/Condesa safer; Juarez rising.",
        thumb: "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=600&q=60",
        summary: "Nora compares three central neighborhoods for visitors with night transit tips.",
        sentiment: "neutral",
        riskCallouts: ["Short-term rental rules changing", "Safety perceptions vary block-to-block"],
        claims: [
          { title: "Area split", text: "Roma/Condesa favored for safety but pricier.", risk: "medium" },
          { title: "Juarez emerging", text: "Cheaper stays but mixed late-night reviews.", risk: "medium" },
        ],
      },
    ],
  },
  {
    slug: "balkan-road-trip-loop",
    title: "Balkan road-trip loop",
    summary:
      "Vanlife and road-trip channels highlight Bosnia, Montenegro, and Albania for cheap ferries, castle towns, and lakeside campsites. Viewers ask for rental tips and border wait times.",
    videosAnalyzed: 241,
    claimsCount: 16,
    creatorsCount: 33,
    sentimentScore: "79% positive",
    velocity: "+14% week-over-week",
    sentiment: "positive",
    topCreators: ["VanVidaLena", "RoadsAndRila", "NomadNorthStar", "BalkanBreeze", "CampWithKai"],
    claims: [
      { text: "Cross-border car rentals cost ~€10/day more; pick up/drop in same country to save.", source: "VanVidaLena", views: "189K", engagement: "6.4%", growth: "+12%" },
      { text: "Kotor to Ohrid loop is doable in 6 days with two ferries.", source: "RoadsAndRila", views: "143K", engagement: "5.9%", growth: "+10%" },
      { text: "Wild camping tolerated outside national parks; check local bylaws.", source: "NomadNorthStar", views: "121K", engagement: "5.5%", growth: "+9%" },
    ],
    videos: [
      {
        title: "6-Day Kotor to Ohrid Loop",
        channel: "RoadsAndRila",
        views: "143K",
        published: "2 weeks ago",
        claim: "Loop doable in 6 days with two ferries.",
        thumb: "https://images.unsplash.com/photo-1505764706515-aa95265c5abc?auto=format&fit=crop&w=600&q=60",
        summary: "Route, ferries, and toll costs for a 6-day Balkan loop without rushing.",
        sentiment: "positive",
        riskCallouts: ["Border waits vary by hour", "Ferry schedules can slip in storms"],
        claims: [
          { title: "Two ferries only", text: "Managed the loop with two short ferry legs.", risk: "low" },
          { title: "Border timing", text: "Cross before 10am to avoid queues.", risk: "medium" },
        ],
      },
      {
        title: "Vanlife Costs in the Balkans",
        channel: "VanVidaLena",
        views: "189K",
        published: "1 month ago",
        claim: "Cross-border rentals add €10/day.",
        thumb: "https://images.unsplash.com/photo-1505761671935-60b3a7427bad?auto=format&fit=crop&w=600&q=60",
        summary: "Lena breaks down rental surcharges, fuel, and camping fees for vans.",
        sentiment: "positive",
        riskCallouts: ["Insurance rules change by country", "Cash-only tolls in rural areas"],
        claims: [
          { title: "Rental surcharge", text: "Cross-border van rental added ~€10/day.", risk: "medium" },
          { title: "Fuel variability", text: "Diesel prices swing 8–12% between borders.", risk: "medium" },
        ],
      },
      {
        title: "Wild Camping Rules Explained",
        channel: "NomadNorthStar",
        views: "121K",
        published: "3 weeks ago",
        claim: "Tolerated outside national parks.",
        thumb: "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=600&q=60",
        summary: "Covers legality and etiquette for wild camping across the Balkans.",
        sentiment: "neutral",
        riskCallouts: ["Local bylaws can differ by municipality", "Seasonal fire bans common"],
        claims: [
          { title: "Outside parks OK", text: "Wild camping generally tolerated outside parks.", risk: "medium" },
          { title: "Fire bans", text: "Summer fire bans limit cooking fuel options.", risk: "high" },
        ],
      },
    ],
  },
  {
    slug: "seoul-night-markets-kpop",
    title: "Seoul night markets & K-pop pilgrimages",
    summary:
      "Short-form hauls and concert vlogs dominate; creators map market stalls, merch streets, and late-night transit. Audience wants exact shop locations and after-midnight options.",
    videosAnalyzed: 512,
    claimsCount: 27,
    creatorsCount: 97,
    sentimentScore: "88% positive",
    velocity: "+21% week-over-week",
    sentiment: "positive",
    topCreators: ["SeoulSnacks", "KWaveKait", "TransitTae", "MidnightMandu", "MerchMapMae"],
    claims: [
      { text: "Myeongdong street food peaks 9–11pm; lines drop after 11:15pm.", source: "SeoulSnacks", views: "710K", engagement: "10.2%", growth: "+24%" },
      { text: "Hongdae merch streets stay open past midnight on weekends.", source: "KWaveKait", views: "654K", engagement: "9.4%", growth: "+20%" },
      { text: "Airport line and night buses cover most markets until ~1am.", source: "TransitTae", views: "402K", engagement: "7.1%", growth: "+15%" },
    ],
    videos: [
      {
        title: "Hongdae Merch Streets at Midnight",
        channel: "KWaveKait",
        views: "654K",
        published: "1 week ago",
        claim: "Merch streets stay open past midnight.",
        thumb: "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=600&q=60",
        summary: "Walkthrough of Hongdae merch alleys with timestamps and late-night safety notes.",
        sentiment: "positive",
        riskCallouts: ["Crowds dense till midnight", "Card-only in some pop-up shops"],
        claims: [
          { title: "Open late", text: "Most shops stayed open past 00:15 on weekends.", risk: "low" },
          { title: "Cash vs card", text: "Some pop-ups were card-only despite signage.", risk: "medium" },
        ],
      },
      {
        title: "Night Bus vs Subway in Seoul",
        channel: "TransitTae",
        views: "402K",
        published: "2 weeks ago",
        claim: "Airport line + night buses cover markets till ~1am.",
        thumb: "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=600&q=60",
        summary: "Transit options after midnight including night buses, subway last trains, and safety.",
        sentiment: "positive",
        riskCallouts: ["Schedules shift on holidays", "Late taxis can surge near concerts"],
        claims: [
          { title: "1am coverage", text: "Night buses run at 20–30 min intervals until ~1am.", risk: "low" },
          { title: "Last trains", text: "Airport line last departures vary by station; check before 00:10.", risk: "medium" },
        ],
      },
      {
        title: "Street Food Peak Hours",
        channel: "SeoulSnacks",
        views: "710K",
        published: "5 days ago",
        claim: "Myeongdong lines drop after 11:15pm.",
        thumb: "https://images.unsplash.com/photo-1505761671935-60b3a7427bad?auto=format&fit=crop&w=600&q=60",
        summary: "Food stall walkthrough showing when lines fade and what sells out first.",
        sentiment: "positive",
        riskCallouts: ["Oil reuse concerns at some stalls", "Popular items sell out by 23:00"],
        claims: [
          { title: "Line timing", text: "Lines eased after 23:15 on weekdays.", risk: "low" },
          { title: "Sell-outs", text: "Top items (cheese sticks) sold out around 23:00.", risk: "medium" },
        ],
      },
    ],
  },
  {
    slug: "us-national-parks-winter-playbook",
    title: "US national parks winter playbook",
    summary:
      "Creators pivot to winter hiking, astro photography, and crowd-free itineraries in Yellowstone, Zion, and Yosemite. Emphasis on gear, closures, and sunrise/sunset timing.",
    videosAnalyzed: 198,
    claimsCount: 14,
    creatorsCount: 29,
    sentimentScore: "73% positive",
    velocity: "+9% week-over-week",
    sentiment: "positive",
    topCreators: ["TrailTessa", "FrostyFootprints", "PeakPixel", "SummitSage", "NationalNora"],
    claims: [
      { text: "Zion shuttle is off in winter; personal cars allowed most days.", source: "TrailTessa", views: "211K", engagement: "6.7%", growth: "+11%" },
      { text: "Yellowstone thermal basins are open via snowcoach; book 4+ weeks early.", source: "FrostyFootprints", views: "167K", engagement: "6.2%", growth: "+10%" },
      { text: "Yosemite sunrise at Tunnel View has <10 cars in January weekdays.", source: "PeakPixel", views: "139K", engagement: "5.8%", growth: "+9%" },
    ],
    videos: [
      {
        title: "Winter in Zion: Shuttle Off",
        channel: "TrailTessa",
        views: "211K",
        published: "3 weeks ago",
        claim: "Personal cars allowed most days in winter.",
        thumb: "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=600&q=60",
        summary: "What changes when Zion shuttle pauses and how to time parking.",
        sentiment: "positive",
        riskCallouts: ["Road closures after snow", "Parking lots fill by 9am on holidays"],
        claims: [
          { title: "Drive yourself", text: "Winter allows personal cars through the canyon.", risk: "low" },
          { title: "Parking caveat", text: "Arrive before 9am on holiday weekends.", risk: "medium" },
        ],
      },
      {
        title: "Booking Yellowstone Snowcoach",
        channel: "FrostyFootprints",
        views: "167K",
        published: "1 month ago",
        claim: "Book snowcoach 4+ weeks early.",
        thumb: "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=600&q=60",
        summary: "How to secure snowcoach seats and what basins stay open.",
        sentiment: "positive",
        riskCallouts: ["Limited seats during storms", "Thermal areas can close same-day"],
        claims: [
          { title: "Book early", text: "Snowcoach tours sold out 4–6 weeks ahead.", risk: "medium" },
          { title: "Weather swings", text: "Storms can cancel routes with short notice.", risk: "high" },
        ],
      },
      {
        title: "Yosemite Sunrise in January",
        channel: "PeakPixel",
        views: "139K",
        published: "10 days ago",
        claim: "Tunnel View has <10 cars on weekdays.",
        thumb: "https://images.unsplash.com/photo-1505764706515-aa95265c5abc?auto=format&fit=crop&w=600&q=60",
        summary: "Crowd levels, icy roads, and photo tips for sunrise spots.",
        sentiment: "positive",
        riskCallouts: ["Chains often required", "Trail closures change weekly"],
        claims: [
          { title: "Low crowds", text: "Weekday sunrise had under 10 cars present.", risk: "low" },
          { title: "Chains needed", text: "Carry tire chains—rangers check during snow.", risk: "medium" },
        ],
      },
    ],
  },
]


const sentimentChip = (sentiment: NarrativeDetail["sentiment"]) => {
  if (sentiment === "positive") return "text-emerald-300 bg-emerald-400/10"
  if (sentiment === "negative") return "text-rose-300 bg-rose-400/10"
  return "text-amber-200 bg-amber-400/10"
}

type Params = { params: Promise<{ slug: string }> }

export default async function NarrativeDetailPage({ params }: Params) {
  const { slug } = await params
  const narrative = narratives.find((n) => n.slug === slug)
  if (!narrative) return notFound()

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0b0b10] via-[#0f1018] to-[#0b0b10] text-white">
      <div className="max-w-6xl mx-auto px-6 pb-16 pt-12 space-y-10">
        <div className="flex items-center gap-4 text-sm text-gray-400">
          <Link href="/narratives" className="underline underline-offset-4 decoration-white/30 hover:text-white">
            Narratives
          </Link>
          <span>›</span>
          <span className="text-gray-200">{narrative.title}</span>
        </div>

        <header className="space-y-4">
          <div className="flex flex-wrap items-center gap-3">
            <span className={`rounded-full px-3 py-1 text-xs ${sentimentChip(narrative.sentiment)}`}>
              {narrative.sentiment}
            </span>
            <span className="rounded-full bg-white/10 text-gray-200 px-3 py-1 text-xs border border-white/10">
              {narrative.velocity}
            </span>
            <span className="rounded-full bg-white/10 text-gray-200 px-3 py-1 text-xs border border-white/10">
              {narrative.creatorsCount} creators
            </span>
            <span className="rounded-full bg-white/10 text-gray-200 px-3 py-1 text-xs border border-white/10">
              {narrative.videosAnalyzed} videos analyzed
            </span>
          </div>
          <h3 className="text-sm uppercase tracking-[0.25em] text-gray-400">Narrative overview</h3>
          <h1 className="text-4xl font-semibold leading-tight">{narrative.title}</h1>
          <p className="text-base text-gray-300 max-w-3xl">{narrative.summary}</p>
        </header>

        <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <MetricCard label="Videos analyzed" value={narrative.videosAnalyzed.toLocaleString()} />
          <MetricCard label="Active claims" value={narrative.claimsCount.toString()} />
          <MetricCard label="Active creators" value={narrative.creatorsCount.toString()} />
          <MetricCard label="Sentiment" value={narrative.sentimentScore} />
        </section>

        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-gray-400">Top creators</p>
              <p className="text-sm text-gray-400">Primary channels informing this narrative.</p>
            </div>
            <span className="text-xs text-gray-400">{narrative.topCreators.length} highlighted</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {narrative.topCreators.map((creator) => (
              <span key={creator} className="rounded-full bg-white/5 border border-white/10 px-3 py-2 text-xs text-gray-200">
                {creator}
              </span>
            ))}
          </div>
        </section>

        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-gray-400">Claims carousel</p>
              <p className="text-sm text-gray-400">High-signal claims clustered for this narrative.</p>
            </div>
            <span className="text-xs text-gray-400">{narrative.claims.length} shown</span>
          </div>

          <div className="flex gap-4 overflow-x-auto pb-2">
            {narrative.claims.map((claim, idx) => (
              <div
                key={idx}
                className="min-w-[240px] max-w-[260px] rounded-2xl border border-white/10 bg-gradient-to-b from-[#151525] via-[#11111a] to-[#0c0c12] p-4 shadow-lg shadow-black/40"
              >
                <p className="text-sm text-gray-200 mb-3">“{claim.text}”</p>
                <div className="text-xs text-gray-400 space-y-1">
                  <p><span className="text-gray-500">Source:</span> {claim.source}</p>
                  <p><span className="text-gray-500">Views:</span> {claim.views}</p>
                  <p><span className="text-gray-500">Engagement:</span> {claim.engagement}</p>
                  <p><span className="text-gray-500">Growth:</span> {claim.growth}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="space-y-3">
            <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-gray-400">Related Videos</p>
              <p className="text-sm text-gray-400">Each video contributed a claim; together they form this narrative.</p>
            </div>
            <span className="text-xs text-gray-400">{narrative.videos.length} shown</span>
          </div>
          <div className="flex gap-4 overflow-x-auto pb-2">
            {narrative.videos.map((video, idx) => (
              <div
                key={idx}
                className="min-w-[260px] max-w-[280px] rounded-2xl border border-white/10 bg-gradient-to-b from-[#151525] via-[#11111a] to-[#0c0c12] shadow-lg shadow-black/40 overflow-hidden"
              >
                <div className="h-40 w-full bg-gray-800 overflow-hidden">
                  <img src={video.thumb} alt={video.title} className="h-full w-full object-cover" />
                </div>
                <div className="p-4 space-y-2">
                  <p className="text-sm font-semibold text-white line-clamp-2">{video.title}</p>
                  <p className="text-xs text-gray-300">{video.channel}</p>
                  <p className="text-[11px] text-gray-400">{video.views} • {video.published}</p>
                  <p className="text-xs text-blue-200 line-clamp-2">Claim: {video.claim}</p>
                </div>
              </div>
            ))}
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
