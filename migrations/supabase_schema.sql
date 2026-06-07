-- ============================================
-- ANIVIBE SUPABASE SCHEMA
-- Run this in Supabase SQL Editor
-- ============================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- PROFILES TABLE (extends Supabase auth.users)
-- ============================================
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    avatar_url VARCHAR(500),
    bio TEXT,
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    mal_username VARCHAR(100),
    mal_user_id INTEGER,
    anilist_username VARCHAR(100),
    anilist_user_id INTEGER,
    preferred_language VARCHAR(10) DEFAULT 'en',
    show_nsfw BOOLEAN DEFAULT false,
    anime_watched INTEGER DEFAULT 0,
    episodes_watched INTEGER DEFAULT 0,
    watch_time_hours FLOAT DEFAULT 0.0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_profiles_username ON profiles(username);

-- ============================================
-- ANIME TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.anime (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    title_english VARCHAR(500),
    title_japanese VARCHAR(500),
    title_synonyms TEXT,
    mal_id INTEGER UNIQUE,
    anilist_id INTEGER UNIQUE,
    synopsis TEXT,
    background TEXT,
    image_url VARCHAR(500),
    trailer_url VARCHAR(500),
    type VARCHAR(20),
    status VARCHAR(50),
    episodes INTEGER,
    duration_minutes INTEGER,
    aired_from TIMESTAMPTZ,
    aired_to TIMESTAMPTZ,
    season VARCHAR(20),
    year INTEGER,
    score FLOAT,
    scored_by INTEGER,
    rank INTEGER,
    popularity INTEGER,
    members INTEGER,
    favorites INTEGER,
    rating VARCHAR(50),
    source VARCHAR(100),
    is_nsfw BOOLEAN DEFAULT false,
    is_hidden_gem BOOLEAN DEFAULT false,
    popularity_score FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_synced TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_anime_title ON anime(title);
CREATE INDEX IF NOT EXISTS idx_anime_year ON anime(year);
CREATE INDEX IF NOT EXISTS idx_anime_score ON anime(score);
CREATE INDEX IF NOT EXISTS idx_anime_mal_id ON anime(mal_id);
CREATE INDEX IF NOT EXISTS idx_anime_popularity ON anime(popularity);

-- ============================================
-- GENRES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.genres (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    mal_id INTEGER UNIQUE,
    description TEXT
);

CREATE INDEX IF NOT EXISTS idx_genres_name ON genres(name);

-- ============================================
-- STUDIOS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.studios (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) UNIQUE NOT NULL,
    mal_id INTEGER UNIQUE,
    established INTEGER
);

CREATE INDEX IF NOT EXISTS idx_studios_name ON studios(name);

-- ============================================
-- TAGS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(50),
    description TEXT,
    anilist_id INTEGER UNIQUE
);

CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name);
CREATE INDEX IF NOT EXISTS idx_tags_category ON tags(category);

-- ============================================
-- JUNCTION TABLES (Many-to-Many)
-- ============================================
CREATE TABLE IF NOT EXISTS public.anime_genres (
    anime_id INTEGER REFERENCES anime(id) ON DELETE CASCADE,
    genre_id INTEGER REFERENCES genres(id) ON DELETE CASCADE,
    PRIMARY KEY (anime_id, genre_id)
);

CREATE TABLE IF NOT EXISTS public.anime_studios (
    anime_id INTEGER REFERENCES anime(id) ON DELETE CASCADE,
    studio_id INTEGER REFERENCES studios(id) ON DELETE CASCADE,
    PRIMARY KEY (anime_id, studio_id)
);

CREATE TABLE IF NOT EXISTS public.anime_tags (
    anime_id INTEGER REFERENCES anime(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (anime_id, tag_id)
);

-- ============================================
-- RATINGS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.ratings (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    anime_id INTEGER REFERENCES anime(id) ON DELETE CASCADE NOT NULL,
    score FLOAT NOT NULL CHECK (score >= 1 AND score <= 10),
    review TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, anime_id)
);

