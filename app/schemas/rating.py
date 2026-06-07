"""
Rating schemas for Supabase
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class RatingBase(BaseModel):
    """Base rating schema"""
    anime_id: int = Field(..., description="Anime ID")
    score: float = Field(..., ge=1, le=10, description="Rating score (1-10)")


class RatingCreate(RatingBase):
    """Schema for creating a rating"""
    review: Optional[str] = Field(None, max_length=5000, description="Review text")


class RatingUpdate(BaseModel):
    """Schema for updating a rating"""
    score: Optional[float] = Field(None, ge=1, le=10)
    review: Optional[str] = Field(None, max_length=5000)


class RatingResponse(RatingBase):
    """Rating response schema (Supabase UUID user)"""
    id: int
    user_id: str  # UUID as string
    review: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RatingWithAnime(RatingResponse):
    """Rating response with anime details"""
    anime: Optional[dict] = None


class BulkRatingCreate(BaseModel):
    """Schema for bulk rating creation"""
    ratings: List[RatingCreate] = Field(..., max_length=100)
