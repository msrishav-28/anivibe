"""
Rating endpoints for Supabase
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from uuid import UUID

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.rating import Rating
from app.models.anime import Anime

router = APIRouter()


# Request/Response schemas (inline for simplicity)
from pydantic import BaseModel, Field


class RatingCreate(BaseModel):
    anime_id: int
    score: float = Field(..., ge=1, le=10)
    review: Optional[str] = None


class RatingUpdate(BaseModel):
    score: Optional[float] = Field(None, ge=1, le=10)
    review: Optional[str] = None


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_rating(
    rating_data: RatingCreate,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new rating
    """
    user_id = UUID(current_user["id"])
    
    # Check if anime exists
    anime_result = await db.execute(
        select(Anime).filter(Anime.id == rating_data.anime_id)
    )
    anime = anime_result.scalar_one_or_none()
    if not anime:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Anime not found"
        )
    
    # Check if rating already exists
    existing_result = await db.execute(
        select(Rating).filter(
            and_(
                Rating.user_id == user_id,
                Rating.anime_id == rating_data.anime_id
            )
        )
    )
    if existing_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating already exists. Use PUT to update."
        )
    
    # Create rating
    rating = Rating(
        user_id=user_id,
        anime_id=rating_data.anime_id,
        score=rating_data.score,
        review=rating_data.review
    )
    
    db.add(rating)
    await db.commit()
    await db.refresh(rating)
    
    return rating.to_dict()


@router.get("/")
async def get_user_ratings(
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Get current user's ratings
    """
    user_id = UUID(current_user["id"])
    
    result = await db.execute(
        select(Rating)
        .filter(Rating.user_id == user_id)
        .order_by(Rating.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    ratings = result.scalars().all()
    
    return [r.to_dict() for r in ratings]


@router.get("/{rating_id}")
async def get_rating(
    rating_id: int,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific rating
    """
    user_id = UUID(current_user["id"])
    
    result = await db.execute(
        select(Rating).filter(
            and_(
                Rating.id == rating_id,
                Rating.user_id == user_id
            )
        )
    )
    rating = result.scalar_one_or_none()
    
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found"
        )
    
    return rating.to_dict()


@router.put("/{rating_id}")
async def update_rating(
    rating_id: int,
    rating_update: RatingUpdate,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a rating
    """
    user_id = UUID(current_user["id"])
    
    result = await db.execute(
        select(Rating).filter(
            and_(
                Rating.id == rating_id,
                Rating.user_id == user_id
            )
        )
    )
    rating = result.scalar_one_or_none()
    
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found"
        )
    
    # Update fields
    for field, value in rating_update.dict(exclude_unset=True).items():
        setattr(rating, field, value)
    
    await db.commit()
    await db.refresh(rating)
    
    return rating.to_dict()


@router.delete("/{rating_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rating(
    rating_id: int,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a rating
    """
    user_id = UUID(current_user["id"])
    
    result = await db.execute(
        select(Rating).filter(
            and_(
                Rating.id == rating_id,
                Rating.user_id == user_id
            )
        )
    )
    rating = result.scalar_one_or_none()
    
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found"
        )
    
    await db.delete(rating)
    await db.commit()
    
    return None
