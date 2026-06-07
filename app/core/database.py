"""
Pure Supabase database connection
"""
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from supabase import create_client, Client
import logging

from config import settings

logger = logging.getLogger(__name__)

# SQLAlchemy Base
Base = declarative_base()

# Supabase clients
supabase: Optional[Client] = None
supabase_admin: Optional[Client] = None

# SQLAlchemy engine
engine = None
AsyncSessionLocal = None


async def init_db():
    """Initialize Supabase connections"""
    global supabase, supabase_admin, engine, AsyncSessionLocal
    
    try:
        # Supabase client (respects RLS)
        supabase = create_client(
            settings.supabase_url,
            settings.supabase_anon_key
        )
        logger.info("✓ Supabase client initialized")
        
        # Supabase admin (bypasses RLS for server operations)
        supabase_admin = create_client(
            settings.supabase_url,
            settings.supabase_service_key
        )
        logger.info("✓ Supabase admin client initialized")
        
        # SQLAlchemy async engine for complex queries
        engine = create_async_engine(
            settings.database_url,
            echo=settings.debug,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        
        AsyncSessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        
        logger.info("✓ SQLAlchemy engine connected to Supabase")
        
        # Test connection
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        
        logger.info("✓ Database connection verified")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise


async def close_db():
    """Close connections"""
    global engine
    
    if engine:
        await engine.dispose()
        logger.info("Database connections closed")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for async database sessions.
    
    Usage:
        @router.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            ...
    """
    if AsyncSessionLocal is None:
        raise RuntimeError("Database not initialized")
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_supabase() -> Client:
    """Get Supabase client (respects RLS)"""
    if supabase is None:
        raise RuntimeError("Supabase not initialized")
    return supabase


def get_supabase_admin() -> Client:
    """Get Supabase admin client (bypasses RLS)"""
    if supabase_admin is None:
        raise RuntimeError("Supabase admin not initialized")
    return supabase_admin
