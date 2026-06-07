"""
Recommendation endpoints for Supabase
"""
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from uuid import UUID
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.anime import Anime
from app.services.recommendations import (
    get_personalized_recommendations,
    get_similar_anime,
    discover_hidden_gems,
    get_mood_based_recommendations,
    get_user_taste_profile
)

router = APIRouter()


# Request schemas
class RecommendationRequest(BaseModel):
    top_k: int = 10
    method: str = "hybrid"
    filters: Optional[Dict[str, Any]] = None
    exclude_watched: bool = True
    popularity_attenuation: float = 0.3
    diversity_weight: float = 0.2


class SimilarAnimeRequest(BaseModel):
    anime_id: int
    top_k: int = 10
    method: str = "multimodal"


class HiddenGemRequest(BaseModel):
    user_id: Optional[str] = None
    top_k: int = 10
    max_popularity: int = 50000
    min_score: float = 7.0
    genres: Optional[List[str]] = None
    tags: Optional[List[str]] = None


class MoodBasedRequest(BaseModel):
    mood: str
    top_k: int = 10
    user_id: Optional[str] = None


@router.post("/personalized")
async def personalized_recommendations(
    request: RecommendationRequest,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get personalized recommendations for current user
    Uses the current hybrid system: collaborative filtering + content-based scoring
    """
    user_id = UUID(current_user["id"])
    
    try:
        results = await get_personalized_recommendations(
            user_id=str(user_id),
            top_k=request.top_k,
            method=request.method,
            filters=request.filters,
            exclude_watched=request.exclude_watched,
            popularity_attenuation=request.popularity_attenuation,
            diversity_weight=request.diversity_weight,
            db=db
        )
        
        return results
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Recommendation generation failed: {str(e)}"
        )


@router.post("/similar")
async def similar_anime(
    request: SimilarAnimeRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Find anime similar to a given anime
    Uses content-based similarity in the current implementation
    """
    try:
        results = await get_similar_anime(
            anime_id=request.anime_id,
            top_k=request.top_k,
            method=request.method,
            db=db
        )
        
        return results
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Similar anime search failed: {str(e)}"
        )


@router.post("/hidden-gems")
async def hidden_gems(
    request: HiddenGemRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Discover hidden gem anime
    High-quality, low-popularity titles
    """
    try:
        results = await discover_hidden_gems(
            user_id=request.user_id,
            top_k=request.top_k,
            max_popularity=request.max_popularity,
            min_score=request.min_score,
            genres=request.genres,
            tags=request.tags,
            db=db
        )
        
        return results
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Hidden gem discovery failed: {str(e)}"
        )


@router.post("/mood-based")
async def mood_based_recommendations(
    request: MoodBasedRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Get recommendations based on mood/emotional state
    Uses sentiment analysis and LLM parsing
    """
    try:
        results = await get_mood_based_recommendations(
            mood=request.mood,
            top_k=request.top_k,
            user_id=request.user_id,
            db=db
        )
        
        return results
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Mood-based recommendations failed: {str(e)}"
        )


@router.get("/taste-profile")
async def taste_profile(
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's taste profile
    Analyzes rating patterns, genres, studios, etc.
    """
    user_id = UUID(current_user["id"])
    
    try:
        profile = await get_user_taste_profile(
            user_id=str(user_id),
            db=db
        )
        
        return profile
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Taste profile generation failed: {str(e)}"
        )


@router.get("/cold-start")
async def cold_start_recommendations(
    top_k: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    Get recommendations for new users (cold start)
    Returns popular, highly-rated anime across diverse genres
    """
    import random
    
    # Get top-rated anime with diverse genres
    result = await db.execute(
        select(Anime)
        .options(
            selectinload(Anime.genres),
            selectinload(Anime.studios),
            selectinload(Anime.tags)
        )
        .filter(
            Anime.score >= 8.0,
            Anime.scored_by >= 10000
        )
        .order_by(func.random())
        .limit(top_k * 2)
    )
    
    anime_list = result.scalars().all()
    
    # Diversify by genres
    selected = []
    seen_genres = set()
    
    for anime in anime_list:
        anime_genres = {g.name for g in anime.genres}
        if not seen_genres or len(anime_genres & seen_genres) < 2:
            selected.append(anime)
            seen_genres.update(anime_genres)
            if len(selected) >= top_k:
                break
    
    # Fill remaining with random picks
    if len(selected) < top_k:
        remaining = [a for a in anime_list if a not in selected]
        selected.extend(remaining[:top_k - len(selected)])
    
    recommendations = []
    for i, anime in enumerate(selected, 1):
        recommendations.append({
            "anime_id": anime.id,
            "anime": anime.to_dict(include_relationships=True),
            "score": anime.score or 0.0,
            "rank": i,
            "explanation": None,
            "similarity_reasons": ["Popular and highly-rated", "Diverse genre selection"]
        })
    
    return {
        "recommendations": recommendations,
        "total": len(recommendations),
        "method": "cold_start",
        "user_id": None,
        "execution_time_ms": 0.0
    }
