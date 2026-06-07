"""
Anime management endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.cache import cache_get, cache_set
from app.models.anime import Anime, Genre, Studio, Tag
from app.schemas.anime import AnimeResponse, AnimeSearch, GenreResponse, StudioResponse, TagResponse

router = APIRouter()


@router.get("/{anime_id}", response_model=AnimeResponse)
async def get_anime_by_id(
    anime_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get anime by ID
    """
    # Try cache first
    cache_key = f"anime:{anime_id}"
    cached = await cache_get(cache_key)
    if cached:
        return cached
    
    # Query database with relationships
    result = await db.execute(
        select(Anime)
        .options(
            selectinload(Anime.genres),
            selectinload(Anime.studios),
            selectinload(Anime.tags)
        )
        .filter(Anime.id == anime_id)
    )
    anime = result.scalar_one_or_none()
    
    if not anime:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Anime not found"
        )
    
    # Cache result
    anime_dict = anime.to_dict(include_relationships=True)
    await cache_set(cache_key, anime_dict, expire=3600)
    
    return anime_dict


@router.get("/", response_model=dict)
async def search_anime(
    search: AnimeSearch = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Search and filter anime
    """
    query = select(Anime).options(
        selectinload(Anime.genres),
        selectinload(Anime.studios),
        selectinload(Anime.tags)
    )
    
    # Apply filters
    conditions = []
    
    if search.query:
        conditions.append(
            or_(
                Anime.title.ilike(f"%{search.query}%"),
                Anime.title_english.ilike(f"%{search.query}%"),
                Anime.title_japanese.ilike(f"%{search.query}%")
            )
        )
    
    if search.type:
        conditions.append(Anime.type == search.type)
    
    if search.status:
        conditions.append(Anime.status == search.status)
    
    if search.year_from:
        conditions.append(Anime.year >= search.year_from)
    
    if search.year_to:
        conditions.append(Anime.year <= search.year_to)
    
    if search.score_min:
        conditions.append(Anime.score >= search.score_min)
    
    if search.score_max:
        conditions.append(Anime.score <= search.score_max)
    
    if search.episodes_min:
        conditions.append(Anime.episodes >= search.episodes_min)
    
    if search.episodes_max:
        conditions.append(Anime.episodes <= search.episodes_max)
    
    if conditions:
        query = query.filter(and_(*conditions))
    
    # Apply ordering
    if search.order_by == "score":
        order_col = Anime.score
    elif search.order_by == "popularity":
        order_col = Anime.popularity
    elif search.order_by == "members":
        order_col = Anime.members
    elif search.order_by == "year":
        order_col = Anime.year
    else:
        order_col = Anime.score
    
    if search.sort == "desc":
        query = query.order_by(order_col.desc().nullslast())
    else:
        query = query.order_by(order_col.asc().nullsfirst())
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    offset = (search.page - 1) * search.limit
    query = query.offset(offset).limit(search.limit)
    
    # Execute query
    result = await db.execute(query)
    anime_list = result.scalars().all()
    
    pages = (total + search.limit - 1) // search.limit if total else 0
    anime_data = [a.to_dict(include_relationships=True) for a in anime_list]
    
    return {
        "items": anime_data,  # Frontend convention
        "results": anime_data,  # Backward compatibility
        "total": total,
        "page": search.page,
        "limit": search.limit,
        "pages": pages,
        "has_next": search.page < pages,
        "has_prev": search.page > 1
    }


@router.get("/genres/", response_model=List[GenreResponse])
async def list_genres(
    db: AsyncSession = Depends(get_db)
):
    """
    List all genres
    """
    cache_key = "genres:all"
    cached = await cache_get(cache_key)
    if cached:
        return cached
    
    result = await db.execute(select(Genre).order_by(Genre.name))
    genres = result.scalars().all()
    
    genre_list = [g.to_dict() for g in genres]
    await cache_set(cache_key, genre_list, expire=7200)
    
    return genre_list


@router.get("/studios/", response_model=List[StudioResponse])
async def list_studios(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(100, ge=1, le=500)
):
    """
    List all studios
    """
    result = await db.execute(
        select(Studio).order_by(Studio.name).limit(limit)
    )
    studios = result.scalars().all()
    
    return [s.to_dict() for s in studios]


@router.get("/tags/", response_model=List[TagResponse])
async def list_tags(
    db: AsyncSession = Depends(get_db),
    category: str = Query(None, description="Filter by category"),
    limit: int = Query(200, ge=1, le=1000)
):
    """
    List all tags
    """
    query = select(Tag)
    
    if category:
        query = query.filter(Tag.category == category)
    
    query = query.order_by(Tag.name).limit(limit)
    
    result = await db.execute(query)
    tags = result.scalars().all()
    
    return [t.to_dict() for t in tags]


@router.get("/random/", response_model=AnimeResponse)
async def get_random_anime(
    db: AsyncSession = Depends(get_db),
    min_score: float = Query(7.0, ge=0, le=10)
):
    """
    Get a random anime
    """
    result = await db.execute(
        select(Anime)
        .options(
            selectinload(Anime.genres),
            selectinload(Anime.studios),
            selectinload(Anime.tags)
        )
        .filter(Anime.score >= min_score)
        .order_by(func.random())
        .limit(1)
    )
    anime = result.scalar_one_or_none()
    
    if not anime:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No anime found"
        )
    
    return anime.to_dict(include_relationships=True)


@router.get("/trending", response_model=dict)
async def get_trending_anime(
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """
    Get trending anime (based on recent popularity/activity)
    Mapping to Search Logic: Sort by Popularity Descending
    """
    # Reuse search logic manually or call internal function (cleaner to query direct)
    query = select(Anime).options(
        selectinload(Anime.genres),
        selectinload(Anime.studios),
        selectinload(Anime.tags)
    ).order_by(Anime.popularity.asc()).limit(limit) # Lower popularity number = more popular usually in MAL, but let's assume 'members' desc
    
    # Actually 'popularity' field in MAL is ranking (1 is best). So ASC is correct.
    
    result = await db.execute(query)
    anime_list = result.scalars().all()
    anime_data = [a.to_dict(include_relationships=True) for a in anime_list]
    
    return {
        "items": anime_data,
        "total": len(anime_data)
    }


@router.get("/popular", response_model=dict)
async def get_popular_anime(
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all-time popular anime
    """
    query = select(Anime).options(
        selectinload(Anime.genres),
        selectinload(Anime.studios),
        selectinload(Anime.tags)
    ).order_by(Anime.members.desc()).limit(limit)
    
    result = await db.execute(query)
    anime_list = result.scalars().all()
    anime_data = [a.to_dict(include_relationships=True) for a in anime_list]
    
    return {
        "items": anime_data,
        "total": len(anime_data)
    }
