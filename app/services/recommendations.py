"""
Recommendation engine service
Implements the database-backed hybrid recommendation path:
collaborative filtering plus content-based scoring.
"""
import time
import logging
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
import numpy as np

from app.models.anime import Anime
from app.models.rating import Rating
from app.models.watchlist import WatchlistEntry
from app.services.collaborative_filtering import get_collaborative_recommendations
from app.services.content_based import get_content_based_recommendations
from app.services.llm_parser import parse_query_with_llm
from app.core.cache import cache_get, cache_set

logger = logging.getLogger(__name__)


async def get_personalized_recommendations(
    user_id: str,
    top_k: int = 10,
    method: str = "hybrid",
    filters: Optional[Dict[str, Any]] = None,
    exclude_watched: bool = True,
    popularity_attenuation: float = 0.3,
    diversity_weight: float = 0.2,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """
    Get personalized recommendations for user
    
    Args:
        user_id: User ID
        top_k: Number of recommendations
        method: Recommendation method (collaborative, content, hybrid)
        filters: Additional filters
        exclude_watched: Exclude anime user has already watched
        popularity_attenuation: Factor for deprioritizing popular anime (0-1)
        diversity_weight: Weight for genre diversity (0-1)
        db: Database session
    
    Returns:
        Recommendation results
    """
    start_time = time.time()
    
    # Check cache
    cache_key = f"recommendations:user:{user_id}:method:{method}:k:{top_k}"
    cached = await cache_get(cache_key)
    if cached:
        return cached
    
    # Get user's watched anime for exclusion
    watched_ids = set()
    if exclude_watched:
        watched_result = await db.execute(
            select(WatchlistEntry.anime_id)
            .filter(WatchlistEntry.user_id == user_id)
        )
        watched_ids = {row[0] for row in watched_result}
    
    # Get user ratings for collaborative filtering
    ratings_result = await db.execute(
        select(Rating)
        .filter(Rating.user_id == user_id)
    )
    user_ratings = {r.anime_id: r.score for r in ratings_result.scalars().all()}
    
    # Generate recommendations based on method
    if method == "collaborative":
        recommendations = await get_collaborative_recommendations(
            user_id=user_id,
            user_ratings=user_ratings,
            top_k=top_k * 2,
            db=db
        )
    elif method == "content":
        recommendations = await get_content_based_recommendations(
            user_ratings=user_ratings,
            top_k=top_k * 2,
            db=db
        )
    else:  # hybrid
        # Get both types and combine
        collab_recs = await get_collaborative_recommendations(
            user_id=user_id,
            user_ratings=user_ratings,
            top_k=top_k * 2,
            db=db
        )
        content_recs = await get_content_based_recommendations(
            user_ratings=user_ratings,
            top_k=top_k * 2,
            db=db
        )
        
        # Combine with weights
        recommendations = {}
        for anime_id, score in collab_recs.items():
            recommendations[anime_id] = score * 0.6  # 60% collaborative
        
        for anime_id, score in content_recs.items():
            recommendations[anime_id] = recommendations.get(anime_id, 0) + score * 0.4  # 40% content
    
    # Exclude watched anime
    for anime_id in watched_ids:
        recommendations.pop(anime_id, None)
    
    # Apply popularity attenuation for hidden gem discovery
    if popularity_attenuation > 0:
        anime_popularity = await db.execute(
            select(Anime.id, Anime.members)
            .filter(Anime.id.in_(list(recommendations.keys())))
        )
        
        for anime_id, members in anime_popularity:
            if members and anime_id in recommendations:
                # Logarithmic dampening
                attenuation = 1.0 - (popularity_attenuation * np.log10(max(members, 10)) / 6)
                recommendations[anime_id] *= max(attenuation, 0.1)
    
    # Sort and get top K
    sorted_recs = sorted(
        recommendations.items(),
        key=lambda x: x[1],
        reverse=True
    )[:top_k]
    
    # Fetch anime details
    anime_ids = [anime_id for anime_id, _ in sorted_recs]
    result = await db.execute(
        select(Anime)
        .options(
            selectinload(Anime.genres),
            selectinload(Anime.studios),
            selectinload(Anime.tags)
        )
        .filter(Anime.id.in_(anime_ids))
    )
    anime_dict = {anime.id: anime for anime in result.scalars().all()}
    
    # Format recommendations
    recommendations_list = []
    for rank, (anime_id, score) in enumerate(sorted_recs, 1):
        anime = anime_dict.get(anime_id)
        if not anime:
            continue
        
        recommendations_list.append({
            "anime_id": anime_id,
            "anime": anime.to_dict(include_relationships=True),
            "score": float(score),
            "rank": rank,
            "explanation": {
                "method": method,
                "confidence": float(score),
                "features": [
                    {"feature_name": "user_preferences", "importance": 0.8, "value": "based on your ratings"},
                    {"feature_name": "popularity_adjusted", "importance": popularity_attenuation, "value": "hidden gem factor"}
                ],
                "reasoning": f"Recommended based on your rating history and preferences using {method} method"
            }
        })
    
    execution_time = (time.time() - start_time) * 1000
    
    result = {
        "recommendations": recommendations_list,
        "total": len(recommendations_list),
        "method": method,
        "user_id": user_id,
        "execution_time_ms": execution_time
    }
    
    # Cache for 1 hour
    await cache_set(cache_key, result, expire=3600)
    
    return result


async def get_similar_anime(
    anime_id: int,
    top_k: int = 10,
    method: str = "multimodal",
    db: AsyncSession = None
) -> Dict[str, Any]:
    """
    Find anime similar to given anime
    
    Args:
        anime_id: Target anime ID
        top_k: Number of similar anime
        method: Similarity method
        db: Database session
    
    Returns:
        Similar anime results
    """
    start_time = time.time()
    
    # Get target anime
    result = await db.execute(
        select(Anime)
        .options(selectinload(Anime.genres), selectinload(Anime.studios), selectinload(Anime.tags))
        .filter(Anime.id == anime_id)
    )
    target_anime = result.scalar_one_or_none()
    
    if not target_anime:
        return {
            "recommendations": [],
            "total": 0,
            "method": method,
            "user_id": None,
            "execution_time_ms": 0
        }
    
    # Use content-based similarity
    similar = await get_content_based_recommendations(
        user_ratings={anime_id: 10.0},  # Fake rating to get similar
        top_k=top_k + 1,  # +1 to exclude self
        db=db
    )
    
    # Remove the target anime itself
    similar.pop(anime_id, None)
    
    # Get top K
    sorted_similar = sorted(similar.items(), key=lambda x: x[1], reverse=True)[:top_k]
    
    # Fetch anime details
    similar_ids = [aid for aid, _ in sorted_similar]
    result = await db.execute(
        select(Anime)
        .options(selectinload(Anime.genres), selectinload(Anime.studios), selectinload(Anime.tags))
        .filter(Anime.id.in_(similar_ids))
    )
    anime_dict = {anime.id: anime for anime in result.scalars().all()}
    
    # Format recommendations
    recommendations = []
    for rank, (aid, score) in enumerate(sorted_similar, 1):
        anime = anime_dict.get(aid)
        if not anime:
            continue
        
        # Find similarity reasons
        reasons = []
        if target_anime.genres and anime.genres:
            shared_genres = set(g.name for g in target_anime.genres) & set(g.name for g in anime.genres)
            if shared_genres:
                reasons.append(f"Shared genres: {', '.join(list(shared_genres)[:3])}")
        
        if target_anime.studios and anime.studios:
            shared_studios = set(s.name for s in target_anime.studios) & set(s.name for s in anime.studios)
            if shared_studios:
                reasons.append(f"Same studio: {list(shared_studios)[0]}")
        
        recommendations.append({
            "anime_id": aid,
            "anime": anime.to_dict(include_relationships=True),
            "score": float(score),
            "rank": rank,
            "similarity_reasons": reasons if reasons else ["Similar content and themes"]
        })
    
    execution_time = (time.time() - start_time) * 1000
    
    return {
        "recommendations": recommendations,
        "total": len(recommendations),
        "method": method,
        "user_id": None,
        "execution_time_ms": execution_time
    }


async def discover_hidden_gems(
    user_id: Optional[str],
    top_k: int = 10,
    max_popularity: int = 50000,
    min_score: float = 7.5,
    genres: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """
    Discover hidden gem anime (high quality, low popularity)
    """
    start_time = time.time()
    
    query = select(Anime).options(
        selectinload(Anime.genres),
        selectinload(Anime.studios),
        selectinload(Anime.tags)
    )
    
    # Apply filters
    conditions = [
        Anime.members <= max_popularity,
        Anime.score >= min_score,
        Anime.scored_by >= 1000  # Minimum ratings for reliability
    ]
    
    query = query.filter(and_(*conditions))
    query = query.order_by(Anime.score.desc()).limit(top_k * 2)
    
    result = await db.execute(query)
    hidden_gems = result.scalars().all()
    
    # Format recommendations
    recommendations = []
    for rank, anime in enumerate(hidden_gems[:top_k], 1):
        recommendations.append({
            "anime_id": anime.id,
            "anime": anime.to_dict(include_relationships=True),
            "score": anime.score or 0.0,
            "rank": rank,
            "similarity_reasons": [
                f"High quality (score: {anime.score})",
                f"Under the radar (only {anime.members:,} members)",
                "Hidden gem"
            ]
        })
    
    execution_time = (time.time() - start_time) * 1000
    
    return {
        "recommendations": recommendations,
        "total": len(recommendations),
        "method": "hidden_gems",
        "user_id": user_id,
        "execution_time_ms": execution_time
    }


async def get_mood_based_recommendations(
    mood: str,
    top_k: int = 10,
    user_id: Optional[str] = None,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """
    Get recommendations based on mood/emotional state
    """
    # Parse mood with LLM
    parsed = await parse_query_with_llm(f"I want anime that matches this mood: {mood}")
    
    # Use semantic search with mood as query
    from app.services.semantic_search import semantic_vibe_search
    
    return await semantic_vibe_search(
        query=parsed.get("text_description", mood),
        top_k=top_k,
        db=db
    )


async def get_user_taste_profile(
    user_id: str,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """
    Analyze user's taste profile
    """
    # Get user ratings with anime details
    result = await db.execute(
        select(Rating, Anime)
        .join(Anime, Rating.anime_id == Anime.id)
        .options(selectinload(Anime.genres), selectinload(Anime.studios))
        .filter(Rating.user_id == user_id)
    )
    
    ratings_with_anime = result.all()
    
    if not ratings_with_anime:
        return {
            "user_id": user_id,
            "dominant_genres": [],
            "favorite_studios": [],
            "average_score": 0.0,
            "rating_distribution": {},
            "preferred_types": {},
            "watch_patterns": {},
            "genre_diversity_score": 0.0
        }
    
    # Analyze genres
    genre_scores = {}
    genre_counts = {}
    
    for rating, anime in ratings_with_anime:
        for genre in anime.genres:
            genre_scores[genre.name] = genre_scores.get(genre.name, 0) + rating.score
            genre_counts[genre.name] = genre_counts.get(genre.name, 0) + 1
    
    dominant_genres = [
        {"genre": genre, "average_score": genre_scores[genre] / genre_counts[genre]}
        for genre in sorted(genre_counts, key=lambda x: genre_counts[x], reverse=True)[:10]
    ]
    
    # Analyze studios
    studio_counts = {}
    for _, anime in ratings_with_anime:
        for studio in anime.studios:
            studio_counts[studio.name] = studio_counts.get(studio.name, 0) + 1
    
    favorite_studios = [
        {"studio": studio, "count": count}
        for studio, count in sorted(studio_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    ]
    
    # Rating distribution
    scores = [r.score for r, _ in ratings_with_anime]
    avg_score = sum(scores) / len(scores)
    
    rating_dist = {}
    for score in range(1, 11):
        rating_dist[str(score)] = len([s for s in scores if int(s) == score])
    
    # Genre diversity (entropy)
    total_ratings = sum(genre_counts.values())
    genre_probs = [count / total_ratings for count in genre_counts.values()]
    diversity = -sum(p * np.log2(p) for p in genre_probs if p > 0)
    
    return {
        "user_id": user_id,
        "dominant_genres": dominant_genres,
        "favorite_studios": favorite_studios,
        "average_score": avg_score,
        "rating_distribution": rating_dist,
        "preferred_types": {},
        "watch_patterns": {},
        "genre_diversity_score": float(diversity)
    }
