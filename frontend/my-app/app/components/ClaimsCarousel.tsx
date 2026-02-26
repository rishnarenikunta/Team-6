"use client";

import { motion } from "framer-motion";
import { useRef } from "react";
import "./ClaimsCarousel.css";


const claims = [
  {
    text: "You can eat in Tokyo for under $10.",
    source: "WonderWithMia",
    views: "842K",
    engagement: "9.8%",
    growth: "+37%",
  },
  {
    text: "Tokyo convenience stores are underrated.",
    source: "TravelTomo",
    views: "620K",
    engagement: "8.1%",
    growth: "+21%",
  },
  {
    text: "Japan train passes save you hundreds.",
    source: "NomadNick",
    views: "1.2M",
    engagement: "11.2%",
    growth: "+42%",
  },
  {
    text: "Hidden ramen spots beat tourist spots.",
    source: "WanderNina",
    views: "540K",
    engagement: "7.5%",
    growth: "+18%",
  },
  {
    text: "Hidden ramen spots beat tourist spots.",
    source: "WanderNina",
    views: "540K",
    engagement: "7.5%",
    growth: "+18%",
  }
];

export default function ClaimsCarousel() {
  const carouselRef = useRef<HTMLDivElement>(null);

  return (
    <div className="carousel-wrapper">
      <motion.div
        ref={carouselRef}
        className="carousel-track"
        drag="x"
        dragConstraints={carouselRef}
        dragElastic={0.08}
      >
        {claims.map((claim, index) => (
          <motion.div
            key={index}
            className="carousel-card"
            whileHover={{ scale: 1.05, y: -8 }}
            transition={{ type: "spring", stiffness: 200, damping: 15 }}
          >
            <h3 className="card-title">Claim:</h3>

            <p className="card-quote">“{claim.text}”</p>

            <div className="card-meta">
              <p>Source: {claim.source}</p>
              <p>Views: {claim.views}</p>
              <p>Engagement Rate: {claim.engagement}</p>
              <p>Growth Velocity: {claim.growth}</p>
            </div>
          </motion.div>
        ))}
      </motion.div>
    </div>
  );
}
