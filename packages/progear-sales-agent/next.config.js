const path = require('path');

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Produce a self-contained server bundle (.next/standalone) so the app can run
  // on localhost, in Docker, or on Azure App Service / Container Apps with
  // `node server.js` - no Vercel-specific runtime required.
  output: 'standalone',
  experimental: {
    // This package lives in an npm workspace; trace files from the monorepo root
    // so the standalone bundle includes hoisted node_modules.
    outputFileTracingRoot: path.join(__dirname, '../../'),
  },
  // Allow connections to backend
  async rewrites() {
    return [
      {
        source: '/api/backend/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
