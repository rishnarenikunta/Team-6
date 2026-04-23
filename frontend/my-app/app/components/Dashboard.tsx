// 'use client'

// import Link from "next/link"
// import { useState } from "react"
// import { TypeAnimation } from "react-type-animation"
// import DiscoverBar from "./DiscoverBar"
// import { useRouter } from "next/navigation"
// import { TrendingClaims } from "../sections/TrendingClaims"
// import StatsMain from "../sections/StatsMain"
// import TrendingNarratives from "../sections/TrendingNarratives"
// import TrendingLocations from "../sections/TrendingLocations"
// import TrendingTopics from "./TrendingTopics"
// import TopCountries from "./TopCountries"

// export default function Dashboard() {
//   const [searchTerm, setSearchTerm] = useState("")
//   const [isTyping, setIsTyping] = useState(true)
//   const router = useRouter()

//   return (
//     <div className="bg-gradient-to-b from-[#0c0c12] via-[#130f18] to-[#0c0c12] text-white">
//       <div className="mx-auto max-w-6xl px-6 pb-16 pt-10 space-y-12">
//         <header className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
//           <div className="space-y-2">
//             <p className="text-xs uppercase tracking-[0.3em]  text-gray-400">Welcome to YouTravel</p>
//             <h1 className="text-4xl font-semibold leading-tight">Dashboard</h1>
//             <p className="text-sm text-gray-400 max-w-2xl">
//               Combine creator sentiment, trend velocity, and safety signals before you book. Start with a search or
//               pick a quick filter to explore narratives already emerging on YouTube.
//             </p>
//           </div>
//         </header>

//         <form className="w-full">
//           <label className="sr-only" htmlFor="discover-search">
//             Search destinations
//           </label>
//           <div className="relative flex gap-2 bg-[#16161e] border border-[#242436] rounded-2xl px-4 py-3 shadow-lg shadow-black/40">
//             <input
//               id="discover-search"
//               type="search"
//               placeholder="search your next travel destination"
//               className="flex-1 bg-transparent text-sm text-white focus:outline-none placeholder:text-transparent"
//               value={searchTerm}
//               onChange={(e) => setSearchTerm(e.target.value)}
//               onFocus={() => setIsTyping(false)}
//               onBlur={() => {
//                 if (!searchTerm) setIsTyping(true)
//               }}
//             />
//             {isTyping && !searchTerm && (
//               <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-sm text-gray-500">
//                 <TypeAnimation sequence={["search your next travel destination", 1600, ""]} speed={60} repeat={Infinity} cursor={false} />
//               </span>
//             )}
//             <button
//               type="button"
//               className="rounded-xl bg-white/10 px-4 py-2 text-sm font-medium transition hover:bg-white/20"
//               onClick={() => router.push(`/discover/${searchTerm}`)}
//             >
//               Search
//             </button>
//           </div>
//         </form>

//         <TrendingTopics />
//         <StatsMain />
//         <TrendingNarratives />
//         <TopCountries />
//         <TrendingLocations />
//         <TrendingClaims />
//       </div>
//     </div>
//   )
// }
