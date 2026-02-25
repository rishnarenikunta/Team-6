import React from 'react'
import ClaimsCarousel from '../components/ClaimsCarousel';


export const TrendingClaims = () => {
  return (
    <div className='p-8 w-full h-dvh'>
         <h2 className="text-3xl font-semibold text-foreground tracking-tight mb-2">Trending Claims</h2>
          <p className="text-lg text-gray-300 mb-4">Explore the most talked-about claims in the travel world.</p> 
          <ClaimsCarousel />

    </div>
  )
}
