// app/sections/TrendingNarratives.tsx
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

        console.log("Raw trending narratives sample:", raw[0]);
        console.log("Creators sample:", creators[0]);

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
        console.log("Number of trending topics:", enriched.length);
      } catch (err) {
        console.error("Failed to fetch narratives:", err);
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

  return (
    <div className="w-full mt-10 h-fit mb-50">
      <h2 className="text-2xl font-semibold text-white tracking-tight mb-2">
        Trending Narratives
      </h2>
      <p className="text-sm text-neutral-400 border-b border-neutral-800 pb-4 mb-4">
        Narratives represent AI-clustered story themes emerging across travel videos.
      </p>

      <div className="relative flex gap-16 text-white">
        {/* LEFT SIDE LIST */}
        <div className="flex flex-col gap-4 w-1/2 mt-8">
          {displayedNarratives.map((item) => (
            <motion.p
              key={item.id}
              onClick={() => setSelected(item)}
              className="cursor-pointer text-md text-gray-300 hover:text-purple-300 transition pl-5 mr-5"
              whileHover={{ x: 5 }}
            >
              "{item.text}"
            </motion.p>
          ))}
        </div>

        {/* FLOATING BUBBLE */}
        <AnimatePresence>
          {selected && (
            <motion.div
              key={selected.id}
              initial={{ opacity: 0, scale: 0.9, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 10 }}
              transition={{ duration: 0.25 }}
              className="absolute right-0 top-10 w-1/2 bg-purple-300 text-black rounded-3xl p-8 shadow-2xl"
            >
              <h2 className="text-2xl pt-8 px-8 italic mb-0">
                "{selected.text}"
              </h2>

              <p className="text-sm mb-6 text-gray-700 px-8 pt-4">
                {secondaryLabel(selected)}
              </p>

              <div className="grid grid-cols-2 gap-6 text-lg pt-2 px-8 pb-8">
                <div>
                  <div className="text-3xl font-bold">
                    {selected.cluster_size}
                  </div>
                  <div className="text-sm">Similar Narratives</div>
                </div>

                <div>
                  <div className="text-3xl font-bold truncate">
                    {selected.creator_name !== "—"
                      ? selected.creator_name
                      : selected.destination}
                  </div>
                  <div className="text-sm">
                    {selected.creator_name !== "—" ? "Top Creator" : "Destination"}
                  </div>
                </div>

                <div>
                  <div className="text-3xl font-bold">
                    {selected.computed_at
                      ? new Date(selected.computed_at).toLocaleDateString()
                      : "—"}
                  </div>
                  <div className="text-sm">Last Updated</div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}