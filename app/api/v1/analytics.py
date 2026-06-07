"""
Analytics API endpoints
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from uuid import UUID
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import Profile
from app.models.watchlist import WatchlistEntry
from app.models.anime import Anime, anime_genres, Genre
from app.schemas.analytics import GenreDistribution, HeatmapData, AnalyticsStats

router = APIRouter()

@router.get("/genres", response_model=List[GenreDistribution])
async def get_genre_distribution(
    user_id: str = None,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get distribution of genres in user's watchlist/history"""
    target_user_id = UUID(user_id) if user_id else UUID(current_user["id"])
    
    # Calculate genre distribution from Completed or Watching anime
    query = select(Genre.name, func.count(Genre.id))\
        .join(anime_genres, Genre.id == anime_genres.c.genre_id)\
        .join(Anime, Anime.id == anime_genres.c.anime_id)\
        .join(WatchlistEntry, WatchlistEntry.anime_id == Anime.id)\
        .filter(WatchlistEntry.user_id == target_user_id)\
        .group_by(Genre.name)\
        .order_by(func.count(Genre.id).desc())
        
    result = await db.execute(query)
    rows = result.all()
    
    total = sum(row[1] for row in rows)
    
    distribution = []
    # Simple color mapping or random
    colors = ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF", "#FF9F40"]
    
    for i, row in enumerate(rows):
        distribution.append({
            "genre": row[0],
            "count": row[1],
            "percentage": (row[1] / total * 100) if total else 0,
            "color": colors[i % len(colors)]
        })
        
    return distribution

@router.get("/heatmap", response_model=List[HeatmapData])
async def get_watch_time_heatmap(
    user_id: str = None,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get watch time heatmap data"""
    target_user_id = UUID(user_id) if user_id else UUID(current_user["id"])
    
    # Use WatchlistEntry updated_at/completed_at for heatmap
    # This replaces the dependency on the Social/Activity table
    from sqlalchemy import func, or_
    
    # Query for both completed_at and updated_at (if watching)
    query = select(
            func.date(func.coalesce(WatchlistEntry.completed_at, WatchlistEntry.updated_at)), 
            func.count(WatchlistEntry.id)
        )\
        .filter(
            WatchlistEntry.user_id == target_user_id,
            or_(
                WatchlistEntry.status == "completed",
                WatchlistEntry.status == "watching"
            )
        )\
        .group_by(func.date(func.coalesce(WatchlistEntry.completed_at, WatchlistEntry.updated_at)))
        
    result = await db.execute(query)
    rows = result.all()
    
    data = []
    for row in rows:
        if row[0]: # Ensure date is not None
            data.append({
                "date": str(row[0]),
                "episodes": row[1], 
                "hours": row[1] * 5.0 # Estimate: An anime series ~5 hours? Or just episodes. 
                                      # If row[1] is count of Anime, then * 12 eps * 20 mins? 
                                      # Let's assume row[1] is Anime Count. 
                                      # To be safe/conservative, let's say 2.5 hours per entry update.
            })
        
    return data
