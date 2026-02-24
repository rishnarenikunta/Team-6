import StatCard from "../components/StatCard";

export default function StatsMain() {
  return (
    <div className="text-white p-8">
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

        <StatCard
          title="Active Narratives"
          value="184"
        />

        <StatCard
          title="Claims Analyzed"
          value="12,487"
        />

        <StatCard
          title="Active Risk Alerts"
          value="6"
          subtitle="Potential misinformation or high-negative sentiment spikes detected"
        />

      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">

        <div className="
          bg-gradient-to-br from-neutral-900 to-neutral-950
          border border-neutral-800
          rounded-2xl
          p-8
        ">
          <p className="text-sm text-neutral-400 mb-3">
            Fastest Rising Destination
          </p>

          <h1 className="text-5xl font-bold tracking-tight text-[#E4CAFF]">
            Kyoto, <br /> Japan
          </h1>

          <p className="text-sm text-neutral-400 mt-4">
            +42% Discussion Growth
          </p>
        </div>

        <div className="
          bg-gradient-to-br from-neutral-900 to-neutral-950
          border border-neutral-800
          rounded-2xl
          p-8
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

      </div>

    </div>
  )
}

