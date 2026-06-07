import type { Metadata } from 'next';
import { Header } from '@/components/layout/header';
import { Footer } from '@/components/layout/footer';
import { BottomNav } from '@/components/layout/bottom-nav';
import { ErrorBoundary } from '@/components/error-boundary';
import { ToastProvider } from '@/components/toast-provider';
import { Providers } from '@/components/providers';
import { CinematicContainer } from '@/components/layout/cinematic-container';
import '@/styles/globals.css';

export const metadata: Metadata = {
  title: 'AniVibe - AI-Powered Anime Discovery',
  description:
    'Discover your next favorite anime with AI-powered recommendations, semantic search, and interactive visualizations.',
  keywords: ['anime', 'recommendations', 'AI', 'discovery', 'semantic search'],
  authors: [{ name: 'AniVibe Team' }],
  openGraph: {
    title: 'AniVibe - AI-Powered Anime Discovery',
    description: 'Discover your next favorite anime with AI',
    type: 'website',
  },
};

import { Outfit } from 'next/font/google';

const outfit = Outfit({
  subsets: ['latin'],
  variable: '--font-outfit',
  display: 'swap',
});

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`dark ${outfit.variable}`}>
      <head>
        <link href="https://api.fontshare.com/v2/css?f[]=clash-display@600,700,500&f[]=satoshi@900,700,500,400&display=swap" rel="stylesheet" />
      </head>
      <body className="font-sans text-foreground bg-background antialiased overflow-x-hidden selection:bg-primary-500/30 selection:text-white">
        <ErrorBoundary>
          <div className="relative flex min-h-screen flex-col">
            <Providers>
              <CinematicContainer>
                <Header />
                <main className="flex-1 relative z-10 pb-20 md:pb-0">{children}</main>
                <Footer />
                <BottomNav />
              </CinematicContainer>
            </Providers>
          </div>
          <ToastProvider />
        </ErrorBoundary>
      </body>
    </html>
  );
}
