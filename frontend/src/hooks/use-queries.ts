import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api-client';
import { Anime, User, UserStats } from '@/types';

// ==================== KEY CONFIG ====================
// Stale Time: 5 minutes (Data is considered fresh for 5 mins)
// Cache Time: 30 minutes (Unused data stays in memory)
const STALE_TIME = 1000 * 60 * 5;

export function useAnime(id: number) {
    return useQuery({
        queryKey: ['anime', id],
        queryFn: () => api.getAnime(id),
        staleTime: STALE_TIME,
        retry: 1, // Don't retry indefinitely if 404
    });
}

export function useSimilarAnime(id: number) {
    return useQuery({
        queryKey: ['anime', id, 'similar'],
        queryFn: async () => {
            const recommendations = await api.getSimilarAnime(id, 12);
            // Map recommendations to just the Anime object for the UI
            return recommendations.map(rec => rec.anime || rec);
        },
        staleTime: STALE_TIME,
    });
}

export function useUserStats(userId?: string) {
    return useQuery({
        queryKey: ['user', userId || 'me', 'stats'],
        queryFn: () => api.getUserStats(userId),
        staleTime: 1000 * 60 * 2, // Stats update slightly more often
        enabled: !!userId, // Only run if userId exists
    });
}

export function useAnimeReviews(animeId: number, page: number = 1) {
    return useQuery({
        queryKey: ['anime', animeId, 'reviews', page],
        queryFn: () => api.getAnimeReviews(animeId, page),
        staleTime: 1000 * 60, // Reviews update frequently
    });
}

export function useExplanation(animeId: number) {
    return useQuery({
        queryKey: ['anime', animeId, 'explanation'],
        queryFn: () => api.explainRecommendation(animeId),
        staleTime: 1000 * 60 * 60, // Explanations are relatively static
        retry: false, // Do not retry if 404/500 (just don't show tooltip)
    });
}

export function useAnalytics() {
    return useQuery({
        queryKey: ['analytics'],
        queryFn: () => ({ /* mock analytics */ }),
        enabled: false
    });
}

export function usePersonalizedRecommendations(limit: number = 20) {
    return useQuery({
        queryKey: ['recommendations', 'personalized'],
        queryFn: () => api.getPersonalized(limit),
        staleTime: 1000 * 60 * 15,
        retry: false
    });
}

// Mutations usually don't need a custom hook wrapper if they are simple, 
// but for consistency and error handling, we can create them or use useMutation directly in components.
// Here I'll export them to keep api calls centralized.

import { useMutation, useQueryClient } from '@tanstack/react-query';

export function useImageSearch() {
    return useMutation({
        mutationFn: (file: File) => api.imageSearch(file),
    });
}

export function useRateAnime() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: ({ id, score }: { id: number; score: number }) => api.rateAnime(id, score),
        onSuccess: (_, { id }) => {
            queryClient.invalidateQueries({ queryKey: ['anime', id] });
            queryClient.invalidateQueries({ queryKey: ['user', 'me', 'stats'] });
        },
    });
}

export function useCreateReview() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: ({ id, content, rating }: { id: number; content: string; rating: number }) =>
            api.createReview(id, content, rating),
        onSuccess: (_, { id }) => {
            queryClient.invalidateQueries({ queryKey: ['anime', id, 'reviews'] });
        },
    });
}

export function useUpdateProfile() {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (data: Parameters<typeof api.updateProfile>[0]) => api.updateProfile(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['user', 'me'] });
        },
    });
}
