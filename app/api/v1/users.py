"""
User management endpoints for Supabase
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from uuid import UUID

from app.core.database import get_db, get_supabase
from app.core.security import get_current_user, get_current_active_user
from app.models.user import Profile
from app.models.rating import Rating
from app.models.watchlist import WatchlistEntry
from app.schemas.user import UserResponse, UserUpdate
from supabase import Client

router = APIRouter()


@router.get("/me")
async def get_current_user_profile(
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user profile from database
    """
    user_id = UUID(current_user["id"])
    
    result = await db.execute(
        select(Profile).filter(Profile.id == user_id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        # Return data from auth if profile not in DB yet
        return current_user
    
    return profile.to_dict()


@router.put("/me")
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update current user profile
    """
    user_id = UUID(current_user["id"])
    
    result = await db.execute(
        select(Profile).filter(Profile.id == user_id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    # Update profile fields
    for field, value in user_update.dict(exclude_unset=True).items():
        if hasattr(profile, field):
            setattr(profile, field, value)
    
    await db.commit()
    await db.refresh(profile)
    
    return profile.to_dict()


@router.post("/me/avatar")
async def upload_avatar(
    avatar: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    supabase: Client = Depends(get_supabase)
):
    """
    Upload user avatar
    """
    user_id = current_user["id"]
    
    # 1. Read file
    file_content = await avatar.read()
    file_ext = avatar.filename.split(".")[-1] if "." in avatar.filename else "jpg"
    file_path = f"{user_id}/avatar.{file_ext}" 
    
    # 2. Upload to Supabase Storage
    try:
        # Assumes 'avatars' bucket exists. If not, create it manually in Supabase Dashboard.
        res = supabase.storage.from_("avatars").upload(
            file_path,
            file_content,
            {"content-type": avatar.content_type or "image/jpeg", "upsert": "true"}
        )
        
        # 3. Get Public URL
        public_url = supabase.storage.from_("avatars").get_public_url(file_path)
        
        # 4. Update Profile
        await db.execute(
            update(Profile).where(Profile.id == UUID(user_id)).values(avatar_url=public_url)
        )
        await db.commit()
        
        return public_url
        
    except Exception as e:
        # Log error
        import logging
        logging.error(f"Avatar upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/{user_id}")
async def get_user_by_id(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get user by ID (public profile)
    """
    try:
        uid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    result = await db.execute(
        select(Profile).filter(Profile.id == uid, Profile.is_active == True)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return profile.to_dict()


@router.get("/{user_id}/stats")
async def get_user_statistics(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get user statistics
    """
    try:
        uid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )
    
    # Get user profile
    result = await db.execute(
        select(Profile).filter(Profile.id == uid)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get ratings count and average
    ratings_result = await db.execute(
        select(
            func.count(Rating.id),
            func.avg(Rating.score)
        ).filter(Rating.user_id == uid)
    )
    ratings_count, avg_rating = ratings_result.one()
    
    # Get watchlist stats
    watchlist_result = await db.execute(
        select(func.count(WatchlistEntry.id))
        .filter(WatchlistEntry.user_id == uid)
    )
    watchlist_count = watchlist_result.scalar()
    
    # Get watchlist by status
    status_counts = {}
    for status_name in ["plan_to_watch", "watching", "completed", "on_hold", "dropped"]:
        result = await db.execute(
            select(func.count(WatchlistEntry.id))
            .filter(
                WatchlistEntry.user_id == uid,
                WatchlistEntry.status == status_name
            )
        )
        status_counts[status_name] = result.scalar() or 0
    
    return {
        "user_id": str(uid),
        "username": profile.username,
        "anime_watched": profile.anime_watched,
        "episodes_watched": profile.episodes_watched,
        "watch_time_hours": profile.watch_time_hours,
        "ratings_count": ratings_count or 0,
        "average_rating": float(avg_rating) if avg_rating else 0.0,
        "watchlist_total": watchlist_count or 0,
        "watchlist_by_status": status_counts,
        "member_since": profile.created_at.isoformat() if profile.created_at else None
    }


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    supabase: Client = Depends(get_supabase)
):
    """
    Delete current user account
    Note: This only deletes the profile. Supabase auth user deletion requires admin API.
    """
    user_id = UUID(current_user["id"])
    
    result = await db.execute(
        select(Profile).filter(Profile.id == user_id)
    )
    profile = result.scalar_one_or_none()
    
    if profile:
        await db.delete(profile)
        await db.commit()
    
    return None
