"use client"

import { useRouter } from "next/navigation"

const topics = [
  "kyoto",
  "seoul",
  "lisbon",
  "europe",
  "paris",
  "london",
  "maldives",
  "tokyo",
  "bali",
  "sydney"
]

export default function TrendingTopics() {
  const router = useRouter()

  return (
    <div className="w-full pt-6 text-foreground space-y-3">
      {/* Section Title */}
      <h2 className="text-sm font-semibold text-gray-300">
        Trending Topics
      </h2>

      {/* Scroll Container */}
      <div className="flex flex-wrap gap-3 py-2 max-w-full md:flex-nowrap md:overflow-x-auto md:whitespace-nowrap md:no-scrollbar">
        {topics.map((topic) => (
          <button
            key={topic}
            onClick={() => router.push(`/discover/${topic}`)}
            className="
              rounded-full
              border 
              border-white/10 
              bg-white/5 
              px-4 
              py-2 
              text-xs 
              text-gray-200 
              transition 
              hover:-translate-y-0.5 
              hover:border-white/25 
              hover:bg-[#E4CAFF] 
              hover:text-[#1c1b22]
            "
          >
            {topic}
          </button>
        ))}
      </div>
    </div>
  )
}
