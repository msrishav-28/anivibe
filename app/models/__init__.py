"""
Database models for Supabase
"""
from app.models.user import Profile, User  # User is alias for Profile
from app.models.anime import Anime, Genre, Studio, Tag
from app.models.rating import Rating
from app.models.watchlist import WatchlistEntry
from app.models.social import Friend, Activity
from app.models.review import Review, ReviewVote

__all__ = [
    "Profile",
    "User",  # Alias for backwards compatibility
    "Anime",
    "Genre",
    "Studio",
    "Tag",
    "Rating",
    "WatchlistEntry",
    "Friend",
    "Activity",
    "Review",
    "ReviewVote"
]
