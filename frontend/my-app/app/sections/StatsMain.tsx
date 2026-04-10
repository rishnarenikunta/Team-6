"use client"

import Link from "next/link";
import { useEffect, useState } from "react";
import StatCard from "../components/StatCard";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export interface CreatorTierBreakdown {
  count: number;
  pct: number;
}

export interface CreatorInsights {
  total: number;
  tiers: {
    micro: CreatorTierBreakdown;
    mid_tier: CreatorTierBreakdown;
    large: CreatorTierBreakdown;
    enterprise: CreatorTierBreakdown;
  };
}

export interface TopDestination {
  name: string;
  growth: number;
}

export interface StatsResponse {
  top_destination: TopDestination;
  active_narratives: number;
  total_claims: number;
  trending_creators: number;
  creator_insights: CreatorInsights;
}

export default function StatsMain() {
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function fetchStats() {
      try {
        setError(null);
        const res = await fetch(`${API_BASE}/api/stats/main`);
        if (!res.ok) throw new Error(`API ${res.status}`);
        const data: StatsResponse = await res.json();
        if (!cancelled) setStats(data);
      } catch (err) {
        if (!cancelled) setError("Failed to load stats");
        console.error("Stats fetch failed:", err);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    fetchStats();
    return () => {
      cancelled = true;
    };
  }, []);

  const cards = [
    {
      title: "Active Narratives",
      value: stats?.active_narratives ?? "–",
      href: "/narratives",
    },
    {
      title: "Claims Analyzed",
      value: stats?.total_claims ?? "–",
    },
    {
      title: "Trending Creators",
      value: stats?.trending_creators ?? "–",
    },
  ];

  const topDestination = stats?.top_destination ?? { name: "—", growth: 0 };
  const tiers = stats?.creator_insights.tiers;

  if (loading) {
    return (
      <div className="text-white">
        <p className="text-sm text-gray-400">Loading stats…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-white">
        <p className="text-sm text-red-300">{error}</p>
      </div>
    );
  }

  return (
    <div className="text-white">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {cards.map((card) => (
          <StatCard
            key={card.title}
            title={card.title}
            value={card.value}
            href={card.href}
          />
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
        <Link href={`/discover/${topDestination.name.toLowerCase()}`}>
          <div
            className="
            bg-gradient-to-br from-neutral-900 to-neutral-950
            border border-neutral-800
            rounded-2xl
            p-8
            hover:border-white/30 transition
            h-full
          "
          >
            <p className="text-sm text-neutral-400 mb-3">Fastest Rising Destination</p>
            <h1 className="text-5xl font-bold tracking-tight text-[#E4CAFF]">
              {topDestination.name}
            </h1>
            <p className="text-sm text-neutral-400 mt-4">
              +{topDestination.growth}% Discussion Growth
            </p>
          </div>
        </Link>

        <Link href="/creators">
          <div
            className="
              bg-gradient-to-br from-neutral-900 to-neutral-950
              border border-neutral-800
              rounded-2xl
              p-8
              hover:border-white/30 transition
              h-full
            "
          >
            <p className="text-sm text-neutral-400 mb-3">Creator Insights</p>
            <ul className="text-sm text-neutral-300 space-y-2">
              <li>Micro (0–50K): {tiers?.micro.pct ?? "–"}% ({tiers?.micro.count ?? "–"})</li>
              <li>Mid-tier (50K–500K): {tiers?.mid_tier.pct ?? "–"}% ({tiers?.mid_tier.count ?? "–"})</li>
              <li>Large (500K–1M): {tiers?.large.pct ?? "–"}% ({tiers?.large.count ?? "–"})</li>
              <li>Enterprise (1M+): {tiers?.enterprise.pct ?? "–"}% ({tiers?.enterprise.count ?? "–"})</li>
            </ul>
          </div>
        </Link>
      </div>
    </div>
  );
}
