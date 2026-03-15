"use client";

import { useState } from "react";
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

const data = [
  { week: "W1", Japan: 1200, Portugal: 1100, Bali: 900 },
  { week: "W2", Japan: 1400, Portugal: 1000, Bali: 1000 },
  { week: "W3", Japan: 2500, Portugal: 1500, Bali: 1200 },
  { week: "W4", Japan: 2700, Portugal: 1800, Bali: 2000 },
  { week: "W5", Japan: 3000, Portugal: 2600, Bali: 2900 },
];

export default function TrendingLocations() {
  const [activeCountry, setActiveCountry] = useState<string | null>("Japan");

  return (
    <div className="w-full h-dvh pt-8 px-8">
    <h2 className="text-2xl font-semibold text-white tracking-tight mb-2">
        Destination Trend Graph
      </h2>
      <p className="text-sm text-neutral-400 border-b border-neutral-800 pb-4 mb-4">Narratives represent AI-clustered story themes emerging across travel videos.</p>
    <div className="p-10 flex gap-10 height-100vh mt-8 pt-2">
      
      {/* LEFT GRAPH */}
      <div className="w-1/2 h-[350px] pt-3">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid stroke="#222" vertical={false} />
            <XAxis dataKey="week" stroke="#666" />
            <Tooltip content={() => null} />
            <Legend
              verticalAlign="bottom"
              align="left"
              iconType="square"
              wrapperStyle={{ paddingTop: 10, color: "#cbd5e1" }}
            />
            <Line
              type="monotone"
              dataKey="Japan"
              stroke="#ff7cf0"
              strokeWidth={3}
              dot={{ r: 4 }}
              activeDot={{
                r: 8, 
                onMouseEnter: () => setActiveCountry("Japan"),
              }}
            />

            <Line
              type="monotone"
              dataKey="Portugal"
              stroke="#c084fc"
              strokeWidth={3}
              dot={{ r: 4 }}
              activeDot={{
                r: 8,
                onMouseEnter: () => setActiveCountry("Portugal"),
              }}
            />

            <Line
              type="monotone"
              dataKey="Bali"
              stroke="#6366f1"
              strokeWidth={3}
              dot={{ r: 4 }}
              activeDot={{
                r: 8,
                onMouseEnter: () => setActiveCountry("Bali"),
              }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* RIGHT INFO BUBBLE */}
      <div className="w-1/2 relative min-h-[260px]">
        <AnimatePresence>
          {activeCountry && (
            <motion.div
              key={activeCountry}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="absolute top-0 left-0 right-0 max-w-[430px] bg-purple-300 text-black rounded-2xl p-8 shadow-2xl"
            >
              <h2 className="text-xl font-semibold mb-2">
                {activeCountry}
              </h2>

              <p className="font-medium mb-1">
                4,812 mentions
              </p>

              <p className="font-medium mb-4">
                Growth velocity: +31%
              </p>

              <p className="text-sm text-gray-700">
                Discussion around {activeCountry} surged following multiple
                “budget itinerary” videos. Growth appears organic and
                sustained over 3 weeks.
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
    </div>
  );
}