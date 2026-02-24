import Image from "next/image";
import Navbar from "./components/Navbar";
import DiscoverBar from "./components/DiscoverBar";
import TrendingTopics from "./components/TrendingTopics";
import StatsMain from "./sections/StatsMain";
import TrendingNarratives from "./sections/TrendingNarratives";
import TrendingLocations from "./sections/TrendingLocations";
import ClaimCarousel from "./components/ClaimsCarousel";

export default function Home() {
  return (
    <div className="bg-background text-foreground">
      <DiscoverBar />
      <TrendingTopics />
      <StatsMain />
      <TrendingNarratives />
      <TrendingLocations />
      <ClaimCarousel />
    </div>
  );
}
