# ProGear Sales Agent (Next.js frontend)
#
# Build context must be the REPOSITORY ROOT (npm workspace), e.g.:
#   docker build -f packages/progear-sales-agent/Dockerfile -t progear-frontend .
#
# NEXT_PUBLIC_* variables are inlined by Next.js at BUILD time, so they are
# passed as --build-arg here. Server-only secrets (NEXTAUTH_SECRET,
# OKTA_CLIENT_SECRET, NEXTAUTH_URL) are read at RUNTIME from the container
# environment / Azure App Settings and must NOT be baked into the image.

# ---------- deps ----------
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
COPY packages/progear-sales-agent/package.json ./packages/progear-sales-agent/
COPY packages/progear-sales-mcp-server/package.json ./packages/progear-sales-mcp-server/
RUN npm ci --ignore-scripts

# ---------- build ----------
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY package.json package-lock.json ./
COPY packages/progear-sales-agent ./packages/progear-sales-agent
COPY packages/progear-sales-mcp-server/package.json ./packages/progear-sales-mcp-server/

ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ARG NEXT_PUBLIC_OKTA_CLIENT_ID
ARG NEXT_PUBLIC_OKTA_DOMAIN
ARG NEXT_PUBLIC_OKTA_ISSUER
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL \
    NEXT_PUBLIC_OKTA_CLIENT_ID=$NEXT_PUBLIC_OKTA_CLIENT_ID \
    NEXT_PUBLIC_OKTA_DOMAIN=$NEXT_PUBLIC_OKTA_DOMAIN \
    NEXT_PUBLIC_OKTA_ISSUER=$NEXT_PUBLIC_OKTA_ISSUER \
    NEXT_TELEMETRY_DISABLED=1

RUN npm run build --workspace=packages/progear-sales-agent

# ---------- run ----------
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME=0.0.0.0

RUN addgroup --system --gid 1001 nodejs && adduser --system --uid 1001 nextjs

# Standalone output is rooted at the monorepo root (see next.config.js
# outputFileTracingRoot), so server.js lives under packages/progear-sales-agent.
COPY --from=builder --chown=nextjs:nodejs /app/packages/progear-sales-agent/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/packages/progear-sales-agent/.next/static ./packages/progear-sales-agent/.next/static

USER nextjs
EXPOSE 3000

CMD ["node", "packages/progear-sales-agent/server.js"]
