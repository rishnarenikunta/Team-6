import Link from "next/link"
import DiscoverBar from "./DiscoverBar"

export default function Dashboard() {
  return (
    <div className="text-foreground">
      <div className="max-w-6xl mx-auto px-6 pb-5 pt-10 space-y-10">
        <header className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div className="space-y-2">
            <p className="text-xs uppercase tracking-[0.3em]  text-gray-400">Welcome to YouTravel</p>
            <h1 className="text-4xl font-semibold leading-tight">Dashboard</h1>
            <p className="text-sm text-gray-400 max-w-2xl">
              Combine creator sentiment, trend velocity, and safety signals before you book. Start with a search or
              pick a quick filter to explore narratives already emerging on YouTube.
            </p>
          </div>

          {/* <form className="w-full md:w-[360px]">
            <label className="sr-only" htmlFor="discover-search">
              Search destinations
            </label>
            <div className="flex gap-2 bg-[#ffffff] border border-[#242436] rounded-2xl px-4 py-3 shadow-lg shadow-black/40">
              <input
                id="discover-search"
                type="search"
                placeholder="Search a city, region, or keyword"
                className="flex-1 bg-transparent text-sm focus:outline-none placeholder:[#404040]"
              />
              <button
                type="button"
                className="rounded-xl bg-white/10 px-4 py-2 text-sm font-medium transition hover:bg-white/20"
              >
                Preview signals
              </button>
            </div>
          </form> */}

          {/* <DiscoverBar /> */}
        </header>
        
      </div>
    </div>
  )
}
