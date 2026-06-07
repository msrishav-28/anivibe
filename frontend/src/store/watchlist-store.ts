import { create } from 'zustand';
import type { WatchlistEntry } from '@/types';
import { api } from '@/lib/api-client';

interface WatchlistState {
  entries: WatchlistEntry[];
  isLoading: boolean;
  error: string | null;

  // Actions
  fetchWatchlist: (userId?: string, status?: string) => Promise<void>;
  addToWatchlist: (animeId: number, status: string) => Promise<void>;
  updateEntry: (entryId: number, data: Partial<WatchlistEntry>) => Promise<void>;
  removeFromWatchlist: (entryId: number) => Promise<void>;
  getEntryByAnimeId: (animeId: number) => WatchlistEntry | undefined;
  clearError: () => void;
}

export const useWatchlistStore = create<WatchlistState>((set, get) => ({
  entries: [],
  isLoading: false,
  error: null,

  fetchWatchlist: async (userId?: string, status?: string) => {
    set({ isLoading: true, error: null });
    try {
      const entries = await api.getWatchlist(userId, status);
      set({ entries, isLoading: false });
    } catch (error: any) {
      set({
        error: error.message || 'Failed to fetch watchlist',
        isLoading: false,
      });
    }
  },

  addToWatchlist: async (animeId: number, status: string) => {
    set({ isLoading: true, error: null });
    try {
      const entry = await api.addToWatchlist(animeId, status);
      set((state) => ({
        entries: [...state.entries, entry],
        isLoading: false,
      }));
    } catch (error: any) {
      set({
        error: error.message || 'Failed to add to watchlist',
        isLoading: false,
      });
      throw error;
    }
  },

  updateEntry: async (entryId: number, data: Partial<WatchlistEntry>) => {
    set({ isLoading: true, error: null });
    try {
      const updatedEntry = await api.updateWatchlistEntry(entryId, data);
      set((state) => ({
        entries: state.entries.map((entry) =>
          entry.entry_id === entryId ? updatedEntry : entry
        ),
        isLoading: false,
      }));
    } catch (error: any) {
      set({
        error: error.message || 'Failed to update entry',
        isLoading: false,
      });
      throw error;
    }
  },

  removeFromWatchlist: async (entryId: number) => {
    set({ isLoading: true, error: null });
    try {
      await api.removeFromWatchlist(entryId);
      set((state) => ({
        entries: state.entries.filter((entry) => entry.entry_id !== entryId),
        isLoading: false,
      }));
    } catch (error: any) {
      set({
        error: error.message || 'Failed to remove from watchlist',
        isLoading: false,
      });
      throw error;
    }
  },

  getEntryByAnimeId: (animeId: number) => {
    return get().entries.find((entry) => entry.anime_id === animeId);
  },

  clearError: () => {
    set({ error: null });
  },
}));
