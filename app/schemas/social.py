"""
Social feature schemas
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from app.schemas.anime import AnimeResponse

class UserBasic(BaseModel):
    id: str
    username: string
    avatar_url: Optional[str] = None
    
    class Config:
        from_attributes = True

class FriendResponse(BaseModel):
    user_id: str
    username: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    taste_affinity: float = 0.0
    mutual_anime: int = 0
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class FriendRequest(BaseModel):
    user_id: str

class ActivityResponse(BaseModel):
    activity_id: int = Field(alias="id")
    user_id: str
    user: Dict[str, Any]  # username, avatar
    type: str
    anime_id: Optional[int] = None
    anime: Optional[AnimeResponse] = None
    metadata: Optional[Dict[str, Any]] = {}
    created_at: datetime
    
    class Config:
        from_attributes = True
