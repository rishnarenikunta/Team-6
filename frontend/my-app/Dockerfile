FROM node:20-alpine AS base

# Install dependencies
FROM base AS deps
# libc6-compat is often required by Node.js on Alpine
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Copy package.json and lockfile (adjust if using yarn or pnpm)
COPY package.json package-lock.json* ./
RUN npm ci

# Build the application
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules

# ENV VAR for NExT.JS API URL (can be overridden at runtime)
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Build the Next.js app (creates the .next/standalone directory)
RUN npm run build

# Production Runner
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production

# Create a non-root user for security
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy the public directory
COPY --from=builder /app/public ./public

# Copy the standalone build and static files, setting permissions
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Switch to the non-root user
USER nextjs

# Expose the port
EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Start the application using the standalone server.js
CMD ["node", "server.js"]