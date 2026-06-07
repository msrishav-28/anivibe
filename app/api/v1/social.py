"""
Social Sharing API
Enables generating shareable links and tracking shares
"""
from fastapi import APIRouter, Depends
from typing import Dict, Any

from app.core.security import get_current_user_optional

router = APIRouter()

@router.post("/share/anime/{anime_id}")
async def share_anime(
    anime_id: int,
    platform: str,
    current_user: Dict[str, Any] = Depends(get_current_user_optional)
):
    """
    Track a share event and return a deep link
    """
    # In a real app, we might log this share event for analytics
    # or generate a unique short link
    
    base_url = "https://anivibe.vercel.app"
    share_url = f"{base_url}/anime/{anime_id}"
    
    return {
        "url": share_url,
        "message": f"Check out this anime on AniVibe!",
        "hashtags": ["anime", "anivibe", "recommendation"]
    }

@router.post("/share/list/{username}")
async def share_watchlist(
    username: str,
    platform: str
):
    """
    Share a user's watchlist
    """
    base_url = "https://anivibe.vercel.app"
    share_url = f"{base_url}/profile/{username}/list"
    
    return {
        "url": share_url,
        "message": f"Check out {username}'s anime list on AniVibe!",
        "hashtags": ["anime", "watchlist", "anivibe"]
    }
