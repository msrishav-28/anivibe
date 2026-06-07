'use client';

import { useEffect, useState } from 'react';
import Image from 'next/image';
import { motion } from 'framer-motion';
import { Star, Play, Plus, Check, Share2, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ReviewSection } from '@/components/features/review-section';
import { GlitchText } from '@/components/ui/glitch-text';
import { AnimeCard } from '@/components/features/anime-card';
import { useWatchlistStore } from '@/store/watchlist-store';
import { WhyTooltip } from '@/components/features/why-tooltip';
import { useAnime, useSimilarAnime, useExplanation } from '@/hooks/use-queries';
import type { Anime } from '@/types';

interface AnimeDetailPageProps {
  params: { id: string };
}

export default function AnimeDetailPage({ params }: AnimeDetailPageProps) {
  // $10k Upgrade: React Query Hooks
  const { data: anime, isLoading: isAnimeLoading } = useAnime(parseInt(params.id));
  const { data: similarAnime = [] } = useSimilarAnime(parseInt(params.id));
  const { data: explanation } = useExplanation(parseInt(params.id));

  const { entries, addToWatchlist } = useWatchlistStore();

  const isInWatchlist = entries.some((entry) => entry.anime_id === parseInt(params.id));

  const handleAddToWatchlist = () => {
    if (anime) {
      addToWatchlist(anime.anime_id, 'plan_to_watch');
    }
  };

  if (isAnimeLoading || !anime) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="h-12 w-12 animate-spin rounded-full border-4 border-primary-500 border-t-transparent" />
          <p className="mt-4 text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      {/* Glass Pane Layout - Neo-Tokyo Pivot */}
      {/* 1. Background Layer (Blurred Poster) */}
      <div className="fixed inset-0 z-0">
        <Image
          src={anime.image_url}
          alt={anime.title}
          fill
          className="object-cover opacity-60 blur-3xl saturate-150"
          priority
        />
        <div className="absolute inset-0 bg-black/60" /> {/* Dimmer */}
      </div>

      {/* 2. Foreground Glass Sheet */}
      <div className="relative z-10 min-h-screen pt-[30vh]">
        <motion.div
          initial={{ y: 100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="min-h-[70vh] rounded-t-[3rem] border-t border-white/10 bg-black/80 backdrop-blur-md px-6 pt-12 pb-32 md:px-12"
        >
          <div className="container-custom max-w-5xl mx-auto">
            {/* Header Section */}
            <div className="flex flex-col md:flex-row gap-8 mb-12">
              {/* Poster Card (Floating) */}
              <motion.div
                className="relative -mt-32 h-[450px] w-[300px] flex-shrink-0 rounded-2xl overflow-hidden shadow-[0_0_50px_rgba(0,0,0,0.5)] border border-white/10 mx-auto md:mx-0"
                whileHover={{ scale: 1.02 }}
                transition={{ duration: 0.4 }}
              >
                <Image
                  src={anime.image_url}
                  alt={anime.title}
                  fill
                  className="object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent" />
              </motion.div>

              {/* Title & Actions */}
              <div className="flex-1 flex flex-col justify-end pt-4">
                <div className="mb-4 flex flex-wrap gap-2">
                  {anime.genres.map((genre) => (
                    <Badge key={genre} variant="secondary" className="bg-primary/10 text-primary border-primary/20 backdrop-blur-md">
                      {genre}
                    </Badge>
                  ))}
                </div>

                <GlitchText
                  text={anime.title}
                  as="h1"
                  className="text-4xl md:text-6xl text-white mb-2 leading-tight"
                />

                <div className="flex items-center gap-4 text-muted-foreground mb-8 font-mono text-sm">
                  <span>{anime.year}</span>
                  <span>•</span>
                  <span>{anime.type}</span>
                  <span>•</span>
                  <span>{anime.episodes || '?'} eps</span>
                  <span>•</span>
                  <span className="flex items-center text-yellow-400 gap-1">
                    <Star className="w-4 h-4 fill-current" />
                    {anime.score}
                  </span>
                </div>

                <div className="flex flex-wrap gap-4">
                  {anime.trailer_url && (
                    <Button
                      size="lg"
                      className="h-14 px-8 rounded-xl bg-white text-black hover:bg-white/90 font-bold tracking-wide shadow-glow"
                      onClick={() => window.open(anime.trailer_url, '_blank')}
                    >
                      <Play className="mr-2 h-5 w-5 fill-current" />
                      WATCH TRAILER
                    </Button>
                  )}
                  <Button
                    size="lg"
                    variant={isInWatchlist ? 'secondary' : 'secondary'}
                    className="h-14 px-6 rounded-xl border border-white/10 bg-white/5 hover:bg-white/10"
                    onClick={handleAddToWatchlist}
                  >
                    {isInWatchlist ? <Check className="mr-2 h-5 w-5" /> : <Plus className="mr-2 h-5 w-5" />}
                    {isInWatchlist ? 'In Library' : 'Add to List'}
                  </Button>
                  <Button size="icon" variant="ghost" className="h-14 w-14 rounded-xl border border-white/10 hover:bg-white/5">
                    <Share2 className="h-5 w-5" />
                  </Button>
                </div>
              </div>
            </div>

            {/* Content Tabs / Info */}
            <div className="mt-12">
              <Tabs defaultValue="overview" className="w-full">
                <TabsList className="bg-white/5 border border-white/10 mb-8 p-1 h-auto">
                  <TabsTrigger value="overview" className="data-[state=active]:bg-primary/20 data-[state=active]:text-primary px-6 py-2">Overview</TabsTrigger>
                  <TabsTrigger value="reviews" className="data-[state=active]:bg-primary/20 data-[state=active]:text-primary px-6 py-2">Reviews & Ratings</TabsTrigger>
                  <TabsTrigger value="characters" className="data-[state=active]:bg-primary/20 data-[state=active]:text-primary px-6 py-2" disabled>Characters</TabsTrigger>
                </TabsList>

                <TabsContent value="overview" className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                  <div className="grid md:grid-cols-[2fr_1fr] gap-12">
                    <div className="space-y-8">
                      <section>
                        <h3 className="text-xl font-heading mb-4 text-white/50 uppercase tracking-widest">Synopsis</h3>
                        <p className="text-lg leading-relaxed text-muted-foreground">
                          {anime.synopsis}
                        </p>
                      </section>

                      <section>
                        <div className="flex items-center justify-between mb-4">
                          <h3 className="text-xl font-heading text-white/50 uppercase tracking-widest">The Vibe</h3>
                          {explanation && (
                            <WhyTooltip
                              score={Math.round(explanation.score * 100)}
                              reason={explanation.reason}
                            />
                          )}
                        </div>

                        {explanation ? (
                          <div className="p-6 rounded-2xl bg-white/5 border border-white/5 backdrop-blur-sm group cursor-pointer transition-colors hover:bg-white/10"
                            onClick={() => document.querySelector<HTMLElement>('.explainability-trigger')?.click()}
                          >
                            <div className="flex items-center gap-4 mb-4">
                              <div className="h-12 w-12 rounded-full bg-primary/20 flex items-center justify-center text-primary shadow-[0_0_15px_rgba(139,92,246,0.4)] group-hover:scale-110 transition-transform">
                                <Sparkles className="w-6 h-6" />
                              </div>
                              <div>
                                <div className="text-white font-bold text-lg">{Math.round(explanation.score * 100)}% Match</div>
                                <div className="text-sm text-muted-foreground">Based on your taste profile</div>
                              </div>
                            </div>
                            <p className="text-sm text-white/70 italic border-l-2 border-primary/30 pl-4">
                              &quot;{explanation.reason}&quot;
                            </p>
                          </div>
                        ) : (
                          <div className="p-6 rounded-2xl bg-white/5 border border-white/5 opacity-50">
                            <p className="text-sm text-muted-foreground italic">
                              AI analysis pending...
                            </p>
                          </div>
                        )}
                      </section>
                    </div>

                    {/* Sidebar Info (Studio/etc) */}
                    <div className="space-y-6">
                      <div className="p-6 rounded-2xl bg-black/40 border border-white/5">
                        <h4 className="text-sm font-bold text-white mb-4 uppercase tracking-wider">Information</h4>
                        <div className="space-y-4 text-sm">
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Studio</span>
                            <span className="text-white">{anime.studios?.[0] || 'Unknown'}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Status</span>
                            <span className="text-white">{anime.status}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Duration</span>
                            <span className="text-white">{anime.duration}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Rating</span>
                            <span className="text-white">{anime.rating}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="reviews" className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                  <ReviewSection animeId={anime.anime_id} />
                </TabsContent>
              </Tabs>
            </div>

            {/* Similar Anime Section (Optional, could just use Recommendations) */}
            <div className="mt-16">
              <h3 className="text-xl font-heading mb-8 text-white uppercase tracking-widest">Similar Vibes</h3>
              <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
                {similarAnime.map((item) => (
                  <AnimeCard key={item.anime_id} anime={item} variant="grid" />
                ))}
              </div>
            </div>

          </div>
        </motion.div>
      </div>
    </div>
  );
}
