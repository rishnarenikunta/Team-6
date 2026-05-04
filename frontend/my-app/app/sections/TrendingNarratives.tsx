"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface RawTrendingNarrative {
  id: string;
  text: string;
  destination: string;
  cluster_size: number;
  computed_at: string | null;
  source: string;
}

interface Creator {
  channel_id: string;
  creator_name: string;
}

interface Narrative extends RawTrendingNarrative {
  creator_name: string;
}

export default function TrendingNarratives() {
  const [narratives, setNarratives] = useState<Narrative[]>([]);
  const [selected, setSelected] = useState<Narrative | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function fetchNarratives() {
      try {
        const [narrativesRes, creatorsRes] = await Promise.all([
          fetch("/api/narratives/trending"),
          fetch("/api/creators"),
        ]);

        if (!narrativesRes.ok) throw new Error(`API error ${narrativesRes.status}`);
        if (!creatorsRes.ok) throw new Error(`API error ${creatorsRes.status}`);

        const raw: RawTrendingNarrative[] = await narrativesRes.json();
        const creators: Creator[] = await creatorsRes.json();

        const creatorMap: Record<string, string> = {};
        for (const c of creators) {
          creatorMap[c.channel_id] = c.creator_name;
        }

        const enriched: Narrative[] = raw.map((item) => ({
          ...item,
          creator_name:
            creatorMap[item.source] ??
            creatorMap[item.destination] ??
            "—",
        }));

        setNarratives(enriched);
        setSelected(enriched[0] ?? null);
      } catch (err) {
        console.error("Failed to fetch narratives:", err);
      } finally {
        setIsLoading(false);
      }
    }

    fetchNarratives();
  }, []);

  const filteredNarratives = narratives.filter(
    (narrative) => narrative.destination && narrative.text
  );
  
  const uniqueNarrativesMap = new Map<string, Narrative>();
  filteredNarratives.forEach((narrative) => {
    if (!uniqueNarrativesMap.has(narrative.text)) {
      uniqueNarrativesMap.set(narrative.text, narrative);
    }
  });
  
  const uniqueNarratives = Array.from(uniqueNarrativesMap.values());
  const displayedNarratives = uniqueNarratives.slice(0, 6);

  function secondaryLabel(n: Narrative): string {
    return n.creator_name !== "—" ? n.creator_name : n.destination || "—";
  }

  if (isLoading) {
    return (
      <div className="w-full mt-10 mb-24 animate-pulse">
        <div className="h-8 bg-neutral-800 rounded w-64 mb-2"></div>
        <div className="h-4 bg-neutral-800 rounded w-96 mb-8"></div>
        <div className="flex gap-8">
          <div className="w-1/2 space-y-4">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-24 bg-neutral-800 rounded-2xl w-full"></div>
            ))}
          </div>
          <div className="w-1/2 h-80 bg-neutral-800 rounded-3xl"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full mt-10 mb-24">
      {/* Header Section */}
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-white tracking-tight mb-2 flex items-center gap-3">
          Trending Narratives
          <span className="flex h-3 w-3 relative">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-purple-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-purple-500"></span>
          </span>
        </h2>
        <p className="text-neutral-400 border-b border-neutral-800 pb-6">
          Narratives represent AI-clustered story themes emerging across travel videos.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-start">
        {/* LEFT SIDE LIST (CARDS) */}
        <div className="lg:col-span-5 flex flex-col gap-4">
          {displayedNarratives.map((item) => {
            const isActive = selected?.id === item.id;
            
            return (
              <motion.button
                key={item.id}
                onClick={() => setSelected(item)}
                className={`w-full text-left p-5 rounded-2xl transition-all duration-300 relative overflow-hidden group border shadow-sm ${
                  isActive 
                    ? "bg-purple-500/10 border-purple-500/40 shadow-[0_0_15px_rgba(168,85,247,0.1)]" 
                    : "bg-neutral-900/50 border-neutral-800/80 hover:bg-neutral-800 hover:border-neutral-700 hover:shadow-md"
                }`}
                whileHover={!isActive ? { y: -2 } : {}}
              >
                {/* Active left border indicator */}
                {isActive && (
                  <motion.div 
                    layoutId="active-indicator"
                    className="absolute left-0 top-0 bottom-0 w-1 bg-purple-500" 
                  />
                )}
                
                {/* Card Top Metadata */}
                <div className="flex items-center gap-2 mb-2">
                   <div className={`w-1.5 h-1.5 rounded-full ${isActive ? 'bg-purple-400 shadow-[0_0_5px_rgba(168,85,247,0.8)]' : 'bg-neutral-600'}`}></div>
                   <span className={`text-xs font-semibold uppercase tracking-wider ${isActive ? 'text-purple-300' : 'text-neutral-500'}`}>
                     {secondaryLabel(item)}
                   </span>
                </div>

                {/* Card Main Text */}
                <p className={`text-sm md:text-base font-medium leading-relaxed line-clamp-2 ${isActive ? 'text-white' : 'text-neutral-300'}`}>
                  "{item.text}"
                </p>
              </motion.button>
            );
          })}
        </div>

        {/* RIGHT SIDE DETAILS CARD */}
        <div className="lg:col-span-7 sticky top-24">
          <AnimatePresence mode="wait">
            {selected && (
              <motion.div
                key={selected.id}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3, ease: "easeOut" }}
                className="relative bg-neutral-900 border border-neutral-800 rounded-3xl p-8 shadow-2xl overflow-hidden group"
              >
                {/* Decorative glowing background blob */}
                <div className="absolute -top-24 -right-24 w-64 h-64 bg-purple-600/20 rounded-full blur-[80px] pointer-events-none group-hover:bg-purple-600/30 transition-all duration-700"></div>

                <div className="relative z-10">
                  {/* Quote Icon */}
                  <svg className="w-8 h-8 text-purple-500 mb-4 opacity-50" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M14.017 21v-7.391c0-5.704 3.731-9.57 8.983-10.609l.995 2.151c-2.432.917-3.995 3.638-3.995 5.849h4v10h-9.983zm-14.017 0v-7.391c0-5.704 3.748-9.57 9-10.609l.996 2.151c-2.433.917-3.996 3.638-3.996 5.849h3.983v10h-9.983z" />
                  </svg>

                  <h3 className="text-2xl sm:text-3xl font-medium text-white mb-6 leading-tight">
                    "{selected.text}"
                  </h3>

                  <div className="inline-flex items-center gap-2 bg-neutral-800 text-purple-300 px-4 py-2 rounded-full text-sm font-medium mb-8">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    {secondaryLabel(selected)}
                  </div>

                  {/* Stats Grid */}
                  <div className="grid grid-cols-2 sm:grid-cols-3 gap-6 pt-6 border-t border-neutral-800">
                    <div className="flex flex-col">
                      <span className="text-3xl font-bold text-white tracking-tight">
                        {selected.cluster_size}
                      </span>
                      <span className="text-xs font-medium text-neutral-500 uppercase tracking-wider mt-1">
                        Similar Videos
                      </span>
                    </div>

                    <div className="flex flex-col">
                      <span className="text-xl font-bold text-white tracking-tight truncate pb-1">
                        {selected.creator_name !== "—"
                          ? selected.creator_name
                          : selected.destination}
                      </span>
                      <span className="text-xs font-medium text-neutral-500 uppercase tracking-wider mt-1">
                        {selected.creator_name !== "—" ? "Top Creator" : "Destination"}
                      </span>
                    </div>

                    <div className="flex flex-col">
                      <span className="text-xl font-bold text-white tracking-tight">
                        {selected.computed_at
                          ? new Date(selected.computed_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
                          : "—"}
                      </span>
                      <span className="text-xs font-medium text-neutral-500 uppercase tracking-wider mt-1">
                        Last Updated
                      </span>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}