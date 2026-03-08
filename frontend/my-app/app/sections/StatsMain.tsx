import Link from "next/dist/client/link";
import StatCard from "../components/StatCard";
import { stat } from "fs";

export default function StatsMain() {
  const stats = [
    {
      title: "Active Narratives",
      value: "184",
      href: "/narratives"
    },
    {
      title: "Claims Analyzed",
      value: "12,487"
    },
    {
      title: "Active Risk Alerts",
      value: "6",
      subtitle: "Potential misinformation or high-negative sentiment spikes detected"
    }
  ]

  const topDestination = {
    name: "Kyoto",
    growth: "+42%",
    href: "/discover"
  }

  return (
    <div className="text-white">
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

        <StatCard
          title={stats[0].title}
          value={stats[0].value}
          href={stats[0].href}
        />

        <StatCard
          title={stats[1].title}
          value={stats[1].value}
        />

        <StatCard
          title={stats[2].title}
          value={stats[2].value}
          subtitle={stats[2].subtitle}
        />

      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
        <Link href={`/discover/${topDestination.name.toLowerCase()}`}>
        <div className="
          bg-gradient-to-br from-neutral-900 to-neutral-950
          border border-neutral-800
          rounded-2xl
          p-8
          hover:border-white/30 transition
          h-full
        ">
          <p className="text-sm text-neutral-400 mb-3">
            Fastest Rising Destination
          </p>

          
          <h1 className="text-5xl font-bold tracking-tight text-[#E4CAFF]">
            {topDestination.name}
          </h1>
          

          <p className="text-sm text-neutral-400 mt-4">
            {topDestination.growth} Discussion Growth
          </p>
        </div>
        </Link>

        <Link href="/creators">
          <div className="
            bg-gradient-to-br from-neutral-900 to-neutral-950
            border border-neutral-800
            rounded-2xl
            p-8
            hover:border-white/30 transition
            h-full
          ">
            <p className="text-sm text-neutral-400 mb-3">
              Creator Insights
            </p>

            <ul className="text-sm text-neutral-300 space-y-2">
              <li>Micro (0–50K): 42%</li>
              <li>Mid-tier (50K–500K): 35%</li>
              <li>Large (500K–1M): 14%</li>
              <li>Enterprise (1M+): 9%</li>
            </ul>
          </div>
        </Link>

      </div>

    </div>
  )
}

