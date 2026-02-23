import Link from "next/link"
import React from "react"

const DiscoverBar = () => {
  return (
    <div className="w-full flex justify-center">
      <Link
        href="/discover"
        className="block text-sm p-3 m-5 w-full bg-[#353535] text-white rounded-3xl hover:bg-[#404040] transition"
      >
        search your next travel destination ✈️
      </Link>
    </div>
  )
}

export default DiscoverBar
