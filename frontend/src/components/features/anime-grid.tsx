'use client';

import { useEffect } from 'react';
import { motion } from 'framer-motion';
import { useIntersectionObserver } from '@/hooks/use-intersection-observer';
import { AnimeCard } from './anime-card';
import { Skeleton } from '@/components/ui/skeleton';
import type { Anime } from '@/types';

// Interface update
interface AnimeGridProps {
  anime: Anime[];
  isLoading?: boolean;
  hasMore?: boolean;
  onLoadMore?: () => void;
  className?: string; // variant removed
}

export function AnimeGrid({
  anime,
  isLoading = false,
  hasMore = false,
  onLoadMore,
  className = '',
}: AnimeGridProps) {
  const [ref, inView] = useIntersectionObserver({
    threshold: 0.5,
  });

  useEffect(() => {
    if (inView && hasMore && onLoadMore && !isLoading) {
      onLoadMore();
    }
  }, [inView, hasMore, onLoadMore, isLoading]);

  if (anime.length === 0 && !isLoading) {
    return (
      <div className="flex min-h-[400px] items-center justify-center">
        <div className="text-center">
          <p className="text-lg text-muted-foreground">No anime found</p>
          <p className="text-sm text-muted-foreground">Try adjusting your filters</p>
        </div>
      </div>
    );
  }

  return (
    <div className={className}>
      <motion.div
        className='grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6'
        variants={{
          hidden: { opacity: 0 },
          show: {
            opacity: 1,
            transition: {
              staggerChildren: 0.05
            }
          }
        }}
        initial="hidden"
        animate="show"
      >
        {anime.map((item) => (
          <motion.div
            key={item.anime_id}
            variants={{
              hidden: { opacity: 0, y: 20 },
              show: { opacity: 1, y: 0 }
            }}
          >
            <AnimeCard anime={item} variant="grid" />
          </motion.div>
        ))}
      </motion.div>

      {/* Loading More Indicator */}
      {isLoading && (
        <div
          className='mt-8 grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6'
        >
          {Array.from({ length: 12 }).map((_, i) => (
            <Skeleton
              key={i}
              className='aspect-poster h-full'
            />
          ))}
        </div>
      )}

      {/* Infinite Scroll Trigger */}
      {hasMore && <div ref={ref} className="h-10" />}
    </div>
  );
}
