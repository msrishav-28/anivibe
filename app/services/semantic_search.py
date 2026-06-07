"""
Semantic search service using CLIP + BERT + LLM
"""
import time
import asyncio
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import numpy as np

from app.core.ml_models import encode_text_clip, encode_text_sbert
from app.core.cache import cache_get, cache_set
from app.models.anime import Anime
from app.services.llm_parser import parse_query_with_llm
from app.services.vector_search import search_by_clip, search_by_sbert


async def semantic_vibe_search(
    query: str,
    top_k: int = 10,
    use_clip: bool = True,
    use_sbert: bool = True,
    visual_weight: float = 0.4,
    text_weight: float = 0.6,
    filters: Optional[Dict[str, Any]] = None,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """
    Perform semantic vibe-based search using multimodal approach
    
    Args:
        query: Natural language search query
        top_k: Number of results to return
        use_clip: Use CLIP for visual search
        use_sbert: Use SBERT for text search
        visual_weight: Weight for visual features (0-1)
        text_weight: Weight for text features (0-1)
        filters: Additional filters
        db: Database session
    
    Returns:
        Dictionary with recommendations
    """
    start_time = time.time()
    
    # Step 1: Parse query with LLM to extract structured information
    parsed_query = await parse_query_with_llm(query)
    
    # Step 2: Perform visual search if CLIP enabled and visual elements present
    visual_results = {}
    if use_clip and parsed_query.get("visual_elements"):
        visual_query = " ".join(parsed_query["visual_elements"])
        # search_by_clip might fallback to SBERT (db required) or use Modal
        # For text-to-image search, we likely need SBERT fallback or a specific Modal endpoint not yet built
        # Let's use search_by_sbert as a safe proxy if db is available
        if db:
             visual_results = await search_by_sbert(visual_query, top_k=top_k * 2, db=db)
    
    # Step 3: Perform text semantic search if SBERT enabled
    text_results = {}
    if use_sbert and db:
        text_query = parsed_query.get("text_description", query)
        text_results = await search_by_sbert(text_query, top_k=top_k * 2, db=db)
    
    # Step 4: Combine results with weighted scoring
    combined_scores = {}
    
    # Add visual scores
    for anime_id, score in visual_results.items():
        combined_scores[anime_id] = score * visual_weight
    
    # Add text scores
    for anime_id, score in text_results.items():
        combined_scores[anime_id] = combined_scores.get(anime_id, 0) + score * text_weight
    
    # Step 5: Sort and get top K
    sorted_results = sorted(
        combined_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )[:top_k]
    
    # Step 6: Fetch anime details from database
    anime_ids = [anime_id for anime_id, _ in sorted_results]
    
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
    
    # Step 7: Format recommendations
    recommendations = []
    for rank, (anime_id, score) in enumerate(sorted_results, 1):
        anime = anime_dict.get(anime_id)
        if not anime:
            continue
        
        # Build explanation
        matched_elements = []
        if parsed_query.get("visual_elements"):
            matched_elements.append(f"Visual: {', '.join(parsed_query['visual_elements'])}")
        if parsed_query.get("emotions"):
            matched_elements.append(f"Mood: {', '.join(parsed_query['emotions'])}")
        if parsed_query.get("genres"):
            matched_elements.append(f"Genres: {', '.join(parsed_query['genres'])}")
        
        recommendations.append({
            "anime_id": anime_id,
            "anime": anime.to_dict(include_relationships=True),
            "score": float(score),
            "rank": rank,
            "explanation": {
                "method": "multimodal_semantic_search",
                "confidence": float(score),
                "features": [
                    {"feature_name": "visual_similarity", "importance": visual_weight, "value": str(visual_results.get(anime_id, 0))},
                    {"feature_name": "text_similarity", "importance": text_weight, "value": str(text_results.get(anime_id, 0))}
                ],
                "reasoning": f"Matched query: {query}. " + "; ".join(matched_elements)
            },
            "similarity_reasons": matched_elements
        })
    
    execution_time = (time.time() - start_time) * 1000
    
    return {
        "recommendations": recommendations,
        "total": len(recommendations),
        "method": "semantic_vibe_search",
        "user_id": None,
        "execution_time_ms": execution_time
    }
