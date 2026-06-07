'use client';

import { usePersonalizedRecommendations } from '@/hooks/use-queries';
import { AnimeCard } from '@/components/features/anime-card';
import { Skeleton } from '@/components/ui/skeleton';
import { AlertCircle, Sparkles } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { useAuthStore } from '@/store/auth-store';

export function PersonalizedFeed() {
    const { user } = useAuthStore();
    const { data: recommendations, isLoading, error } = usePersonalizedRecommendations(12);

    if (!user) {
        return (
            <div className="text-center py-12 border border-white/10 rounded-xl bg-black/40">
                <p className="text-muted-foreground">Log in to see your personalized neural stream.</p>
            </div>
        );
    }

    if (isLoading) {
        return (
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
                {[...Array(4)].map((_, i) => (
                    <Skeleton key={i} className="h-[300px] rounded-xl bg-white/5" />
                ))}
            </div>
        );
    }

    if (error) {
        return (
            <Alert variant="destructive" className="bg-red-900/20 border-red-900/50 text-red-200">
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>Neural Link Severed</AlertTitle>
                <AlertDescription>
                    Could not generate recommendations. The model might be offline.
                </AlertDescription>
            </Alert>
        );
    }

    if (!recommendations || recommendations.length === 0) {
        return (
            <div className="text-center py-12 border border-white/10 rounded-xl bg-black/40">
                <Sparkles className="h-8 w-8 text-muted-foreground/50 mx-auto mb-3" />
                <p className="text-muted-foreground">Not enough data to calculate vibes inside the matrix yet. Rate some anime!</p>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center gap-2 mb-6">
                <Sparkles className="h-5 w-5 text-secondary" />
                <h2 className="text-2xl font-bold font-heading text-white">Recommended For You</h2>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                {recommendations.map((item: any) => (
                    // Supports both direct Anime object or Recommendation object with { anime: ... }
                    <AnimeCard
                        key={item.anime?.id || item.id}
                        anime={item.anime || item}
                        variant="compact" // Assuming compact variant exists or will fallback
                    />
                ))}
            </div>
        </div>
    );
}
