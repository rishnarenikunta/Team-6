"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface Narrative {
  id: number;
  title: string;
  description: string;
  stats: {
    videos: number;
    claims: number;
    growth: string;
    sentiment: string;
  };
}

const narratives: Narrative[] = [
  {
    id: 1,
    title: "Japan Is Surprisingly Affordable",
    description:
      "This narrative centers on the perception that Japan offers high-quality experiences at lower-than-expected costs.",
    stats: {
      videos: 326,
      claims: 1842,
      growth: "+28%",
      sentiment: "82%",
    },
  },
  {
    id: 2,
    title: "Hidden Gems in Portugal",
    description: "Explores lesser-known coastal towns and authentic experiences.",
    stats: {
      videos: 211,
      claims: 980,
      growth: "+12%",
      sentiment: "76%",
    },
  },
  {
    id: 3,
    title: "Japan Is Surprisingly Affordable",
    description:
      "This narrative centers on the perception that Japan offers high-quality experiences at lower-than-expected costs.",
    stats: {
      videos: 326,
      claims: 1842,
      growth: "+28%",
      sentiment: "82%",
    },
  },
  {
    id: 4,
    title: "Hidden Gems in Portugal",
    description: "Explores lesser-known coastal towns and authentic experiences.",
    stats: {
      videos: 211,
      claims: 980,
      growth: "+12%",
      sentiment: "76%",
    },
  },
  {
    id: 5,
    title: "Japan Is Surprisingly Affordable",
    description:
      "This narrative centers on the perception that Japan offers high-quality experiences at lower-than-expected costs.",
    stats: {
      videos: 326,
      claims: 1842,
      growth: "+28%",
      sentiment: "82%",
    },
  },
  {
    id: 6,
    title: "Hidden Gems in Portugal",
    description: "Explores lesser-known coastal towns and authentic experiences.",
    stats: {
      videos: 211,
      claims: 980,
      growth: "+12%",
      sentiment: "76%",
    },
  },
];

export default function TrendingNarratives() {
  const [hovered, setHovered] = useState<Narrative | null>(narratives[0]);

  return (
    <div className="w-full h-dvh p-8 mt-6">
      <h2 className="text-3xl font-semibold text-white tracking-tight mb-2">
        Trending Narratives
      </h2>
      <p className="text-sm text-neutral-400 border-b border-neutral-800 pb-4 mb-4">Narratives represent AI-clustered story themes emerging across travel videos.</p>
    <div className="relative flex gap-16 text-white">

      {/* LEFT SIDE LIST */}
      <div className="flex flex-col gap-4 w-1/2 mt-8">
        {narratives.map((item) => (
          <motion.p
            key={item.id}
            onClick={() => setHovered(item)}
            className="cursor-pointer text-2xl text-gray-300 hover:text-purple-300 transition pl-5"
            whileHover={{ x: 5 }}
          >
            “{item.title}”
          </motion.p>
        ))}
      </div>

      {/* FLOATING BUBBLE */}
      <AnimatePresence>
        {hovered && (
          <motion.div
            key={hovered.id}
            initial={{ opacity: 0, scale: 0.9, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 10 }}
            transition={{ duration: 0.25 }}
            className="absolute right-0 top-10 w-1/2 bg-purple-300 text-black rounded-3xl p-8 shadow-2xl"
          >
            <h2 className="text-2xl pt-8 px-8 italic mb-0">
              “{hovered.title}”
            </h2>

            <p className="text-sm mb-6 text-gray-700 p-8">
              {hovered.description}
            </p>

            <div className="grid grid-cols-2 gap-6 text-lg pt-2 px-8">
              <div>
                <div className="text-3xl font-bold">
                  {hovered.stats.videos}
                </div>
                <div className="text-sm">Videos</div>
              </div>

              <div>
                <div className="text-3xl font-bold">
                  {hovered.stats.claims.toLocaleString()}
                </div>
                <div className="text-sm">Claims</div>
              </div>

              <div>
                <div className="text-3xl font-bold">
                  {hovered.stats.growth}
                </div>
                <div className="text-sm">Growth</div>
              </div>

              <div>
                <div className="text-3xl font-bold">
                  {hovered.stats.sentiment}
                </div>
                <div className="text-sm">Positive Sentiment</div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
    </div>
  );
}
