import Image from "next/image";
import Navbar from "./components/Navbar";
import DiscoverBar from "./components/DiscoverBar";
import TrendingTopics from "./components/TrendingTopics";
import StatsMain from "./sections/StatsMain";
import TrendingNarratives from "./sections/TrendingNarratives";
import TrendingLocations from "./sections/TrendingLocations";
import { TrendingClaims } from "./sections/TrendingClaims";
import Dashboard from "./components/Dashboard";

export default function Home() {
  return (
    <div className="bg-gradient-to-b from-[#0b0b0e] via-[#101014] to-[#0b0b0e] text-foreground max-w-6xl align-middle mx-auto">
      <Dashboard />
      <DiscoverBar />
      <TrendingTopics />
      <StatsMain />
      <TrendingNarratives />
      <TrendingLocations />
      <TrendingClaims />
    </div>
  );
}
