"""
User/Profile model for Supabase
"""
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, Float, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class Profile(Base):
    """
    User profile model - extends Supabase auth.users.
    
    The ID is a UUID that references auth.users(id) in Supabase.
    Profile is automatically created when a user signs up via trigger.
    """
    
    __tablename__ = "profiles"
    
    # Primary key is UUID referencing auth.users
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), nullable=False)
    
    # Profile
    full_name = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    
    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # External integrations
    mal_username = Column(String(100), nullable=True)
    mal_user_id = Column(Integer, nullable=True)
    anilist_username = Column(String(100), nullable=True)
    anilist_user_id = Column(Integer, nullable=True)
    
    # Preferences
    preferred_language = Column(String(10), default="en")
    show_nsfw = Column(Boolean, default=False)
    
    # Statistics
    anime_watched = Column(Integer, default=0)
    episodes_watched = Column(Integer, default=0)
    watch_time_hours = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    ratings = relationship("Rating", back_populates="user", cascade="all, delete-orphan")
    watchlist = relationship("WatchlistEntry", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Profile(id={self.id}, username='{self.username}')>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.id),  # Alias for frontend compatibility
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "avatar_url": self.avatar_url,
            "bio": self.bio,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "mal_username": self.mal_username,
            "anilist_username": self.anilist_username,
            "anime_watched": self.anime_watched,
            "episodes_watched": self.episodes_watched,
            "watch_time_hours": self.watch_time_hours,
            "preferred_language": self.preferred_language,
            "show_nsfw": self.show_nsfw,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None
        }


# Alias for backwards compatibility
User = Profile
