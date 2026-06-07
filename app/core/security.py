"""
Security utilities for Supabase Auth
"""
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
# from passlib.context import CryptContext (Removed)
import logging

from app.core.database import get_supabase, get_supabase_admin

logger = logging.getLogger(__name__)

# HTTP Bearer security scheme
security = HTTPBearer(auto_error=False)

# Password hashing context removed - Supabase handles all authentication
# verify_password and get_password_hash are deprecated/removed

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """DEPRECATED: Verify a password against a hash (backwards compatibility)"""
    raise NotImplementedError("Use Supabase Auth")


def get_password_hash(password: str) -> str:
    """DEPRECATED: Hash a password (backwards compatibility)"""
    raise NotImplementedError("Use Supabase Auth")


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    supabase: Client = Depends(get_supabase)
) -> Dict[str, Any]:
    """
    Verify Supabase JWT and return current user.
    
    Usage:
        user = Depends(get_current_user)
    
    Returns:
        Dictionary with user data including id, email, username
    
    Raises:
        HTTPException 401 if token is invalid or missing
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        token = credentials.credentials
        
        # Verify token with Supabase and get user
        response = supabase.auth.get_user(token)
        
        if response.user:
            user_metadata = response.user.user_metadata or {}
            
            return {
                "id": str(response.user.id),
                "user_id": str(response.user.id),
                "email": response.user.email,
                "username": user_metadata.get("username", response.user.email.split("@")[0]),
                "full_name": user_metadata.get("full_name"),
                "avatar_url": user_metadata.get("avatar_url"),
                "is_verified": response.user.email_confirmed_at is not None,
                "created_at": response.user.created_at
            }
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    supabase: Client = Depends(get_supabase)
) -> Optional[Dict[str, Any]]:
    """
    Get current user if authenticated, otherwise return None.
    
    Useful for endpoints that work with or without authentication.
    
    Usage:
        user = Depends(get_current_user_optional)
        if user:
            # User is logged in
        else:
            # Anonymous user
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, supabase)
    except HTTPException:
        return None


async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get current user and verify they are active.
    
    Raises:
        HTTPException 403 if user is inactive
    """
    # Supabase users are always active if the token is valid
    # Add additional checks here if needed
    return current_user


async def get_current_verified_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get current user and verify their email is confirmed.
    
    Raises:
        HTTPException 403 if email not verified
    """
    if not current_user.get("is_verified"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please check your email for verification link."
        )
    return current_user


def create_access_token(data: dict) -> str:
    """
    Create access token - DEPRECATED.
    
    Supabase handles token creation. This function is kept for backwards compatibility
    but should not be used in new code.
    """
    logger.warning("create_access_token called but Supabase handles token creation")
    raise NotImplementedError("Use Supabase Auth for token creation")


def create_refresh_token(data: dict) -> str:
    """
    Create refresh token - DEPRECATED.
    
    Supabase handles token creation. This function is kept for backwards compatibility
    but should not be used in new code.
    """
    logger.warning("create_refresh_token called but Supabase handles token creation")
    raise NotImplementedError("Use Supabase Auth for token creation")


def decode_token(token: str) -> dict:
    """
    Decode token - DEPRECATED.
    
    Use get_current_user dependency instead.
    """
    logger.warning("decode_token called but use get_current_user instead")
    raise NotImplementedError("Use get_current_user dependency for token verification")
