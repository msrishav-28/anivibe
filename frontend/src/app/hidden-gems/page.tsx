'use client';

import { useState, useEffect, useCallback } from 'react';
import { HiddenGemCard } from '@/components/features/hidden-gem-card';
import { Card, CardContent } from '@/components/ui/card';
// Slider removed
import { Button } from '@/components/ui/button';
import { Gem, Sparkles } from 'lucide-react';
import { api } from '@/lib/api-client';
import type { Anime } from '@/types';

export default function HiddenGemsPage() {
  const [gems, setGems] = useState<Anime[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [minScore, setMinScore] = useState([7.5]);
  const [maxPopularity, setMaxPopularity] = useState([10000]);

  // Track applied filters separately to avoid re-fetching while dragging sliders
  const [activeFilters, setActiveFilters] = useState({
    minScore: 7.5,
    maxPopularity: 10000
  });

  const loadHiddenGems = useCallback(async () => {
    setIsLoading(true);
    try {
      const results = await api.getHiddenGems({
        min_score: activeFilters.minScore,
        max_popularity: activeFilters.maxPopularity,
        top_k: 24,
      });
      setGems(results);
    } catch (error) {
      console.error('Failed to load hidden gems:', error);
    } finally {
      setIsLoading(false);
    }
  }, [activeFilters]);

  useEffect(() => {
    loadHiddenGems();
  }, [loadHiddenGems]);

  const handleFiltersApply = () => {
    setActiveFilters({
      minScore: minScore[0] ?? 7.5,
      maxPopularity: maxPopularity[0] ?? 10000
    });
  };

  return (
    <div className="min-h-screen">
      <div className="container-custom py-8">
        {/* Header */}
        <div className="mb-8 text-center">
          <div className="mb-4 flex items-center justify-center gap-3">
            <Gem className="h-10 w-10 text-primary-500" />
            <h1 className="text-4xl font-bold">Hidden Gems</h1>
            <Sparkles className="h-10 w-10 text-accent-pink" />
          </div>
          <p className="text-lg text-muted-foreground">
            Discover high-quality anime that flew under the radar
          </p>
        </div>

        {/* Filters */}
        <Card className="mb-8 border-white/10 bg-black/40 backdrop-blur-md">
          <CardContent className="p-6">
            <div className="grid gap-6 md:grid-cols-2">
              <div>
                <label className="mb-4 block text-sm font-medium text-white">
                  Minimum Score: {(minScore[0] ?? 7.5).toFixed(1)}
                </label>
                <div className="relative">
                  <input
                    type="range"
                    min="6"
                    max="9"
                    step="0.1"
                    value={minScore[0]}
                    onChange={(e) => setMinScore([parseFloat(e.target.value)])}
                    className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer accent-primary-500 hover:accent-primary-400 transition-all focus:outline-none focus:ring-2 focus:ring-primary-500/50"
                  />
                  <div className="mt-2 flex justify-between text-xs text-muted-foreground">
                    <span>6.0</span>
                    <span>9.0</span>
                  </div>
                </div>
              </div>

              <div>
                <label className="mb-4 block text-sm font-medium text-white">
                  Max Popularity Rank: {(maxPopularity[0] ?? 10000).toLocaleString()}
                </label>
                <div className="relative">
                  <input
                    type="range"
                    min="1000"
                    max="20000"
                    step="1000"
                    value={maxPopularity[0]}
                    onChange={(e) => setMaxPopularity([parseFloat(e.target.value)])}
                    className="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer accent-secondary hover:accent-secondary/80 transition-all focus:outline-none focus:ring-2 focus:ring-secondary/50"
                  />
                  <div className="mt-2 flex justify-between text-xs text-muted-foreground">
                    <span>1k</span>
                    <span>20k</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-6 text-center">
              <Button onClick={handleFiltersApply}>
                Apply Filters
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Results */}
        {isLoading ? (
          <div className="text-center py-12">
            <div className="h-12 w-12 animate-spin rounded-full border-4 border-primary-500 border-t-transparent mx-auto" />
            <p className="mt-4 text-muted-foreground">Discovering hidden gems...</p>
          </div>
        ) : gems.length > 0 ? (
          <>
            <div className="mb-6">
              <h2 className="text-2xl font-bold">
                {gems.length} Hidden Gems Found
              </h2>
              <p className="text-muted-foreground">
                High-quality anime with less than {(maxPopularity[0] ?? 10000).toLocaleString()} members
              </p>
            </div>

            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {gems.map((anime) => (
                <HiddenGemCard
                  key={anime.anime_id}
                  anime={anime}
                  reason={`Score: ${anime.score} • Members: ${anime.popularity || 'Low'}`}
                />
              ))}
            </div>
          </>
        ) : (
          <Card>
            <CardContent className="py-12 text-center">
              <p className="text-lg text-muted-foreground">
                No hidden gems found with these criteria. Try adjusting the filters!
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
