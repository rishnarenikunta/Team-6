"use client";

import { useState, useEffect } from "react";
import {
  LineChart,
  Line,
  XAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Legend,
} from "recharts";
import { motion, AnimatePresence } from "framer-motion";


const LINE_COLORS = ["#ff7cf0", "#c084fc", "#6366f1"];

interface TimelineEntry {
  period: string;
  mentions: number;
}

interface Location {
  name: string;
  total: number;
  timeline: TimelineEntry[];
}

// Merge all locations' timelines into a unified chart data array
function buildChartData(locations: Location[]) {
  const periodSet = new Set<string>();
  locations.forEach((loc) => (loc.timeline ?? []).forEach((t) => periodSet.add(t.period)));
  const periods = Array.from(periodSet).sort().slice(-10);

  return periods.map((period) => {
    const row: Record<string, string | number> = { period };
    locations.forEach((loc) => {
      const entry = (loc.timeline ?? []).find((t) => t.period === period);
      row[loc.name] = entry ? entry.mentions : 0;
    });
    return row;
  });
}

export default function TrendingLocations() {
  const [locations, setLocations] = useState<Location[]>([]);
  const [activeCountry, setActiveCountry] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchLocations() {
      try {
        const res = await fetch(`/api/destinations/trending-locations`);
        if (!res.ok) throw new Error(`API ${res.status}`);
        const data: Location[] = await res.json();
        setLocations(data);
        if (data.length > 0) setActiveCountry(data[0].name);
      } catch (err) {
        console.error("Failed to fetch trending locations:", err);
        setError("Could not load trending locations.");
      } finally {
        setLoading(false);
      }
    }
    fetchLocations();
  }, []);

  if (loading) {
    return (
      <div className="w-full h-64 rounded-2xl bg-white/10 animate-pulse mt-8" />
    );
  }

  if (error) {
    return (
      <div className="w-full mt-8 rounded-lg border border-red-500/40 bg-red-900/60 px-4 py-3 text-sm text-red-100">
        {error}
      </div>
    );
  }

  const chartData = buildChartData(locations);
  const activeLocation = locations.find((l) => l.name === activeCountry) ?? null;

  // Calculate growth: compare first vs last timeline entry
  function calcGrowth(loc: Location): string {
    if (loc.timeline.length < 2) return "N/A";
    const first = loc.timeline[0].mentions;
    const last = loc.timeline[loc.timeline.length - 1].mentions;
    if (first === 0) return "N/A";
    const pct = Math.round(((last - first) / first) * 100);
    return `${pct > 0 ? "+" : ""}${pct}%`;
  }

  return (
    <div className="w-full h-full pt-8 px-8">
      <h2 className="text-2xl font-semibold text-white tracking-tight mb-2">
        Destination Trend Graph
      </h2>
      <p className="text-sm text-neutral-400 border-b border-neutral-800 pb-4 mb-4">
        Narratives represent AI-clustered story themes emerging across travel videos.
      </p>

      <div className="p-10 flex gap-10 mt-8 pt-2">
        {/* LEFT GRAPH */}
        <div className="w-1/2 h-[350px] pt-3">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid stroke="#222" vertical={false} />
              <XAxis dataKey="period" stroke="#666" />
              <Tooltip content={() => null} />
              <Legend
                verticalAlign="bottom"
                align="left"
                iconType="square"
                wrapperStyle={{ paddingTop: 10, color: "#cbd5e1" }}
              />
              {locations.map((loc, i) => (
                <Line
                  key={loc.name}
                  type="monotone"
                  dataKey={loc.name}
                  stroke={LINE_COLORS[i % LINE_COLORS.length]}
                  strokeWidth={3}
                  dot={{ r: 4 }}
                  activeDot={{
                    r: 8,
                    onMouseEnter: () => setActiveCountry(loc.name),
                  }}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* RIGHT INFO BUBBLE */}
        <div className="w-1/2 relative min-h-[260px]">
          <AnimatePresence>
            {activeCountry && activeLocation && (
              <motion.div
                key={activeCountry}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="absolute top-0 left-0 right-0 max-w-[430px] bg-purple-300 text-black rounded-2xl p-8 shadow-2xl"
              >
                <h2 className="text-xl font-semibold mb-2">{activeCountry}</h2>
                <p className="font-medium mb-1">
                  {activeLocation.total.toLocaleString()} total mentions
                </p>
                <p className="font-medium mb-4">
                  Growth velocity: {calcGrowth(activeLocation)}
                </p>
                <p className="text-sm text-gray-700">
                  Discussion around {activeCountry} is tracked across{" "}
                  {activeLocation.timeline.length} time periods in the dataset.
                  Click a line on the chart to explore another destination.
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
