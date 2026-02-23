"use client"

import Link from "next/link"

export default function Navbar() {
  return (
    <nav className="w-full border-b bg-# text-white border-neutral-800
 px-8 py-4">
      <div className="flex items-center justify-between">

        {/* Left Side */}
        <div className="flex flex-col">
          <h1 className="text-3xl font-bold">YouTravel</h1>
          <p className="text-sm text-gray-500">
            AI-powered insights from YouTube travel content. Monitor narratives, detect trends, and evaluate creator risk in real time.
          </p>
        </div>

        {/* Right Side */}
        <div className="flex gap-8 text-sm font-medium">
          <Link href="/discover" className="hover:text-blue-600 transition">
            Discover
          </Link>
          <Link href="/narratives" className="hover:text-blue-600 transition">
            Narratives
          </Link>
          <Link href="/settings" className="hover:text-blue-600 transition">
            Settings
          </Link>
        </div>

      </div>
    </nav>
  )
}
