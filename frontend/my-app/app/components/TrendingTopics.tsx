"use client"

import { useRouter } from "next/navigation"

const topics = [
  "seoul",
  "south korea",
  "gyeongju",
  "europe",
  "paris",
  "london",
  "maldives",
  "tokyo",
  "bali",
  "sydney",
  "dubai",
  "rome",
  "barcelona",
  "singapore",
  "new york",
  "los angeles"
]

export default function TrendingTopics() {
  const router = useRouter()

  return (
    <div className="w-full px-8 py-8 text-foreground">
      {/* Section Title */}
      <h2 className="text-2xl font-semibold text-white mb-6 tracking-tight">
        Trending Topics
      </h2>

      {/* Scroll Container */}
      <div className="flex gap-3 overflow-x-auto whitespace-nowrap no-scrollbar">
        {topics.map((topic) => (
          <button
            key={topic}
            onClick={() => router.push(`/discover?q=${topic}`)}
            className="
              flex-shrink-0
              px-5 py-2
              text-sm font-medium
              text-foreground
              border border-neutral-800
              rounded-full
              hover:bg-[#dd9eff]
              hover:text-black
              hover:shadow-[0_0_12px_rgba(255,255,255,0.05)]
              transition-all duration-200
            "
          >
            {topic}
          </button>
        ))}
      </div>
    </div>
  )
}
