"""
Review API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.review import Review, ReviewVote
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewVoteRequest, ReviewResponse

router = APIRouter()

@router.get("/anime/{anime_id}/reviews", response_model=dict)
async def get_anime_reviews(
    anime_id: int,
    page: int = 1,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Get reviews for an anime"""
    query = select(Review).options(selectinload(Review.user))\
        .filter(Review.anime_id == anime_id)\
        .order_by(desc(Review.created_at))\
        .offset((page - 1) * limit)\
        .limit(limit)
        
    result = await db.execute(query)
    reviews = result.scalars().all()
    
    # Needs explicit conversion to schemas or custom dict because of User relation
    reviews_data = []
    for r in reviews:
        reviews_data.append({
            "id": r.id,
            "user_id": str(r.user_id),
            "user": {
                "username": r.user.username,
                "avatar_url": r.user.avatar_url
            },
            "anime_id": r.anime_id,
            "title": r.title,
            "content": r.content,
            "rating": r.rating,
            "sentiment": r.sentiment,
            "helpful_count": r.helpful_count,
            "is_spoiler": r.is_spoiler,
            "created_at": r.created_at,
            "updated_at": r.updated_at
        })

    # Count
    from sqlalchemy import func
    count_query = select(func.count()).select_from(Review).filter(Review.anime_id == anime_id)
    total = (await db.execute(count_query)).scalar()

    return {
        "items": reviews_data,
        "total": total,
        "page": page,
        "limit": limit,
        "has_next": page * limit < total,
        "has_prev": page > 1
    }

@router.post("/anime/{anime_id}/reviews", response_model=ReviewResponse)
async def create_review(
    anime_id: int,
    review: ReviewCreate,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new review"""
    user_id = UUID(current_user["id"])
    
    # Check if exists
    existing = await db.execute(select(Review).filter(Review.user_id == user_id, Review.anime_id == anime_id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Review already exists")
        
    db_review = Review(
        user_id=user_id,
        anime_id=anime_id,
        **review.model_dump()
    )
    db.add(db_review)
    await db.commit()
    await db.refresh(db_review)
    
    # Eager load user for response
    # Or just mock it since we know current user
    # Or reload
    query = select(Review).options(selectinload(Review.user)).filter(Review.id == db_review.id)
    db_review = (await db.execute(query)).scalar_one()
    
    return db_review

@router.patch("/reviews/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: int,
    review_update: ReviewUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a review"""
    user_id = UUID(current_user["id"])
    
    query = select(Review).options(selectinload(Review.user)).filter(Review.id == review_id)
    db_review = (await db.execute(query)).scalar_one_or_none()
    
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")
        
    if db_review.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    update_data = review_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_review, key, value)
        
    await db.commit()
    await db.refresh(db_review)
    return db_review

@router.delete("/reviews/{review_id}")
async def delete_review(
    review_id: int,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a review"""
    user_id = UUID(current_user["id"])
    
    db_review = await db.get(Review, review_id)
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")
        
    if db_review.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    await db.delete(db_review)
    await db.commit()
    
    return {"message": "Review deleted"}

@router.post("/reviews/{review_id}/vote")
async def vote_review(
    review_id: int,
    vote: ReviewVoteRequest,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Vote on a review (helpful/not helpful)"""
    user_id = UUID(current_user["id"])
    
    # Check review exists
    if not await db.get(Review, review_id):
        raise HTTPException(status_code=404, detail="Review not found")
        
    # Check existing vote
    existing_vote = await db.get(ReviewVote, (review_id, user_id))
    
    if existing_vote:
        existing_vote.is_helpful = vote.helpful
    else:
        new_vote = ReviewVote(review_id=review_id, user_id=user_id, is_helpful=vote.helpful)
        db.add(new_vote)
        
    await db.commit()
    
    # Update helpful count on review (could be done via trigger or here)
    count_query = select(func.count()).filter(ReviewVote.review_id == review_id, ReviewVote.is_helpful == True)
    helpful_count = (await db.execute(count_query)).scalar()
    
    await db.execute(
        update(Review).where(Review.id == review_id).values(helpful_count=helpful_count)
    )
    await db.commit()
    
    return {"message": "Vote recorded"}
