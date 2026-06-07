'use client';

import { useState } from 'react';
import { useAnimeReviews, useCreateReview, useRateAnime } from '@/hooks/use-queries';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Star, MessageSquare, ThumbsUp, Trash2 } from 'lucide-react'; // Added Trash2
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { formatDistanceToNow } from 'date-fns';
import { useAuthStore } from '@/store/auth-store';
import { toast } from 'sonner';
import { Card } from '@/components/ui/card';
import { cn } from '@/lib/utils'; // Ensure utility exists
import { motion, AnimatePresence } from 'framer-motion';

interface ReviewSectionProps {
    animeId: number;
}

export function ReviewSection({ animeId }: ReviewSectionProps) {
    const { user } = useAuthStore();
    const { data: reviewsData, isLoading } = useAnimeReviews(animeId);
    const { mutate: postReview, isPending: isPosting } = useCreateReview();
    const { mutate: rateAnime, isPending: isRating } = useRateAnime();

    const [content, setContent] = useState('');
    const [rating, setRating] = useState(0);
    const [hoverRating, setHoverRating] = useState(0);

    const handleSubmit = () => {
        if (!user) {
            toast.error('You must be logged in to review.');
            return;
        }
        if (rating === 0) {
            toast.error('Please select a rating score.');
            return;
        }
        if (content.length < 10) {
            toast.error('Review must be at least 10 characters.');
            return;
        }

        // Optimistic update logic is complex, simpler to just invalidate query on success (handled in hook)
        // We call rateAnime AND postReview? Backend might handle rate inside review, but typically they are separate or linked.
        // API client has `rateAnime` and `createReview` taking a rating.
        // Let's assume creating a review also updates the rating, or we do both.
        // `api.createReview` takes (id, content, rating). So it does both.

        postReview({ id: animeId, content, rating }, {
            onSuccess: () => {
                toast.success('Review published! Neural pathways updated.');
                setContent('');
                setRating(0);
            },
            onError: (err: any) => {
                toast.error('Failed to publish review.');
                console.error(err);
            }
        });
    };

    const handleRate = (score: number) => {
        if (!user) {
            toast.error('Login to rate.');
            return;
        }
        rateAnime({ id: animeId, score }, {
            onSuccess: () => {
                toast.success(`Rated ${score}/10`);
                setRating(score);
            }
        });
    }

    return (
        <div className="space-y-8">
            <h3 className="text-2xl font-bold font-heading flex items-center gap-2">
                <MessageSquare className="text-primary" />
                Community Resonance
            </h3>

            {/* Write Review Box */}
            <Card className="p-6 bg-white/5 border-white/10 backdrop-blur-sm">
                {!user ? (
                    <div className="text-center py-4 text-muted-foreground">
                        <Button variant="link" className="text-primary p-0" onClick={() => window.location.href = '/login'}>Log in</Button> to contribute your resonance.
                    </div>
                ) : (
                    <div className="space-y-4">
                        <div className="flex items-center gap-4">
                            <span className="text-sm font-bold uppercase tracking-wider text-muted-foreground">Your Sync Rate:</span>
                            <div className="flex gap-1">
                                {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((star) => (
                                    <button
                                        key={star}
                                        type="button"
                                        onMouseEnter={() => setHoverRating(star)}
                                        onMouseLeave={() => setHoverRating(0)}
                                        onClick={() => setRating(star)}
                                        className="transition-transform hover:scale-110 focus:outline-none"
                                    >
                                        <Star
                                            className={cn(
                                                "w-5 h-5 transition-colors",
                                                (hoverRating || rating) >= star ? "fill-primary text-primary" : "text-white/20"
                                            )}
                                        />
                                    </button>
                                ))}
                            </div>
                            <span className="text-lg font-bold text-primary ml-2">
                                {(hoverRating || rating) > 0 ? (hoverRating || rating) : '-'}
                            </span>
                        </div>

                        <Textarea
                            placeholder="Share your analysis... What vibes did you detect?"
                            className="bg-black/20 border-white/10 resize-none min-h-[100px]"
                            value={content}
                            onChange={(e) => setContent(e.target.value)}
                        />

                        <div className="flex justify-end">
                            <Button onClick={handleSubmit} disabled={isPosting}>
                                {isPosting ? 'Broadcasting...' : 'Broadcast Review'}
                            </Button>
                        </div>
                    </div>
                )}
            </Card>

            {/* Reviews List */}
            <div className="space-y-4">
                {isLoading ? (
                    <div className="space-y-4">
                        {[1, 2, 3].map((i) => <div key={i} className="h-32 bg-white/5 animate-pulse rounded-xl" />)}
                    </div>
                ) : reviewsData?.items?.length === 0 ? (
                    <div className="text-center py-12 text-muted-foreground">
                        No signals detected yet. Be the first to resonate.
                    </div>
                ) : (
                    <div className="space-y-4">
                        <AnimatePresence>
                            {reviewsData?.items?.map((review: any) => (
                                <motion.div
                                    key={review.id}
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, scale: 0.95 }}
                                    className="group relative overflow-hidden rounded-xl border border-white/10 bg-black/20 p-6 transition-colors hover:bg-white/5"
                                >
                                    <div className="flex items-start gap-4">
                                        <Avatar className="h-10 w-10 border border-white/10">
                                            <AvatarImage src={review.user?.avatar_url} />
                                            <AvatarFallback>{review.user?.username?.[0]?.toUpperCase() || '?'}</AvatarFallback>
                                        </Avatar>
                                        <div className="flex-1 space-y-2">
                                            <div className="flex items-center justify-between">
                                                <div>
                                                    <span className="font-bold text-white">{review.user?.display_name || review.user?.username || 'Anonymous'}</span>
                                                    <span className="text-xs text-muted-foreground ml-2">
                                                        {review.created_at ? formatDistanceToNow(new Date(review.created_at), { addSuffix: true }) : 'Just now'}
                                                    </span>
                                                </div>
                                                <div className="flex items-center gap-1 bg-primary/10 px-2 py-1 rounded text-xs font-bold text-primary">
                                                    <Star className="w-3 h-3 fill-primary" />
                                                    {review.rating}/10
                                                </div>
                                            </div>
                                            <p className="text-muted-foreground leading-relaxed text-sm">
                                                {review.content}
                                            </p>
                                            <div className="flex items-center gap-4 pt-2">
                                                <button className="flex items-center gap-1 text-xs text-muted-foreground hover:text-white transition-colors">
                                                    <ThumbsUp className="w-3 h-3" />
                                                    {review.likes || 0} Helpful
                                                </button>
                                                {user?.id === review.user?.id && (
                                                    <button className="text-xs text-red-400 hover:text-red-300 transition-colors flex items-center gap-1">
                                                        <Trash2 className="w-3 h-3" /> Delete
                                                    </button>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                </motion.div>
                            ))}
                        </AnimatePresence>
                    </div>
                )}
            </div>
        </div>
    );
}
