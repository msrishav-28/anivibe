'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Award, Zap, Terminal, Check } from 'lucide-react';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Card } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { useAuthStore } from '@/store/auth-store';
import { useWatchlistStore } from '@/store/watchlist-store';
import { useUserStats } from '@/hooks/use-queries';
import { GlitchText } from '@/components/ui/glitch-text';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ProfileEditor } from '@/components/features/profile-editor';
import dynamic from 'next/dynamic';

const ActivityHeatmap = dynamic(() => import('@/components/features/profile/activity-heatmap').then(mod => mod.ActivityHeatmap), {
  loading: () => <Skeleton className="h-[200px] w-full rounded-xl bg-white/5" />,
  ssr: false
});

const StatsRadar = dynamic(() => import('@/components/features/profile/stats-radar').then(mod => mod.StatsRadar), {
  loading: () => <Skeleton className="h-[300px] w-full rounded-xl bg-white/5" />,
  ssr: false
});

const MotionCard = motion(Card);

export default function ProfilePage() {
  const { user } = useAuthStore();
  const { entries } = useWatchlistStore();

  // $10k Upgrade: Use React Query Hook
  const { data: stats, isLoading } = useUserStats(user?.user_id);

  if (!user) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center space-y-4">
          <Terminal className="w-12 h-12 text-primary mx-auto animate-pulse" />
          <p className="text-muted-foreground font-mono">ACCESS DENIED. PLEASE AUTHENTICATE.</p>
        </div>
      </div>
    );
  }

  const watchingCount = entries.filter((e) => e.status === 'watching').length;
  const completedCount = entries.filter((e) => e.status === 'completed').length;

  // Create mock level based on entries count
  const level = Math.floor(entries.length / 5) + 1;
  const progressToNext = (entries.length % 5) * 20;

  return (
    <div className="min-h-screen pt-24 pb-20">
      <div className="container-custom">
        {/* Identity Header Card */}
        <MotionCard
          variant="holo"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="mb-12 p-8"
        >
          {/* Decorative scanning line */}
          <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-primary to-transparent opacity-50 animate-[scan_4s_linear_infinite]" />

          <div className="flex flex-col md:flex-row gap-8 items-center md:items-start">
            <div className="relative">
              <div className="absolute -inset-1 rounded-full bg-gradient-to-tr from-primary to-purple-500 blur opacity-70" />
              <Avatar className="h-32 w-32 border-2 border-white/20 relative z-10">
                <AvatarImage src={user.avatar_url} />
                <AvatarFallback className="text-4xl bg-black text-primary font-bold">
                  {user.username.slice(0, 2).toUpperCase()}
                </AvatarFallback>
              </Avatar>
              <div className="absolute bottom-0 right-0 z-20 bg-black border border-primary text-primary px-2 py-0.5 text-xs font-bold rounded-full">
                LVL {level}
              </div>
            </div>

            <div className="flex-1 text-center md:text-left space-y-4">
              <div>
                <GlitchText text={user.username} as="h1" className="text-4xl md:text-5xl font-bold text-white mb-2" />
                <p className="text-muted-foreground font-mono text-sm tracking-wider">
                  ID: {user.user_id.toString().padStart(6, '0')} • <span className="text-primary">NETRUNNER</span>
                </p>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-2xl">
                <div className="p-3 rounded-xl bg-white/5 border border-white/5">
                  <div className="text-muted-foreground text-xs uppercase tracking-wider mb-1">Anime</div>
                  <div className="text-2xl font-bold text-white">{entries.length}</div>
                </div>
                <div className="p-3 rounded-xl bg-white/5 border border-white/5">
                  <div className="text-muted-foreground text-xs uppercase tracking-wider mb-1">Hours</div>
                  <div className="text-2xl font-bold text-white">{stats?.total_watch_time ? Math.round(stats.total_watch_time / 60) : 0}</div>
                </div>
                <div className="p-3 rounded-xl bg-white/5 border border-white/5">
                  <div className="text-muted-foreground text-xs uppercase tracking-wider mb-1">Score</div>
                  <div className="text-2xl font-bold text-white">{stats?.average_rating?.toFixed(1) || '0.0'}</div>
                </div>
                <div className="p-3 rounded-xl bg-white/5 border border-white/5">
                  <div className="text-muted-foreground text-xs uppercase tracking-wider mb-1">Rank</div>
                  <div className="text-2xl font-bold text-white">#4201</div>
                </div>
              </div>
            </div>

            <div className="w-full md:w-64 space-y-2">
              <div className="flex justify-between text-xs text-muted-foreground uppercase font-bold">
                <span>Exp Progress</span>
                <span>{progressToNext}%</span>
              </div>
              <Progress value={progressToNext} className="h-2" />
              <p className="text-xs text-center text-white/40 italic">Next Level: Otaku Initiate</p>
            </div>
          </div>
        </MotionCard>

        <Tabs defaultValue="dashboard" className="space-y-8">
          <div className="flex items-center justify-between">
            <TabsList className="bg-white/5 border border-white/10">
              <TabsTrigger value="dashboard" className="text-xs uppercase tracking-wider">Dashboard</TabsTrigger>
              <TabsTrigger value="settings" className="text-xs uppercase tracking-wider">Settings</TabsTrigger>
            </TabsList>
          </div>

          <TabsContent value="dashboard" className="animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="grid lg:grid-cols-12 gap-8">
              {/* Left Column: Radar & Badges */}
              <div className="lg:col-span-4 space-y-8">
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.2 }}
                  className="rounded-2xl border border-white/10 bg-black/40 backdrop-blur-sm p-6"
                >
                  <h3 className="text-lg font-bold text-white mb-6 uppercase tracking-widest flex items-center gap-2">
                    <Zap className="w-4 h-4 text-yellow-400" />
                    Taste Profile
                  </h3>
                  <StatsRadar data={stats?.genre_distribution} />
                </motion.div>
              </div>

              {/* Right Column: Heatmap & Recent */}
              <div className="lg:col-span-8 space-y-8">
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                >
                  <h3 className="text-lg font-bold text-white mb-6 uppercase tracking-widest flex items-center gap-2">
                    <Terminal className="w-4 h-4 text-green-400" />
                    Neural Sync
                  </h3>
                  <ActivityHeatmap />
                </motion.div>

                <div className="grid md:grid-cols-2 gap-6">
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.5 }}
                    className="rounded-2xl border border-white/10 bg-black/40 backdrop-blur-sm p-6"
                  >
                    <h3 className="text-sm font-bold text-white/70 mb-4 uppercase">Watching Now</h3>
                    <div className="space-y-4">
                      {watchingCount === 0 && <p className="text-sm text-muted-foreground italic">No active streams.</p>}
                      {entries.filter(e => e.status === 'watching').slice(0, 3).map(entry => (
                        <div key={entry.entry_id} className="flex items-center gap-3 group cursor-pointer">
                          <div className="h-10 w-10 rounded bg-white/10 overflow-hidden relative">
                            {/* Ideally an image here */}
                            <div className="absolute inset-0 bg-primary/20" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="text-sm font-medium text-white truncate group-hover:text-primary transition-colors">{entry.anime?.title || 'Unknown Title'}</div>
                            <div className="text-xs text-muted-foreground">{entry.episodes_watched} / {entry.anime?.episodes || '?'} eps</div>
                          </div>
                          <Badge variant="outline" className="text-[10px] border-primary/20 text-primary">Active</Badge>
                        </div>
                      ))}
                    </div>
                  </motion.div>

                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.6 }}
                    className="rounded-2xl border border-white/10 bg-black/40 backdrop-blur-sm p-6"
                  >
                    <h3 className="text-sm font-bold text-white/70 mb-4 uppercase">Recently Completed</h3>
                    <div className="space-y-4">
                      {completedCount === 0 && <p className="text-sm text-muted-foreground italic">No data archived.</p>}
                      {entries.filter(e => e.status === 'completed').slice(0, 3).map(entry => (
                        <div key={entry.entry_id} className="flex items-center gap-3">
                          <div className="h-10 w-10 rounded bg-white/10 flex items-center justify-center text-success">
                            <Check className="w-5 h-5" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="text-sm font-medium text-white truncate">{entry.anime?.title}</div>
                            <div className="text-xs text-muted-foreground">Score: {entry.score || '-'}/10</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </motion.div>
                </div>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="settings" className="animate-in fade-in slide-in-from-bottom-4 duration-500">
            <ProfileEditor />
          </TabsContent>
        </Tabs>

      </div>
    </div>
  );
}
