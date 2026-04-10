"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface Narrative {
  id: string;
  text: string;
  destination: string;
  cluster_size: number;
  computed_at: string | null;
  source: string;
  creator_name: string;
  views: number;
}

export default function TrendingNarratives() {
  const [narratives, setNarratives] = useState<Narrative[]>([]);
  const [selected, setSelected] = useState<Narrative | null>(null);

  useEffect(() => {
    async function fetchNarratives() {
      try {
        const res = await fetch(`/api/narratives/trending`);
        if (!res.ok) throw new Error(`API error ${res.status}`);
        const data: Narrative[] = await res.json();
        setNarratives(data);
        setSelected(data[0] ?? null);
        console.log("Number of trending topics:", data.length)
      } catch (err) {
        console.error("Failed to fetch narratives:", err);
      }
    }
    fetchNarratives();
  }, []);

  // only display narratives with a destination and text and only the top 10 or min(narratives.length, 10 and unique text
  const filteredNarratives = narratives.filter(narrative => narrative.destination && narrative.text);
  const uniqueNarrativesMap = new Map<string, Narrative>();
  filteredNarratives.forEach(narrative => {
    if (!uniqueNarrativesMap.has(narrative.text)) {
      uniqueNarrativesMap.set(narrative.text, narrative);
    }
  });
  const uniqueNarratives = Array.from(uniqueNarrativesMap.values());
  const displayedNarratives = uniqueNarratives.slice(0, 6);


  return (
    <div className="w-full mt-10 h-fit mb-50">
      <h2 className="text-2xl font-semibold text-white tracking-tight mb-2">
        Trending Narratives
      </h2>
      <p className="text-sm text-neutral-400 border-b border-neutral-800 pb-4 mb-4">Narratives represent AI-clustered story themes emerging across travel videos.</p>
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
                {selected.destination}
              </p>

              <div className="grid grid-cols-2 gap-6 text-lg pt-2 px-8 pb-8">
                <div>
                  <div className="text-3xl font-bold">{selected.cluster_size}</div>
                  <div className="text-sm">Similar Narratives</div>
                </div>

                <div>
                  <div className="text-3xl font-bold">{selected.views.toLocaleString()}</div>
                  <div className="text-sm">Views</div>
                </div>

                <div>
                  <div className="text-3xl font-bold truncate">{selected.creator_name || selected.source}</div>
                  <div className="text-sm">Top Creator</div>
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