import Image from "next/image";
import Navbar from "./components/Navbar";
import DiscoverBar from "./components/DiscoverBar";
import TrendingTopics from "./components/TrendingTopics";
import StatsMain from "./sections/StatsMain";

export default function Home() {
  return (
    <div>
      <DiscoverBar />
      <TrendingTopics />
      <StatsMain />
    </div>
  );
}
