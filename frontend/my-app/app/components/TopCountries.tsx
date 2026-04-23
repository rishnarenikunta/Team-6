"use client";

import Link from "next/link";
import { useEffect, useState } from "react";


interface Destination {
  name: string;
  narrative_count: number;
  claim_count: number;
  share_pct: number;
}

const TopCountries = () => {
  const [destinations, setDestinations] = useState<Destination[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchDestinations() {
      try {
        const res = await fetch(`/api/destinations/top`);
        if (!res.ok) throw new Error(`API ${res.status}`);
        const data: Destination[] = await res.json();
        setDestinations(data);
      } catch (err) {
        console.error("Failed to fetch top destinations:", err);
        setError("Could not load destinations.");
      } finally {
        setLoading(false);
      }
    }
    fetchDestinations();
  }, []);

  if (loading) {
    return (
      <div className="w-full mt-10">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((n) => (
            <div key={n} className="h-44 rounded-2xl bg-white/10 animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full mt-10 rounded-lg border border-red-500/40 bg-red-900/60 px-4 py-3 text-sm text-red-100">
        {error}
      </div>
    );
  }

  return (
    <div className="w-full mt-10 h-fit">
      <h2 className="text-2xl font-semibold text-white tracking-tight mb-2">
        Trending Countries
      </h2>
      <p className="text-sm text-neutral-400 border-b border-neutral-800 pb-4 mb-4">
        Trending countries represent top travel destinations gaining momentum across creator content and audience engagement.
      </p>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {destinations.map((dest) => (
          <Link
            key={dest.name}
            href={`/discover/${encodeURIComponent(dest.name)}`}
            className="group relative overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-b from-[#1c1420] via-[#140f17] to-[#0c0c12] p-5 transition hover:-translate-y-1 hover:border-white/25 hover:shadow-2xl hover:shadow-black/50"
          >
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xl font-semibold group-hover:text-white">{dest.name}</h3>
                <p className="text-sm text-gray-400">{dest.share_pct}% of narratives</p>
              </div>
              <span className="rounded-full bg-purple-500/15 px-3 py-1 text-xs text-purple-300">
                {dest.claim_count} claims
              </span>
            </div>

            <p className="mt-3 text-sm text-purple-300">
              {dest.narrative_count} narratives tracked
            </p>

            <div className="mt-6 flex items-center justify-between text-xs text-gray-400">
              <span className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-emerald-400 shadow-[0_0_0_6px_rgba(52,211,153,0.08)]" />
                Active destination
              </span>
              <span className="font-medium text-purple-200 underline underline-offset-4 decoration-blue-200/40 transition group-hover:text-white">
                Open dashboard
              </span>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
};

export default TopCountries;
