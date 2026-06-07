-- ==============================================================================
-- AniVibe: Neo-Tokyo Edition - Final Production Schema
-- ==============================================================================

-- 1. EXTENSIONS
create extension if not exists "vector";
create extension if not exists "uuid-ossp";

-- 2. ENUMS
create type anime_type as enum ('TV', 'Movie', 'OVA', 'ONA', 'Special', 'Music');
create type anime_status as enum ('Finished Airing', 'Currently Airing', 'Not Yet Aired');
create type anime_season as enum ('Winter', 'Spring', 'Summer', 'Fall');

-- 3. TABLES

-- PROFILES (Extends Supabase auth.users)
create table public.profiles (
  id uuid references auth.users on delete cascade not null primary key,
  username text unique not null,
  email text not null,
  full_name text,
  avatar_url text,
  bio text,
  
  -- Integrations
  mal_username text,
  mal_user_id int,
  anilist_username text,
  anilist_user_id int,
  
  -- Stats
  anime_watched int default 0,
  episodes_watched int default 0,
  watch_time_hours float default 0,
  
  -- Preferences
  preferred_language text default 'en',
  show_nsfw boolean default false,
  
  is_active boolean default true,
  is_verified boolean default false,
  
  created_at timestamptz default now(),
  updated_at timestamptz default now(),
  last_login timestamptz
);

-- ANIME (The Core Data)
create table public.anime (
  id int primary key, -- Explicit ID from MAL
  title text not null,
  title_english text,
  title_japanese text,
  title_synonyms text, -- JSON string
  
  mal_id int unique,
  anilist_id int unique,
  
  synopsis text,
  background text,
  image_url text,
  trailer_url text,
  
  type anime_type,
  status anime_status,
  
  episodes int,
  duration_minutes int,
  
  aired_from timestamp,
  aired_to timestamp,
  season anime_season,
  year int,
  
  score float,
  scored_by int,
  rank int,
  popularity int,
  members int,
  favorites int,
  
  rating text,
  source text,
  
  is_nsfw boolean default false,
  is_hidden_gem boolean default false,
  popularity_score float,
  
  -- VECTORS (The AI Magic)
  embedding_clip vector(512),
  embedding_sbert vector(384),
  
  created_at timestamptz default now(),
  updated_at timestamptz default now(),
  last_synced timestamptz
);

-- METADATA TABLES
create table public.genres (
  id serial primary key,
  name text unique not null,
  description text,
  mal_id int
);

create table public.studios (
  id serial primary key,
  name text unique not null,
  established int,
  mal_id int
);

create table public.tags (
  id serial primary key,
  name text unique not null,
  category text,
  description text,
  anilist_id int
);

-- JUNCTION TABLES
create table public.anime_genres (
  anime_id int references public.anime(id) on delete cascade,
  genre_id int references public.genres(id) on delete cascade,
  primary key (anime_id, genre_id)
);

create table public.anime_studios (
  anime_id int references public.anime(id) on delete cascade,
  studio_id int references public.studios(id) on delete cascade,
  primary key (anime_id, studio_id)
);

create table public.anime_tags (
  anime_id int references public.anime(id) on delete cascade,
  tag_id int references public.tags(id) on delete cascade,
  primary key (anime_id, tag_id)
);

-- WATCHLIST
create table public.watchlist_entries (
  id serial primary key,
  user_id uuid references public.profiles(id) on delete cascade not null,
  anime_id int references public.anime(id) on delete cascade not null,
  
  status text not null default 'plan_to_watch', -- watching, completed, etc.
  progress int default 0,
  score int, -- Personal score 1-10
  
  started_at timestamp,
  completed_at timestamp,
  notes text,
  
  created_at timestamptz default now(),
  updated_at timestamptz default now(),
  
  unique(user_id, anime_id)
);

-- REVIEWS
create table public.reviews (
  id serial primary key,
  user_id uuid references public.profiles(id) on delete cascade not null,
  anime_id int references public.anime(id) on delete cascade not null,
  
  title text,
  content text not null,
  rating float,
  is_spoiler boolean default false,
  
  helpful_count int default 0,
  
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table public.review_votes (
  review_id int references public.reviews(id) on delete cascade,
  user_id uuid references public.profiles(id) on delete cascade,
  is_helpful boolean default true,
  created_at timestamptz default now(),
  primary key (review_id, user_id)
);

-- 4. ROW LEVEL SECURITY (RLS)
alter table public.profiles enable row level security;
alter table public.anime enable row level security;
alter table public.watchlist_entries enable row level security;
alter table public.reviews enable row level security;

-- PROFILES
create policy "Public profiles are viewable by everyone."
  on public.profiles for select
  using ( true );

create policy "Users can update own profile."
  on public.profiles for update
  using ( auth.uid() = id );

-- ANIME (Read only for public, write for service_role)
create policy "Anime is public."
  on public.anime for select
  using ( true );
  
-- WATCHLIST
create policy "Users can view own watchlist."
  on public.watchlist_entries for select
  using ( auth.uid() = user_id );

create policy "Users can insert own watchlist."
  on public.watchlist_entries for insert
  with check ( auth.uid() = user_id );

create policy "Users can update own watchlist."
  on public.watchlist_entries for update
  using ( auth.uid() = user_id );

create policy "Users can delete own watchlist."
  on public.watchlist_entries for delete
  using ( auth.uid() = user_id );

-- REVIEWS
create policy "Reviews are public."
  on public.reviews for select
  using ( true );

create policy "Users can create reviews."
  on public.reviews for insert
  with check ( auth.uid() = user_id );

create policy "Users can update own reviews."
  on public.reviews for update
  using ( auth.uid() = user_id );
  
create policy "Users can delete own reviews."
  on public.reviews for delete
  using ( auth.uid() = user_id );

-- 5. FUNCTION & TRIGGERS

-- Auto-create profile on signup
create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id, email, username)
  values (new.id, new.email, split_part(new.email, '@', 1));
  return new;
end;
$$ language plpgsql security definer;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();

-- Auto-update updated_at timestamp
create or replace function update_updated_at_column()
returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language plpgsql;

create trigger update_profiles_updated_at before update on public.profiles for each row execute procedure update_updated_at_column();
create trigger update_anime_updated_at before update on public.anime for each row execute procedure update_updated_at_column();
create trigger update_watchlist_updated_at before update on public.watchlist_entries for each row execute procedure update_updated_at_column();
create trigger update_reviews_updated_at before update on public.reviews for each row execute procedure update_updated_at_column();

-- 6. INDEXES (Performance)
create index idx_anime_title on public.anime using gin(to_tsvector('english', title));
create index idx_watchlist_user on public.watchlist_entries(user_id);
create index idx_reviews_anime on public.reviews(anime_id);

-- Vector Indexes (IVFFlat for speed)
-- Note: Requires data to be populated first for best results, creating placeholder
-- create index on public.anime using ivfflat (embedding_sbert vector_cosine_ops) with (lists = 100);
-- create index on public.anime using ivfflat (embedding_clip vector_cosine_ops) with (lists = 100);
