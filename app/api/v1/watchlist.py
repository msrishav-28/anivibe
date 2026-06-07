"""
Watchlist endpoints for Supabase
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from uuid import UUID
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import Profile
from app.models.watchlist import WatchlistEntry, WATCHLIST_STATUSES
from app.models.anime import Anime

router = APIRouter()


# Request schemas
class WatchlistEntryCreate(BaseModel):
    anime_id: int
    status: str = "plan_to_watch"
    progress: int = 0
    notes: Optional[str] = None


class WatchlistEntryUpdate(BaseModel):
    status: Optional[str] = None
    progress: Optional[int] = None
    notes: Optional[str] = None


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_to_watchlist(
    entry_data: WatchlistEntryCreate,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add anime to watchlist
    """
    user_id = UUID(current_user["id"])
    
    # Validate status
    if entry_data.status not in WATCHLIST_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {WATCHLIST_STATUSES}"
        )
    
    # Check if anime exists
    anime_result = await db.execute(
        select(Anime).filter(Anime.id == entry_data.anime_id)
    )
    anime = anime_result.scalar_one_or_none()
    if not anime:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Anime not found"
        )
    
    # Check if entry already exists
    existing_result = await db.execute(
        select(WatchlistEntry).filter(
            and_(
                WatchlistEntry.user_id == user_id,
                WatchlistEntry.anime_id == entry_data.anime_id
            )
        )
    )
    if existing_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Anime already in watchlist"
        )
    
    # Create entry
    entry = WatchlistEntry(
        user_id=user_id,
        anime_id=entry_data.anime_id,
        status=entry_data.status,
        progress=entry_data.progress,
        notes=entry_data.notes
    )
    
    # Set started_at if watching
    if entry.status == "watching":
        entry.started_at = datetime.utcnow()
    
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    
    return entry.to_dict()


@router.get("/")
async def get_watchlist(
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    include_anime: bool = Query(True, description="Include anime details")
):
    """
    Get user's watchlist
    """
    user_id = UUID(current_user["id"])
    
    query = select(WatchlistEntry).filter(WatchlistEntry.user_id == user_id)
    
    if include_anime:
        query = query.options(selectinload(WatchlistEntry.anime))
    
    if status_filter:
        if status_filter not in WATCHLIST_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {WATCHLIST_STATUSES}"
            )
        query = query.filter(WatchlistEntry.status == status_filter)
    
    query = query.order_by(WatchlistEntry.updated_at.desc())
    
    result = await db.execute(query)
    entries = result.scalars().all()
    
    return [entry.to_dict(include_anime=include_anime) for entry in entries]


@router.get("/stats")
async def get_watchlist_stats(
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get watchlist statistics
    """
    user_id = UUID(current_user["id"])
    
    # Get counts by status
    stats = {}
    for status_name in WATCHLIST_STATUSES:
        result = await db.execute(
            select(func.count(WatchlistEntry.id))
            .filter(
                and_(
                    WatchlistEntry.user_id == user_id,
                    WatchlistEntry.status == status_name
                )
            )
        )
        stats[status_name] = result.scalar() or 0
    
    total = sum(stats.values())
    completed = stats.get("completed", 0)
    completion_rate = (completed / total * 100) if total > 0 else 0
    
    # Get user profile for episode stats
    profile_result = await db.execute(
        select(Profile).filter(Profile.id == user_id)
    )
    profile = profile_result.scalar_one_or_none()
    
    return {
        "total_entries": total,
        "plan_to_watch": stats.get("plan_to_watch", 0),
        "watching": stats.get("watching", 0),
        "completed": completed,
        "on_hold": stats.get("on_hold", 0),
        "dropped": stats.get("dropped", 0),
        "total_episodes": profile.episodes_watched if profile else 0,
        "total_watch_time_hours": profile.watch_time_hours if profile else 0.0,
        "completion_rate": completion_rate
    }


@router.put("/{entry_id}")
async def update_watchlist_entry(
    entry_id: int,
    entry_update: WatchlistEntryUpdate,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update watchlist entry
    """
    user_id = UUID(current_user["id"])
    
    result = await db.execute(
        select(WatchlistEntry).filter(
            and_(
                WatchlistEntry.id == entry_id,
                WatchlistEntry.user_id == user_id
            )
        )
    )
    entry = result.scalar_one_or_none()
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist entry not found"
        )
    
    # Update fields
    if entry_update.status is not None:
        if entry_update.status not in WATCHLIST_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {WATCHLIST_STATUSES}"
            )
        # Update timestamps based on status
        if entry_update.status == "watching" and not entry.started_at:
            entry.started_at = datetime.utcnow()
        elif entry_update.status == "completed":
            entry.completed_at = datetime.utcnow()
        entry.status = entry_update.status
    
    if entry_update.progress is not None:
        entry.progress = entry_update.progress
    
    if entry_update.notes is not None:
        entry.notes = entry_update.notes
    
    await db.commit()
    await db.refresh(entry)
    
    return entry.to_dict()


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_watchlist(
    entry_id: int,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Remove anime from watchlist
    """
    user_id = UUID(current_user["id"])
    
    result = await db.execute(
        select(WatchlistEntry).filter(
            and_(
                WatchlistEntry.id == entry_id,
                WatchlistEntry.user_id == user_id
            )
        )
    )
    entry = result.scalar_one_or_none()
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist entry not found"
        )
    
    await db.delete(entry)
    await db.commit()
    
    return None
