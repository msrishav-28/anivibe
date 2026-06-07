"""
Authentication endpoints using Supabase Auth
"""
from fastapi import APIRouter, HTTPException, status, Depends, Response, Request
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from supabase import Client
import logging

from app.core.database import get_supabase

router = APIRouter()
logger = logging.getLogger(__name__)


# ===========================================
# REQUEST/RESPONSE SCHEMAS
# ===========================================

class SignUpRequest(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)


class LoginRequest(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema for authentication token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class RefreshTokenRequest(BaseModel):
    """Schema for token refresh"""
    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Schema for password reset request"""
    email: EmailStr


class PasswordUpdateRequest(BaseModel):
    """Schema for password update"""
    new_password: str = Field(..., min_length=8, max_length=100)


# ===========================================
# AUTHENTICATION ENDPOINTS
# ===========================================

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    data: SignUpRequest,
    supabase: Client = Depends(get_supabase)
):
    """
    Register a new user with Supabase Auth.
    
    Creates a user account and triggers profile creation via database trigger.
    """
    try:
        # Sign up with Supabase Auth
        response = supabase.auth.sign_up({
            "email": data.email,
            "password": data.password,
            "options": {
                "data": {
                    "username": data.username,
                    "full_name": data.full_name or ""
                }
            }
        })
        
        if response.user:
            logger.info(f"User registered: {data.email}")
            return {
                "id": str(response.user.id),
                "user_id": str(response.user.id),
                "email": response.user.email,
                "username": data.username,
                "message": "Registration successful. Please check your email for verification."
            }
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed. Please try again."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        error_msg = str(e)
        if "already registered" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    response: Response,  # Inject Response object
    supabase: Client = Depends(get_supabase)
):
    """
    Login with email and password using Supabase Auth.
    
    Sets HttpOnly cookies for access and refresh tokens.
    """
    try:
        # Sign in with Supabase Auth
        sb_response = supabase.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password
        })
        
        if sb_response.user and sb_response.session:
            user_metadata = sb_response.user.user_metadata or {}
            
            # Set cookies
            response.set_cookie(
                key="access_token",
                value=sb_response.session.access_token,
                httponly=True,
                secure=True,  # Requires HTTPS
                samesite="lax",
                max_age=3600  # 1 hour
            )
            response.set_cookie(
                key="refresh_token",
                value=sb_response.session.refresh_token,
                httponly=True,
                secure=True,
                samesite="lax",
                max_age=30 * 24 * 3600  # 30 days
            )
            
            logger.info(f"User logged in: {data.email}")
            return {
                "access_token": sb_response.session.access_token, # Sent for client store if needed (deprecated)
                "refresh_token": sb_response.session.refresh_token,
                "token_type": "bearer",
                "user": {
                    "id": str(sb_response.user.id),
                    "user_id": str(sb_response.user.id),
                    "email": sb_response.user.email,
                    "username": user_metadata.get("username", data.email.split("@")[0]),
                    "full_name": user_metadata.get("full_name"),
                    "avatar_url": user_metadata.get("avatar_url"),
                    "created_at": sb_response.user.created_at
                }
            }
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )


@router.post("/refresh")
async def refresh_token(
    data: RefreshTokenRequest,
    response: Response,
    supabase: Client = Depends(get_supabase)
):
    """
    Refresh access token using refresh token.
    Rotates cookies.
    """
    try:
        sb_response = supabase.auth.refresh_session(data.refresh_token)
        
        if sb_response.session:
            # Set cookies
            response.set_cookie(
                key="access_token",
                value=sb_response.session.access_token,
                httponly=True,
                secure=True,
                samesite="lax",
                max_age=3600
            )
            response.set_cookie(
                key="refresh_token",
                value=sb_response.session.refresh_token,
                httponly=True,
                secure=True,
                samesite="lax",
                max_age=30 * 24 * 3600
            )
            
            return {
                "access_token": sb_response.session.access_token,
                "refresh_token": sb_response.session.refresh_token,
                "token_type": "bearer"
            }
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )


@router.post("/logout")
async def logout(
    response: Response,
    supabase: Client = Depends(get_supabase)
):
    """
    Logout user, invalidate session, and clear cookies.
    """
    try:
        supabase.auth.sign_out()
        response.delete_cookie(key="access_token")
        response.delete_cookie(key="refresh_token")
        return {"message": "Successfully logged out"}
    except Exception as e:
        logger.error(f"Logout error: {e}")
        response.delete_cookie(key="access_token")
        response.delete_cookie(key="refresh_token")
        return {"message": "Successfully logged out"}


@router.post("/password-reset")
async def request_password_reset(
    data: PasswordResetRequest,
    supabase: Client = Depends(get_supabase)
):
    """
    Request password reset email.
    """
    try:
        supabase.auth.reset_password_email(data.email)
        return {
            "message": "If an account exists with this email, a password reset link has been sent."
        }
    except Exception as e:
        logger.error(f"Password reset request error: {e}")
        # Always return success to prevent email enumeration
        return {
            "message": "If an account exists with this email, a password reset link has been sent."
        }


@router.post("/password-update")
async def update_password(
    data: PasswordUpdateRequest,
    supabase: Client = Depends(get_supabase)
):
    """
    Update user password (requires authenticated session).
    """
    try:
        response = supabase.auth.update_user({
            "password": data.new_password
        })
        
        if response.user:
            return {"message": "Password updated successfully"}
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password update failed"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password update error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
