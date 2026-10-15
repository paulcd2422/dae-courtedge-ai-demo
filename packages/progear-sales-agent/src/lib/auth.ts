import type { NextAuthOptions } from 'next-auth';
import OktaProvider from 'next-auth/providers/okta';

/**
 * Okta OIDC settings used by NextAuth (server-side only).
 *
 * Prefer the RUNTIME variables (OKTA_ISSUER / OKTA_CLIENT_ID), which are read
 * from the container environment / Azure App Settings when the server starts,
 * so they can be changed without rebuilding the image. Fall back to the
 * NEXT_PUBLIC_* variables, which Next.js inlines at BUILD time.
 *
 * OKTA_ISSUER must be the Org Authorization Server (https://your-org.okta.com),
 * NOT a custom authorization server URL (.../oauth2/aus...). The backend's
 * ID-JAG token exchange only accepts ID tokens issued by the Org AS.
 */
export const oktaIssuer =
  process.env.OKTA_ISSUER || process.env.NEXT_PUBLIC_OKTA_ISSUER || '';
export const oktaClientId =
  process.env.OKTA_CLIENT_ID || process.env.NEXT_PUBLIC_OKTA_CLIENT_ID || '';

export const authOptions: NextAuthOptions = {
  providers: [
    OktaProvider({
      clientId: oktaClientId,
      clientSecret: process.env.OKTA_CLIENT_SECRET || 'placeholder-for-pkce',
      issuer: oktaIssuer,
    }),
  ],
  pages: {
    signIn: '/auth/signin',
  },
  callbacks: {
    async jwt({ token, account }) {
      if (account) {
        token.accessToken = account.access_token;
        token.idToken = account.id_token;
      }
      return token;
    },
    async session({ session, token }) {
      session.accessToken = token.accessToken as string;
      session.idToken = token.idToken as string;
      session.user = {
        ...session.user,
        id: token.sub as string,
      };
      return session;
    },
  },
  secret: process.env.NEXTAUTH_SECRET,
  debug: true,
};
