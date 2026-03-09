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