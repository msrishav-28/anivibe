"""
Watchlist schemas for Supabase
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# Valid status values
WATCHLIST_STATUSES = ['watching', 'completed', 'on_hold', 'dropped', 'plan_to_watch']


class WatchlistEntryBase(BaseModel):
    """Base watchlist entry schema"""
    anime_id: int = Field(..., description="Anime ID")
    status: str = Field(default="plan_to_watch", description="Watch status")


class WatchlistEntryCreate(WatchlistEntryBase):
    """Schema for creating a watchlist entry"""
    progress: int = Field(0, ge=0, description="Episodes watched")
    notes: Optional[str] = Field(None, max_length=1000)


class WatchlistEntryUpdate(BaseModel):
    """Schema for updating a watchlist entry"""
    status: Optional[str] = None
    progress: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=1000)


class WatchlistEntryResponse(WatchlistEntryBase):
    """Watchlist entry response schema (Supabase UUID user)"""
    id: int
    user_id: str  # UUID as string
    progress: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    anime: Optional[dict] = None
    
    class Config:
        from_attributes = True


class WatchlistStats(BaseModel):
    """Watchlist statistics schema"""
    total_entries: int
    plan_to_watch: int
    watching: int
    completed: int
    on_hold: int
    dropped: int
    total_episodes: int
    total_watch_time_hours: float
    completion_rate: float
