"""
Collaborative filtering implementation
Uses user-user similarity and item-item similarity
"""
import logging
from typing import Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from app.models.rating import Rating

logger = logging.getLogger(__name__)


async def get_collaborative_recommendations(
    user_id: str,
    user_ratings: Dict[int, float],
    top_k: int = 20,
    db: AsyncSession = None
) -> Dict[int, float]:
    """
    Get collaborative filtering recommendations
    
    Args:
        user_id: Target user ID
        user_ratings: Dictionary of anime_id -> score for target user
        top_k: Number of recommendations
        db: Database session
    
    Returns:
        Dictionary mapping anime_id to recommendation score
    """
    if not user_ratings:
        return {}
    
    try:
        # Get all ratings from database
        result = await db.execute(select(Rating))
        all_ratings = result.scalars().all()
        
        if not all_ratings:
            return {}
        
        # Build user-item matrix
        user_ids = set()
        anime_ids = set()
        
        for rating in all_ratings:
            user_ids.add(rating.user_id)
            anime_ids.add(rating.anime_id)
        
        user_id_list = sorted(list(user_ids))
        anime_id_list = sorted(list(anime_ids))
        
        user_id_to_idx = {uid: idx for idx, uid in enumerate(user_id_list)}
        anime_id_to_idx = {aid: idx for idx, aid in enumerate(anime_id_list)}
        
        # Create rating matrix
        rating_matrix = np.zeros((len(user_ids), len(anime_ids)))
        
        for rating in all_ratings:
            user_idx = user_id_to_idx[rating.user_id]
            anime_idx = anime_id_to_idx[rating.anime_id]
            rating_matrix[user_idx, anime_idx] = rating.score
        
        # Find similar users
        target_user_idx = user_id_to_idx.get(user_id)
        if target_user_idx is None:
            return {}
        
        target_user_vector = rating_matrix[target_user_idx:target_user_idx+1]
        
        # Calculate user similarity (cosine)
        user_similarities = cosine_similarity(target_user_vector, rating_matrix)[0]
        
        # Get top similar users (excluding self)
        similar_user_indices = np.argsort(user_similarities)[::-1][1:51]  # Top 50 similar users
        
        # Weighted average of similar users' ratings
        recommendations = {}
        
        for anime_idx, anime_id in enumerate(anime_id_list):
            # Skip if user already rated
            if anime_id in user_ratings:
                continue
            
            # Calculate weighted score from similar users
            weighted_sum = 0
            similarity_sum = 0
            
            for similar_user_idx in similar_user_indices:
                rating = rating_matrix[similar_user_idx, anime_idx]
                if rating > 0:
                    similarity = user_similarities[similar_user_idx]
                    weighted_sum += rating * similarity
                    similarity_sum += similarity
            
            if similarity_sum > 0:
                recommendations[anime_id] = weighted_sum / similarity_sum
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Collaborative filtering failed: {e}")
        return {}
