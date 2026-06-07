"""
User schemas for Supabase
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    """Schema for creating a new user (Supabase signup)"""
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = Field(None, max_length=100)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength"""
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        return v


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Schema for updating user profile"""
    full_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None
    preferred_language: Optional[str] = Field(None, max_length=10)
    show_nsfw: Optional[bool] = None
    mal_username: Optional[str] = Field(None, max_length=100)
    anilist_username: Optional[str] = Field(None, max_length=100)


class UserResponse(BaseModel):
    """Schema for user response (Supabase UUID)"""
    id: str  # UUID as string
    user_id: Optional[str] = None  # Alias for frontend compatibility
    username: str
    email: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    mal_username: Optional[str] = None
    anilist_username: Optional[str] = None
    anime_watched: int = 0
    episodes_watched: int = 0
    watch_time_hours: float = 0.0
    preferred_language: Optional[str] = "en"
    show_nsfw: bool = False
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    @field_validator('user_id', mode='before')
    @classmethod
    def set_user_id(cls, v, info):
        """Set user_id from id for frontend compatibility"""
        return v or info.data.get('id')
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for authentication token"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenWithUser(BaseModel):
    """Schema for authentication token with user data (for login response)"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: Optional[dict] = None  # User data as dict


class TokenPayload(BaseModel):
    """Schema for token payload (Supabase UUID)"""
    sub: Optional[str] = None  # UUID as string
    exp: Optional[int] = None
    type: Optional[str] = None


class PasswordReset(BaseModel):
    """Schema for password reset"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)
