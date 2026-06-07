'use client';

import * as React from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion';
import { Heart, Bookmark, Info, Play, Star } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import type { Anime } from '@/types';
import { genreColors } from '@/config/tokens';

export interface AnimeCardProps {
  anime: Anime;
  variant?: 'grid' | 'compact' | 'featured';
  showStats?: boolean;
  onHover?: 'expand' | 'glow' | 'lift';
  contextMenu?: string[];
  onClick?: () => void;
  className?: string;
}

export function AnimeCard({
  anime,
  variant = 'grid',
  showStats = true,
  onHover = 'lift',
  contextMenu = ['Add to List', 'Similar', 'Share'],
  onClick,
  className,
}: AnimeCardProps) {
  const [isHovered, setIsHovered] = React.useState(false);
  const [isFavorite, setIsFavorite] = React.useState(false);
  const [isBookmarked, setIsBookmarked] = React.useState(false);

  const handleFavorite = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsFavorite(!isFavorite);
  };

  const handleBookmark = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsBookmarked(!isBookmarked);
  };

  // List variant removed for Neo-Tokyo pivot

  // Holographic physics
  const x = useMotionValue(0);
  const y = useMotionValue(0);

  // Smooth out the mouse movement
  const mouseX = useSpring(x, { stiffness: 500, damping: 100 });
  const mouseY = useSpring(y, { stiffness: 500, damping: 100 });

  function onMouseMove({ currentTarget, clientX, clientY }: React.MouseEvent) {
    const { left, top, width, height } = currentTarget.getBoundingClientRect();
    x.set((clientX - left) / width - 0.5);
    y.set((clientY - top) / height - 0.5);
  }

  const rotateX = useTransform(mouseY, [-0.5, 0.5], [7, -7]);
  const rotateY = useTransform(mouseX, [-0.5, 0.5], [-7, 7]);
  const sheenX = useTransform(mouseX, [-0.5, 0.5], ["0%", "200%"]);

  const cardVariants = {
    initial: { scale: 1 },
    hover:
      onHover === 'lift'
        ? { scale: 1.05 }
        : onHover === 'expand'
          ? { scale: 1.05 }
          : { scale: 1 },
  };

  return (
    <motion.div
      initial="initial"
      whileHover="hover"
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
      variants={cardVariants}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      onMouseMove={onMouseMove}
      style={{
        rotateX: isHovered ? rotateX : 0,
        rotateY: isHovered ? rotateY : 0,
        transformStyle: 'preserve-3d',
      }}
      className={cn(
        'group relative overflow-hidden rounded-lg border border-border bg-card transition-all perspective-1000',
        onHover === 'glow' && 'hover:shadow-glow',
        variant === 'featured' ? 'aspect-[2/3]' : 'aspect-poster',
        className
      )}
    >
      <Link href={`/anime/${anime.anime_id}`} onClick={() => onClick?.()}>
        <div className="relative h-full w-full">
          {/* Poster Image */}
          <Image
            src={anime.image_url}
            alt={anime.title}
            fill
            className={cn(
              'object-cover transition-transform duration-500',
              isHovered && 'scale-105'
            )}
            sizes="(max-width: 768px) 50vw, 25vw"
          />

          {/* Gradient Overlay - Always visible for text contrast */}
          <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent opacity-60 group-hover:opacity-90 transition-opacity duration-300" />

          {/* Holographic Sheen */}
          <motion.div
            className="absolute inset-0 z-10 opacity-0 group-hover:opacity-40 pointer-events-none mix-blend-overlay"
            style={{
              background: 'linear-gradient(105deg, transparent 20%, rgba(255,255,255,0.8) 40%, rgba(139,92,246,0.6) 45%, transparent 60%)',
              backgroundSize: '200% 100%',
              backgroundPositionX: sheenX,
            }}
          />

          {/* Genre Badges (Top Right) */}
          <div className="absolute right-2 top-2 flex flex-col gap-1">
            {anime.genres.slice(0, 2).map((genre) => (
              <motion.div
                key={genre}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 }}
              >
                <Badge
                  className="glassmorphism text-xs"
                  style={{
                    backgroundColor: genreColors[genre] + '40',
                    color: 'white',
                    backdropFilter: 'blur(8px)',
                  }}
                >
                  {genre}
                </Badge>
              </motion.div>
            ))}
          </div>

          {/* Rating (Bottom Left) */}
          {showStats && (
            <div className="absolute bottom-2 left-2 flex items-center gap-1 rounded-md bg-black/60 px-2 py-1 backdrop-blur-sm">
              <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
              <span className="text-sm font-semibold text-white">
                {anime.score.toFixed(1)}
              </span>
            </div>
          )}

          {/* Quick Actions (Bottom Right) */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={isHovered ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
            transition={{ delay: 0.2 }}
            className="absolute bottom-2 right-2 flex gap-1"
          >
            <Button
              size="icon"
              variant="secondary"
              className="h-8 w-8 bg-white/90 hover:bg-white"
              onClick={handleFavorite}
            >
              <Heart
                className={cn(
                  'h-4 w-4',
                  isFavorite ? 'fill-red-500 text-red-500' : 'text-gray-700'
                )}
              />
            </Button>
            <Button
              size="icon"
              variant="secondary"
              className="h-8 w-8 bg-white/90 hover:bg-white"
              onClick={handleBookmark}
            >
              <Bookmark
                className={cn(
                  'h-4 w-4',
                  isBookmarked ? 'fill-primary-500 text-primary-500' : 'text-gray-700'
                )}
              />
            </Button>
            {contextMenu && contextMenu.length > 0 && (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    size="icon"
                    variant="secondary"
                    className="h-8 w-8 bg-white/90 hover:bg-white"
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                    }}
                  >
                    <Info className="h-4 w-4 text-gray-700" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                  {contextMenu.map((item) => (
                    <DropdownMenuItem
                      key={item}
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                      }}
                    >
                      {item}
                    </DropdownMenuItem>
                  ))}
                </DropdownMenuContent>
              </DropdownMenu>
            )}
          </motion.div>

          {/* Title Overlay (Bottom) */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={isHovered ? { opacity: 1, y: 0 } : { opacity: 0, y: 10 }}
            transition={{ delay: 0.1 }}
            className="absolute bottom-0 left-0 right-0 p-3"
          >
            <h3 className="line-clamp-2 text-sm font-semibold text-white">
              {anime.title}
            </h3>
            <div className="mt-1 flex items-center gap-2 text-xs text-white/80">
              <span>{anime.type}</span>
              <span>•</span>
              <span>{anime.year}</span>
              {anime.episodes && (
                <>
                  <span>•</span>
                  <span>{anime.episodes} eps</span>
                </>
              )}
            </div>
          </motion.div>

          {/* Play Button (Center on Hover) */}
          {anime.trailer_url && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={
                isHovered
                  ? { opacity: 1, scale: 1 }
                  : { opacity: 0, scale: 0.8 }
              }
              transition={{ delay: 0.15 }}
              className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2"
            >
              <Button
                size="icon"
                className="h-12 w-12 rounded-full bg-primary-500/90 hover:bg-primary-600"
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  window.open(anime.trailer_url, '_blank');
                }}
              >
                <Play className="h-6 w-6 fill-white text-white" />
              </Button>
            </motion.div>
          )}
        </div>
      </Link>
    </motion.div>
  );
}
