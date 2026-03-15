"use client"

import { motion } from "framer-motion";
import { useRef, useEffect, useState } from "react";
// import "./ClaimsCarousel.css";

// ── Types ─────────────────────────────────────────────────────────────────────

interface Claim {
  id: string;
  text: string;
  source: string;
  views: string;
  engagement: string;
  growth: string;
  destination: string;
  verified: boolean;
}

// ── Component ─────────────────────────────────────────────────────────────────

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function ClaimsCarousel() {
  const carouselRef = useRef<HTMLDivElement>(null);
  const [claims, setClaims]   = useState<Claim[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState<string | null>(null);

  useEffect(() => {
    async function fetchClaims() {
      try {
        const res = await fetch(`${API_BASE}/api/claims/trending`);
        if (!res.ok) throw new Error(`API error ${res.status}`);
    
        const data = await res.json();
    
        console.log("RAW API RESPONSE:", data);   // 👈 add this
        console.log("First claim:", data[0]);     // 👈 useful
    
        setClaims(data);
      } catch (err) {
        console.error("Fetch error:", err);
        setError("Could not load claims.");
      } finally {
        setLoading(false);
      }
    }
    fetchClaims();
  }, []);

  // ── Loading skeleton ────────────────────────────────────────────────────────
  if (loading) {
    return (
      <div className="carousel-wrapper">
        <div className="carousel-track" style={{ pointerEvents: "none" }}>
          {[1, 2, 3, 4].map((n) => (
            <div
              key={n}
              className="carousel-card"
              style={{ opacity: 0.4, animation: "pulse 1.5s ease-in-out infinite" }}
            />
          ))}
        </div>
      </div>
    );
  }

  // ── Error state ─────────────────────────────────────────────────────────────
  if (error) {
    return (
      <div className="carousel-wrapper">
        <p style={{ color: "#f87171", padding: "1rem", fontSize: "0.875rem" }}>{error}</p>
      </div>
    );
  }

  // ── Cards ───────────────────────────────────────────────────────────────────
  return (
    <div
      ref={carouselRef}
      className="w-full overflow-x-auto no-scrollbar pb-4 snap-x snap-mandatory"
    >
      <motion.div
        className="flex min-w-max gap-5 px-1 cursor-grab"
        drag="x"
        dragConstraints={carouselRef}
        dragElastic={0.08}
      >
        {claims.map((claim) => (
          <motion.div
            key={claim.id}
            className="carousel-card"
            whileHover={{ scale: 1.05, y: -8 }}
            transition={{ type: "spring", stiffness: 200, damping: 15 }}
          >
            <h3 className="text-sm font-semibold text-gray-100 mb-3">Claim:</h3>

            <p className="text-lg font-medium text-purple-200 mb-4 leading-snug">“{claim.text}”</p>

            <div className="space-y-1 text-sm text-gray-200">
              <p>Source: {claim.source}</p>
              <p>Views: {claim.views}</p>
              <p>Engagement Rate: {claim.engagement}</p>
              <p>Growth Velocity: {claim.growth}</p>
            </div>
          </motion.div>
        ))}
      </motion.div>
    </div>
  )
}
