"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"

export default function TrendingTopics() {
  const router = useRouter()
  const [topics, setTopics] = useState<string[]>([])

  useEffect(() => {
    async function fetchTopics() {
      try {
        const res = await fetch("http://127.0.0.1:8000/api/topics/trending")
        const data = await res.json()
        setTopics(data.topics)
        console.log("Number of trending topics:", data.length)
      } catch (error) {
        console.error("Failed to fetch topics:", error)
      }
    }

    fetchTopics()
  }, [])

  return (
    <div className="w-full px-8 py-8">
      <h2 className="text-2xl font-semibold text-white mb-6 tracking-tight">
        Trending Topics
      </h2>

      <div className="flex gap-3 overflow-x-auto whitespace-nowrap no-scrollbar">
        {topics.map((topic) => (
          <button
            key={topic}
            onClick={() => router.push(`/discover?q=${topic}`)}
            className="
              flex-shrink-0
              px-5 py-2
              text-sm font-medium
              text-gray-300
              border border-neutral-800
              rounded-full
              hover:border-neutral-600
              hover:text-white
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