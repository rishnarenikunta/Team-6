import Link from "next/link"
import React from "react"

const DiscoverBar = () => {
  return (
    <div className="w-full flex justify-center">
      <Link
        href="/discover"
        className="block text-sm p-3 m-5 w-full bg-gray-400 text-black rounded-3xl border border-[#404040] transition"
      >
        search your next travel destination ✈️
      </Link>
    </div>
  )
}

export default DiscoverBar
