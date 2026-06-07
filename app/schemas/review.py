"""
Review schemas
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class ReviewBase(BaseModel):
    title: Optional[str] = None
    content: str
    rating: float = Field(..., ge=1, le=10)
    is_spoiler: bool = False

class ReviewCreate(ReviewBase):
    pass

class ReviewUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    rating: Optional[float] = Field(None, ge=1, le=10)
    is_spoiler: Optional[bool] = None

class ReviewVoteRequest(BaseModel):
    helpful: bool

class ReviewResponse(ReviewBase):
    review_id: int = Field(alias="id")
    user_id: str
    user: Dict[str, Any]
    anime_id: int
    sentiment: Optional[str] = None
    helpful_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
