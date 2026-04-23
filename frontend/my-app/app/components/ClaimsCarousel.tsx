"use client";

import { motion } from "framer-motion";
import { useEffect, useRef, useState } from "react";

// ── Types ─────────────────────────────────────────────────────────────────────

interface Claim {
  id: string;
  text: string;
  destination: string;
  cluster_size: number;
  computed_at: string | null;
  source: string;        // channel_id
  creator_name: string;
}

// ── Component ─────────────────────────────────────────────────────────────────


export default function ClaimsCarousel() {
  const carouselRef = useRef<HTMLDivElement>(null);
  const [claims, setClaims] = useState<Claim[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
  async function fetchClaims() {
    try {
      const [claimsRes, creatorsRes] = await Promise.all([
        fetch(`/api/claims/trending`),
        fetch(`/api/creators`),
      ]);

      if (!claimsRes.ok) throw new Error(`API error ${claimsRes.status}`);
      if (!creatorsRes.ok) throw new Error(`API error ${creatorsRes.status}`);

      const data = await claimsRes.json();
      const creatorsData: { channel_id: string; creator_name: string }[] = await creatorsRes.json();

      // Build lookup map
      const creatorMap: Record<string, string> = {};
      for (const c of creatorsData) {
        creatorMap[c.channel_id] = c.creator_name;
      }

      // Enrich claims with creator names
      const enriched = data.map((claim: Claim) => ({
        ...claim,
        creator_name: creatorMap[claim.source] || claim.creator_name || "Unknown creator",
      }));

      setClaims(enriched);
    } catch (err) {
      console.error("Fetch error:", err);
      setError("Could not load claims.");
    } finally {
      setLoading(false);
    }
  }
  fetchClaims();
}, []);

  // only display claims with a destination and text and only the top 10 or min(claims.length, 10 
  const filteredClaims = claims.filter(claim => claim.destination && claim.text);
  const displayedClaims = filteredClaims.slice(0, 6);

  // ── Loading skeleton ────────────────────────────────────────────────────────
  if (loading) {
    return (
      <div className="w-full overflow-x-hidden">
        <div className="flex gap-4">
          {[1, 2, 3, 4].map((n) => (
            <div
              key={n}
              className="h-44 w-72 rounded-xl bg-white/10 animate-pulse"
            />
          ))}
        </div>
      </div>
    );
  }

  // ── Error state ─────────────────────────────────────────────────────────────
  if (error) {
    return (
      <div className="w-full rounded-lg border border-red-500/40 bg-red-900/60 px-4 py-3 text-sm text-red-100">
        {error}
      </div>
    );
  }

  // ── Empty state ─────────────────────────────────────────────────────────────
  if (!claims.length) {
    return (
      <div className="w-full rounded-lg border border-dashed border-white/15 bg-white/5 px-4 py-3 text-sm text-gray-300">
        No trending claims available yet.
      </div>
    );
  }

  // ── Cards ───────────────────────────────────────────────────────────────────
  return (
    <div
      ref={carouselRef}
      className="w-full overflow-x-auto no-scrollbar pb-4 snap-x snap-mandatory"
    >
      <motion.div
        className="flex min-w-max gap-4 px-1 cursor-grab"
        drag="x"
        dragConstraints={carouselRef}
        dragElastic={0.08}
      >
        {displayedClaims.map((claim) => (
          <motion.div
            key={claim.id}
            className="snap-start w-72 h-auto rounded-2xl border border-white/10 bg-white/5 px-5 py-4 shadow-lg shadow-black/30 backdrop-blur-sm transition hover:border-white/30 hover:bg-white/10 flex flex-col gap-2"
          >
            <h3 className="text-xs font-semibold uppercase tracking-[0.15em] text-indigo-200">
              {claim.destination}
            </h3>
            <p className="mt-2 text-lg font-medium leading-snug text-gray-100">
              “{claim.text}”
            </p>
            <div className="mt-3 space-y-1 text-sm text-gray-400">
              <p className="font-medium text-gray-200">
                {claim.creator_name || "Unknown creator"}
              </p>
              <p className="text-gray-400">
                Based on {claim.cluster_size} similar claims
              </p>
              {claim.computed_at && (
                <p className="text-gray-500">
                  Updated: {new Date(claim.computed_at).toLocaleDateString()}
                </p>
              )}
            </div>
          </motion.div>
        ))}
      </motion.div>
    </div>
  );
}
