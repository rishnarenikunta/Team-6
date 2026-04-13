import React from 'react'


export const TrendingClaims = () => {
  return (
    <div>
         <h2 className="text-5xl font-semibold text-white tracking-tight mb-2">Trending Claims</h2>
            <p className="text-lg text-gray-300 mb-4">Explore the most talked-about claims in the travel world.</p> 
            <ClaimsCarousel />
    </div>
  )
}
