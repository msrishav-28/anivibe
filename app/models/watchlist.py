"""
Watchlist model for Supabase
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class WatchlistEntry(Base):
    """User watchlist entry model"""
    
    __tablename__ = "watchlist_entries"
    __table_args__ = (
        UniqueConstraint('user_id', 'anime_id', name='unique_user_anime_watchlist'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys - user_id is UUID (Supabase auth.users)
    user_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id', ondelete='CASCADE'), nullable=False, index=True)
    anime_id = Column(Integer, ForeignKey('anime.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Status - using string instead of enum for flexibility
    status = Column(String(20), default='plan_to_watch', nullable=False)
    
    # Progress
    progress = Column(Integer, default=0, nullable=False)
    
    # Dates
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("Profile", back_populates="watchlist")
    anime = relationship("Anime", back_populates="watchlist_entries")
    
    def __repr__(self):
        return f"<WatchlistEntry(user_id={self.user_id}, anime_id={self.anime_id}, status={self.status})>"
    
    def to_dict(self, include_anime=False):
        data = {
            "id": self.id,
            "user_id": str(self.user_id),
            "anime_id": self.anime_id,
            "status": self.status,
            "progress": self.progress,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_anime and self.anime:
            data["anime"] = self.anime.to_dict(include_relationships=True)
        
        return data


# Status values for reference
WATCHLIST_STATUSES = ['watching', 'completed', 'on_hold', 'dropped', 'plan_to_watch']