CREATE INDEX IF NOT EXISTS idx_ratings_user ON ratings(user_id);
CREATE INDEX IF NOT EXISTS idx_ratings_anime ON ratings(anime_id);

-- ============================================
-- WATCHLIST ENTRIES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.watchlist_entries (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
    anime_id INTEGER REFERENCES anime(id) ON DELETE CASCADE NOT NULL,
    status VARCHAR(20) DEFAULT 'plan_to_watch' CHECK (status IN ('watching', 'completed', 'on_hold', 'dropped', 'plan_to_watch')),
    progress INTEGER DEFAULT 0,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, anime_id)
);

CREATE INDEX IF NOT EXISTS idx_watchlist_user ON watchlist_entries(user_id);
CREATE INDEX IF NOT EXISTS idx_watchlist_anime ON watchlist_entries(anime_id);
CREATE INDEX IF NOT EXISTS idx_watchlist_status ON watchlist_entries(status);

-- ============================================
-- SOCIAL FEATURES (Friends)
-- ============================================
CREATE TABLE IF NOT EXISTS public.friends (
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    friend_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    status VARCHAR(20) CHECK (status IN ('pending', 'accepted')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (user_id, friend_id)
);

CREATE INDEX IF NOT EXISTS idx_friends_user ON friends(user_id);
CREATE INDEX IF NOT EXISTS idx_friends_friend ON friends(friend_id);

-- ============================================
-- ACTIVITY FEED
-- ============================================
CREATE TABLE IF NOT EXISTS public.activities (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL, -- watched, rated, reviewed, added
    anime_id INTEGER REFERENCES anime(id) ON DELETE SET NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_activities_user ON activities(user_id);
CREATE INDEX IF NOT EXISTS idx_activities_created ON activities(created_at DESC);

-- ============================================
-- ADVANCED REVIEWS
-- ============================================
CREATE TABLE IF NOT EXISTS public.reviews (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    anime_id INTEGER REFERENCES anime(id) ON DELETE CASCADE,
    title VARCHAR(200),
    content TEXT NOT NULL,
    rating FLOAT CHECK (rating >= 1 AND rating <= 10),
    sentiment VARCHAR(20),
    helpful_count INTEGER DEFAULT 0,
    is_spoiler BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_reviews_anime ON reviews(anime_id);
CREATE INDEX IF NOT EXISTS idx_reviews_user ON reviews(user_id);

CREATE TABLE IF NOT EXISTS public.review_votes (
    review_id INTEGER REFERENCES reviews(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    is_helpful BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (review_id, user_id)
);

-- ============================================
-- ROW LEVEL SECURITY POLICIES
-- ============================================

-- Enable RLS on all tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE anime ENABLE ROW LEVEL SECURITY;
ALTER TABLE genres ENABLE ROW LEVEL SECURITY;
ALTER TABLE studios ENABLE ROW LEVEL SECURITY;
ALTER TABLE tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE anime_genres ENABLE ROW LEVEL SECURITY;
ALTER TABLE anime_studios ENABLE ROW LEVEL SECURITY;
ALTER TABLE anime_tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE ratings ENABLE ROW LEVEL SECURITY;
ALTER TABLE watchlist_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE friends ENABLE ROW LEVEL SECURITY;
ALTER TABLE activities ENABLE ROW LEVEL SECURITY;
ALTER TABLE reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE review_votes ENABLE ROW LEVEL SECURITY;

-- ============================================
-- PROFILES POLICIES
-- ============================================
CREATE POLICY "Profiles are viewable by everyone"
    ON profiles FOR SELECT USING (true);

CREATE POLICY "Users can update own profile"
    ON profiles FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile"
    ON profiles FOR INSERT WITH CHECK (auth.uid() = id);

-- ============================================
-- ANIME POLICIES (Public Read)
-- ============================================
CREATE POLICY "Anime is viewable by everyone"
    ON anime FOR SELECT USING (true);

-- ============================================
-- GENRES, STUDIOS, TAGS POLICIES (Public Read)
-- ============================================
CREATE POLICY "Genres viewable by everyone"
    ON genres FOR SELECT USING (true);

CREATE POLICY "Studios viewable by everyone"
    ON studios FOR SELECT USING (true);

CREATE POLICY "Tags viewable by everyone"
    ON tags FOR SELECT USING (true);

CREATE POLICY "Anime genres viewable by everyone"
    ON anime_genres FOR SELECT USING (true);

CREATE POLICY "Anime studios viewable by everyone"
    ON anime_studios FOR SELECT USING (true);

CREATE POLICY "Anime tags viewable by everyone"
    ON anime_tags FOR SELECT USING (true);

-- ============================================
-- RATINGS POLICIES (User-specific)
-- ============================================
CREATE POLICY "Users can view all ratings"
    ON ratings FOR SELECT USING (true);

CREATE POLICY "Users can insert own ratings"
    ON ratings FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own ratings"
    ON ratings FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own ratings"
    ON ratings FOR DELETE USING (auth.uid() = user_id);

-- ============================================
-- WATCHLIST POLICIES (User-specific)
-- ============================================
CREATE POLICY "Users can view own watchlist"
    ON watchlist_entries FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert to own watchlist"
    ON watchlist_entries FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own watchlist"
    ON watchlist_entries FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete from watchlist"
    ON watchlist_entries FOR DELETE USING (auth.uid() = user_id);

-- ============================================
-- SOCIAL POLICIES
-- ============================================
CREATE POLICY "Users can view their own friends"
    ON friends FOR SELECT USING (auth.uid() = user_id OR auth.uid() = friend_id);

CREATE POLICY "Users can insert friend requests"
    ON friends FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update friendship status"
    ON friends FOR UPDATE USING (auth.uid() = friend_id); -- Only recipient can accept

CREATE POLICY "Users can delete friends"
    ON friends FOR DELETE USING (auth.uid() = user_id OR auth.uid() = friend_id);

-- ============================================
-- ACTIVITY POLICIES
-- ============================================
CREATE POLICY "Activities are viewable by everyone"
    ON activities FOR SELECT USING (true);

CREATE POLICY "Users can insert own activity"
    ON activities FOR INSERT WITH CHECK (auth.uid() = user_id);

-- ============================================
-- REVIEW POLICIES
-- ============================================
CREATE POLICY "Reviews are viewable by everyone"
    ON reviews FOR SELECT USING (true);

CREATE POLICY "Users can insert own reviews"
    ON reviews FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own reviews"
    ON reviews FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own reviews"
    ON reviews FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "Votes viewable by everyone"
    ON review_votes FOR SELECT USING (true);

CREATE POLICY "Users can vote"
    ON review_votes FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can change vote"
    ON review_votes FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can remove vote"
    ON review_votes FOR DELETE USING (auth.uid() = user_id);

-- ============================================
-- AUTO-CREATE PROFILE ON SIGNUP TRIGGER
-- ============================================
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, username, email, full_name)
    VALUES (
        NEW.id,
        COALESCE(NEW.raw_user_meta_data->>'username', split_part(NEW.email, '@', 1)),
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', '')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Drop existing trigger if exists
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

-- Create trigger
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ============================================
-- UPDATED_AT TRIGGER FUNCTION
-- ============================================
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at trigger to tables
CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_anime_updated_at
    BEFORE UPDATE ON anime
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ratings_updated_at
    BEFORE UPDATE ON ratings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_watchlist_updated_at
    BEFORE UPDATE ON watchlist_entries
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_friends_updated_at
    BEFORE UPDATE ON friends
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reviews_updated_at
    BEFORE UPDATE ON reviews
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- GRANT PERMISSIONS
-- ============================================
GRANT ALL ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO postgres;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO postgres;
