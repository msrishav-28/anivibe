import axios, { AxiosError } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance
const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Add auth token
client.interceptors.request.use(
  (config) => {
    // No explicit token header needed - cookies are sent automatically
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - Handle errors globally
client.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Token expired, redirect to login
      // localStorage.removeItem('auth_token'); // Removed
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API methods
export const api = {
  // ==================== AUTH ====================
  login: async (email: string, password: string) => {
    const response = await client.post('/auth/login', { email, password });
    // Token is now in HttpOnly cookie
    return response.data;
  },

  register: async (data: {
    username: string;
    email: string;
    password: string;
    display_name?: string;
  }) => {
    const response = await client.post('/auth/register', data);
    return response.data;
  },

  logout: async () => {
    // localStorage.removeItem('auth_token'); // Removed
    await client.post('/auth/logout');
  },

  getCurrentUser: async () => {
    const response = await client.get('/users/me');
    return response.data;
  },

  // ==================== ANIME ====================
  getAnime: async (id: number) => {
    const response = await client.get(`/anime/${id}`);
    return response.data;
  },

  searchAnime: async (query: string, page = 1, limit = 20) => {
    const response = await client.get('/anime/search', {
      params: { q: query, page, limit },
    });
    return response.data;
  },

  getTrendingAnime: async (limit = 20) => {
    const response = await client.get('/anime/trending', {
      params: { limit },
    });
    return response.data;
  },

  getPopularAnime: async (limit = 20) => {
    const response = await client.get('/anime/popular', {
      params: { limit },
    });
    return response.data;
  },

  // ==================== SEARCH ====================
  semanticSearch: async (query: string, limit = 20) => {
    const response = await client.post('/search/semantic', {
      query,
      limit,
    });
    return response.data;
  },

  imageSearch: async (imageFile: File, limit = 20) => {
    const formData = new FormData();
    formData.append('image', imageFile);
    formData.append('limit', limit.toString());

    const response = await client.post('/search/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // ==================== RECOMMENDATIONS ====================
  getRecommendations: async (params?: {
    user_id?: string;
    limit?: number;
    strategy?: 'hybrid' | 'collaborative' | 'content' | 'gnn' | 'bert4rec';
  }) => {
    const response = await client.get('/recommendations', { params });
    return response.data;
  },

  getSimilarAnime: async (animeId: number, limit = 12) => {
    const response = await client.get(`/recommendations/similar/${animeId}`, {
      params: { limit },
    });
    return response.data;
  },

  getPersonalized: async (limit = 20) => {
    // Backend expects POST with top_k
    const response = await client.post('/recommendations/personalized', {
      top_k: limit,
      method: 'hybrid'
    });
    return response.data;
  },

  getHiddenGems: async (limit = 20) => {
    // Backend expects POST with top_k
    const response = await client.post('/recommendations/hidden-gems', {
      top_k: limit
    });
    return response.data;
  },

  // ==================== EXPLAINABILITY ====================
  explainRecommendation: async (animeId: number, method?: 'shap' | 'lime') => {
    const response = await client.get(`/explain/${animeId}`, {
      params: { method },
    });
    return response.data;
  },

  // ==================== RATINGS ====================
  rateAnime: async (animeId: number, score: number) => {
    const response = await client.post('/ratings', {
      anime_id: animeId,
      score,
    });
    return response.data;
  },

  getUserRating: async (animeId: number) => {
    const response = await client.get(`/ratings/anime/${animeId}`);
    return response.data;
  },

  deleteRating: async (animeId: number) => {
    const response = await client.delete(`/ratings/anime/${animeId}`);
    return response.data;
  },

  // ==================== REVIEWS ====================
  getAnimeReviews: async (animeId: number, page = 1, limit = 10) => {
    const response = await client.get(`/anime/${animeId}/reviews`, {
      params: { page, limit },
    });
    return response.data;
  },

  createReview: async (animeId: number, content: string, rating: number) => {
    const response = await client.post('/reviews', {
      anime_id: animeId,
      content,
      rating,
    });
    return response.data;
  },

  updateReview: async (reviewId: number, content: string, rating: number) => {
    const response = await client.put(`/reviews/${reviewId}`, {
      content,
      rating,
    });
    return response.data;
  },

  deleteReview: async (reviewId: number) => {
    const response = await client.delete(`/reviews/${reviewId}`);
    return response.data;
  },

  likeReview: async (reviewId: number) => {
    const response = await client.post(`/reviews/${reviewId}/like`);
    return response.data;
  },

  // ==================== WATCHLIST ====================
  getWatchlist: async (status?: 'watching' | 'completed' | 'plan_to_watch' | 'dropped') => {
    const response = await client.get('/watchlist', {
      params: { status },
    });
    return response.data;
  },

  addToWatchlist: async (animeId: number, status: string) => {
    const response = await client.post('/watchlist', {
      anime_id: animeId,
      status,
    });
    return response.data;
  },

  updateWatchlistStatus: async (animeId: number, status: string, progress?: number) => {
    const response = await client.put(`/watchlist/${animeId}`, {
      status,
      progress,
    });
    return response.data;
  },

  removeFromWatchlist: async (animeId: number) => {
    const response = await client.delete(`/watchlist/${animeId}`);
    return response.data;
  },

  // ==================== USER PROFILE ====================
  getUserProfile: async (userId?: string) => {
    const response = await client.get(`/users/${userId || 'me'}`);
    return response.data;
  },

  updateProfile: async (data: {
    display_name?: string;
    bio?: string;
    avatar_url?: string;
    favorite_genres?: string[];
  }) => {
    const response = await client.put('/users/me', data);
    return response.data;
  },

  getUserStats: async (userId?: string) => {
    const response = await client.get(`/users/${userId || 'me'}/stats`);
    return response.data;
  },

  getTasteProfile: async (userId?: string) => {
    const response = await client.get(`/users/${userId || 'me'}/taste-profile`);
    return response.data;
  },

  // ==================== ANALYTICS ====================
  getUserAnalytics: async () => {
    const response = await client.get('/analytics/user');
    return response.data;
  },

  getWatchTimeAnalytics: async () => {
    const response = await client.get('/analytics/watch-time');
    return response.data;
  },

  getGenreDistribution: async () => {
    const response = await client.get('/analytics/genres');
    return response.data;
  },

  // ==================== ATLAS ====================
  getAtlas: async () => {
    const response = await client.get('/atlas');
    return response.data;
  },
};

// Export client for custom requests
export { client };
