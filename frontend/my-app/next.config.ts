import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  output: 'standalone',
  async rewrites() {
    return [
      {
        // When the browser requests /api/...
        source: '/api/:path*',
        // The Next.js server silently forwards it to your live backend URL
        destination: `${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/api/:path*`,
      },
    ]
  },
};

export default nextConfig;
