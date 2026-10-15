import { NextResponse } from 'next/server';
import { oktaIssuer, oktaClientId } from '@/lib/auth';

// Evaluate at request time so this reflects the running container's
// environment (Azure App Settings / docker env), not build-time values.
export const dynamic = 'force-dynamic';

export async function GET() {
  return NextResponse.json({
    // Effective values NextAuth is actually using (runtime var wins over build-time var)
    effectiveIssuer: oktaIssuer || 'NOT SET',
    effectiveIssuerSource: process.env.OKTA_ISSUER
      ? 'OKTA_ISSUER (runtime)'
      : process.env.NEXT_PUBLIC_OKTA_ISSUER
        ? 'NEXT_PUBLIC_OKTA_ISSUER (baked at build)'
        : 'none',
    issuerIsOrgAuthServer: !!oktaIssuer && !/\/oauth2\//.test(oktaIssuer),
    effectiveClientIdLength: oktaClientId.length,

    // Raw inputs
    hasClientId: !!process.env.NEXT_PUBLIC_OKTA_CLIENT_ID,
    clientIdLength: process.env.NEXT_PUBLIC_OKTA_CLIENT_ID?.length || 0,
    hasRuntimeClientId: !!process.env.OKTA_CLIENT_ID,
    hasClientSecret: !!process.env.OKTA_CLIENT_SECRET,
    clientSecretLength: process.env.OKTA_CLIENT_SECRET?.length || 0,
    hasIssuer: !!process.env.NEXT_PUBLIC_OKTA_ISSUER,
    issuer: process.env.NEXT_PUBLIC_OKTA_ISSUER || 'NOT SET',
    hasRuntimeIssuer: !!process.env.OKTA_ISSUER,
    runtimeIssuer: process.env.OKTA_ISSUER || 'NOT SET',
    hasDomain: !!process.env.NEXT_PUBLIC_OKTA_DOMAIN,
    domain: process.env.NEXT_PUBLIC_OKTA_DOMAIN || 'NOT SET',
    hasNextAuthSecret: !!process.env.NEXTAUTH_SECRET,
    hasNextAuthUrl: !!process.env.NEXTAUTH_URL,
    nextAuthUrl: process.env.NEXTAUTH_URL || 'NOT SET',
    hasApiUrl: !!process.env.NEXT_PUBLIC_API_URL,
    apiUrl: process.env.NEXT_PUBLIC_API_URL || 'NOT SET (will use localhost:8000)',
  });
}
