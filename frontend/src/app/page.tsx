'use client';

import Link from 'next/link';
import { Search, Sparkles, Globe, Play } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { GlitchText } from '@/components/ui/glitch-text';
import { Card, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { motion } from 'framer-motion';
import { VibeTuner } from '@/components/features/vibe-tuner';
import { PersonalizedFeed } from '@/components/features/personalized-feed';

export default function HomePage() {



  return (
    <div className="flex flex-col min-h-screen relative overflow-hidden">
      {/* Hero Section */}
      <section className="relative py-24 md:py-40 flex flex-col items-center justify-center text-center px-4 overflow-hidden">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="relative z-10 max-w-5xl mx-auto"
        >
          <Badge className="mb-6 glassmorphism border-primary/50 text-white/90 px-4 py-2 hover:bg-primary/20 transition-colors cursor-default" variant="secondary">
            <Sparkles className="mr-2 h-4 w-4 text-secondary-DEFAULT" />
            <span className="tracking-wide">AI-POWERED DISCOVERY v2.0</span>
          </Badge>

          <div className="mb-8">
            <GlitchText
              text="FIND YOUR ANIME VIBE"
              as="h1"
              className="text-6xl md:text-8xl text-transparent bg-clip-text bg-gradient-to-r from-primary-400 via-secondary to-primary-400 animate-gradient-x"
            />
          </div>

          <p className="mb-12 text-xl md:text-2xl text-muted-foreground/80 max-w-3xl mx-auto font-sans leading-relaxed">
            Stop searching by genre. Start discovering by <span className="text-white font-medium">emotion</span>.
            Our AI analyzes visual style, atmosphere, and storytelling to find your perfect match.
          </p>

          {/* Vibe Tuner (Search Bar) */}
          <VibeTuner />
        </motion.div>
      </section>

      {/* Personalized Feed (Only visible if logged in, handled by component) */}
      <section className="container-custom relative z-20 -mt-12 mb-24">
        <PersonalizedFeed />
      </section>

      {/* Features Grid */}
      <section className="py-24 relative z-10">
        <div className="container-custom">
          <div className="mb-16 text-center max-w-3xl mx-auto">
            <h2 className="mb-4 text-4xl font-heading font-bold text-white tracking-tight">
              NEURAL <span className="text-secondary">FEATURES</span>
            </h2>
            <p className="text-lg text-muted-foreground font-sans">
              Advanced tools designed for the modern anime connoisseur.
            </p>
          </div>

          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            <Card variant="holo">
              <CardHeader>
                <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4 text-primary border border-primary/20 shadow-[0_0_15px_rgba(139,92,246,0.2)]">
                  <Search className="h-6 w-6" />
                </div>
                <CardTitle className="text-white">Semantic Vibe Search</CardTitle>
                <CardDescription>
                  Forget keywords. Describe scenes, feelings, or art styles. Our AI understands "lonely rainy city lights"
                  better than any tag system.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card variant="holo">
              <CardHeader>
                <div className="h-12 w-12 rounded-lg bg-secondary/10 flex items-center justify-center mb-4 text-secondary border border-secondary/20 shadow-[0_0_15px_rgba(6,182,212,0.2)]">
                  <Sparkles className="h-6 w-6" />
                </div>
                <CardTitle className="text-white">Explainable AI</CardTitle>
                <CardDescription>
                  We don't just recommend. We tell you why. "98% Match because you enjoy High-Octane Action and Cyberpunk Aesthetics."
                </CardDescription>
              </CardHeader>
            </Card>

            <Card variant="holo">
              <CardHeader>
                <div className="h-12 w-12 rounded-lg bg-pink-500/10 flex items-center justify-center mb-4 text-pink-500 border border-pink-500/20 shadow-[0_0_15px_rgba(236,72,153,0.2)]">
                  <Globe className="h-6 w-6" />
                </div>
                <CardTitle className="text-white">Weeb Cred</CardTitle>
                <CardDescription>
                  Gamified tracking with GitHub-style heatmaps. Earn badges like "Shonen King" or "Isekai Survivor" based on your watch history.
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      {/* Stats / Tech Section */}
      <section className="py-24 border-y border-white/5 bg-black/40 backdrop-blur-sm relative z-10">
        <div className="container-custom">
          <div className="grid grid-cols-2 gap-12 md:grid-cols-4">
            <div className="text-center group cursor-default">
              <div className="mb-2 text-5xl font-heading font-bold text-transparent bg-clip-text bg-gradient-to-b from-white to-white/50 group-hover:scale-110 transition-transform duration-300">26k+</div>
              <div className="text-sm font-mono text-primary tracking-widest uppercase">Titles Indexed</div>
            </div>
            <div className="text-center group cursor-default">
              <div className="mb-2 text-5xl font-heading font-bold text-transparent bg-clip-text bg-gradient-to-b from-white to-white/50 group-hover:scale-110 transition-transform duration-300">10+</div>
              <div className="text-sm font-mono text-secondary tracking-widest uppercase">ML Models</div>
            </div>
            <div className="text-center group cursor-default">
              <div className="mb-2 text-5xl font-heading font-bold text-transparent bg-clip-text bg-gradient-to-b from-white to-white/50 group-hover:scale-110 transition-transform duration-300">98%</div>
              <div className="text-sm font-mono text-success tracking-widest uppercase">Accuracy</div>
            </div>
            <div className="text-center group cursor-default">
              <div className="mb-2 text-5xl font-heading font-bold text-transparent bg-clip-text bg-gradient-to-b from-white to-white/50 group-hover:scale-110 transition-transform duration-300">0.2s</div>
              <div className="text-sm font-mono text-pink-500 tracking-widest uppercase">Latency</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-32 relative z-10">
        <div className="container-custom">
          <div className="relative rounded-3xl overflow-hidden border border-white/10 p-12 md:p-24 text-center bg-black/60 shadow-2xl">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-primary to-transparent opacity-50" />

            <h2 className="text-4xl md:text-5xl font-heading font-bold mb-8 text-white">
              Ready to <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-secondary">Ascend?</span>
            </h2>
            <p className="text-xl text-muted-foreground mb-12 max-w-2xl mx-auto">
              Join the beta. Experience the future of anime discovery with zero compromise.
            </p>

            <div className="flex flex-wrap justify-center gap-6">
              <Button size="lg" variant="primary" className="h-14 px-10 text-lg shadow-glow-lg" asChild>
                <Link href="/signup">
                  Get Started Free <Play className="ml-2 h-4 w-4 fill-current" />
                </Link>
              </Button>
              <Button size="lg" variant="ghost" className="h-14 px-10 text-lg" asChild>
                <Link href="/search">Browse Collection</Link>
              </Button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
