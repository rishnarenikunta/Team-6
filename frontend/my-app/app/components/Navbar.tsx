"use client"

import Link from "next/link"

export default function Navbar() {
  return (
    <aside className="h-full w-full shrink-0 bg-gradient-to-b from-[#16121a] via-[#0e0e16] to-[#0a0a12] border-r border-white/10 shadow-2xl shadow-black/40 px-6 py-8 flex flex-col gap-8">
      <div className="space-y-2">
        <p className="text-xs uppercase tracking-[0.3em] text-gray-500">your ultimate travel guide</p>
        <h1 className="text-2xl font-semibold text-white">YouTravel</h1>
        <p className="text-sm text-gray-500">
          Monitor narratives, detect trends, evaluate creator risk in real time.
        </p>
      </div>

      <nav className="flex flex-col gap-3 text-sm font-medium text-gray-200">
        <NavLink href="/" label="Dashboard" />
        {/* <NavLink href="/discover" label="Discover" /> */}
        <NavLink href="/narratives" label="Narratives" />
        <NavLink href="/creators" label="Creators" />
        <NavLink href="/settings" label="Settings" />
      </nav>

      <div className="mt-auto space-y-2 text-xs text-gray-500">
        <p>Signals refreshed hourly from YouTube uploads.</p>
        <p className="text-gray-400">v0.1 dashboard</p>
      </div>
    </aside>
  )
}

function NavLink({ href, label }: { href: string; label: string }) {
  return (
    <Link
      href={href}
      className="rounded-xl border border-white/5 bg-white/5 px-4 py-3 hover:border-white/20 hover:bg-white/10 transition"
    >
      {label}
    </Link>
  )
}
