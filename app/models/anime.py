"""
Anime and related models
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, Table, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
import enum

from app.core.database import Base


# Association tables for many-to-many relationships
anime_genres = Table(
    'anime_genres',
    Base.metadata,
    Column('anime_id', Integer, ForeignKey('anime.id', ondelete='CASCADE')),
    Column('genre_id', Integer, ForeignKey('genres.id', ondelete='CASCADE'))
)

anime_studios = Table(
    'anime_studios',
    Base.metadata,
    Column('anime_id', Integer, ForeignKey('anime.id', ondelete='CASCADE')),
    Column('studio_id', Integer, ForeignKey('studios.id', ondelete='CASCADE'))
)

anime_tags = Table(
    'anime_tags',
    Base.metadata,
    Column('anime_id', Integer, ForeignKey('anime.id', ondelete='CASCADE')),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'))
)


class AnimeType(str, enum.Enum):
    """Anime type enumeration"""
    TV = "TV"
    MOVIE = "Movie"
    OVA = "OVA"
    ONA = "ONA"
    SPECIAL = "Special"
    MUSIC = "Music"


class AnimeStatus(str, enum.Enum):
    """Anime status enumeration"""
    FINISHED = "Finished Airing"
    AIRING = "Currently Airing"
    NOT_YET = "Not Yet Aired"


class AnimeSeason(str, enum.Enum):
    """Anime season enumeration"""
    WINTER = "Winter"
    SPRING = "Spring"
    SUMMER = "Summer"
    FALL = "Fall"


class Anime(Base):
    """Anime model"""
    
    __tablename__ = "anime"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic information
    title = Column(String(500), nullable=False, index=True)
    title_english = Column(String(500), nullable=True)
    title_japanese = Column(String(500), nullable=True)
    title_synonyms = Column(Text, nullable=True)  # JSON array as text
    
    # External IDs
    mal_id = Column(Integer, unique=True, index=True, nullable=True)
    anilist_id = Column(Integer, unique=True, index=True, nullable=True)
    
    # Content
    synopsis = Column(Text, nullable=True)
    background = Column(Text, nullable=True)
    
    # Media
    image_url = Column(String(500), nullable=True)
    trailer_url = Column(String(500), nullable=True)
    
    # Classification
    type = Column(SQLEnum(AnimeType), nullable=True)
    status = Column(SQLEnum(AnimeStatus), nullable=True)
    
    # Episodes
    episodes = Column(Integer, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    
    # Dates
    aired_from = Column(DateTime, nullable=True)
    aired_to = Column(DateTime, nullable=True)
    season = Column(SQLEnum(AnimeSeason), nullable=True)
    year = Column(Integer, index=True, nullable=True)
    
    # Ratings
    score = Column(Float, nullable=True)  # MAL score
    scored_by = Column(Integer, nullable=True)  # Number of users who scored
    rank = Column(Integer, nullable=True)
    popularity = Column(Integer, nullable=True)
    members = Column(Integer, nullable=True)  # Number of members
    favorites = Column(Integer, nullable=True)
    
    # Content rating
    rating = Column(String(50), nullable=True)  # G, PG, PG-13, R, R+, Rx
    
    # Source material
    source = Column(String(100), nullable=True)  # Manga, Light Novel, Original, etc.
    
    # Flags
    is_nsfw = Column(Boolean, default=False)
    is_hidden_gem = Column(Boolean, default=False)
    
    # Computed fields
    popularity_score = Column(Float, nullable=True)  # Computed score for hidden gem discovery
    
    # Vector Embeddings (PGVector)
    # CLIP ViT-B-32 = 512 dimensions
    embedding_clip = Column(Vector(512), nullable=True)
    # SBERT all-MiniLM-L6-v2 = 384 dimensions
    embedding_sbert = Column(Vector(384), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_synced = Column(DateTime, nullable=True)
    
    # Relationships
    genres = relationship("Genre", secondary=anime_genres, back_populates="anime")
    studios = relationship("Studio", secondary=anime_studios, back_populates="anime")
    tags = relationship("Tag", secondary=anime_tags, back_populates="anime")
    ratings = relationship("Rating", back_populates="anime", cascade="all, delete-orphan")
    watchlist_entries = relationship("WatchlistEntry", back_populates="anime", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Anime(id={self.id}, title='{self.title}')>"
    
    def to_dict(self, include_relationships=False):
        """Convert to dictionary"""
        data = {
            "id": self.id,
            "anime_id": self.id,  # Alias for frontend compatibility
            "title": self.title,
            "title_english": self.title_english,
            "title_japanese": self.title_japanese,
            "mal_id": self.mal_id,
            "anilist_id": self.anilist_id,
            "synopsis": self.synopsis,
            "image_url": self.image_url,
            "trailer_url": self.trailer_url,
            "type": self.type.value if self.type else None,
            "status": self.status.value if self.status else None,
            "episodes": self.episodes,
            "duration_minutes": self.duration_minutes,
            "aired_from": self.aired_from.isoformat() if self.aired_from else None,
            "aired_to": self.aired_to.isoformat() if self.aired_to else None,
            "season": self.season.value if self.season else None,
            "year": self.year,
            "score": self.score,
            "scored_by": self.scored_by,
            "rank": self.rank,
            "popularity": self.popularity,
            "members": self.members,
            "favorites": self.favorites,
            "rating": self.rating,
            "source": self.source,
            "is_nsfw": self.is_nsfw,
            "is_hidden_gem": self.is_hidden_gem
        }
        
        if include_relationships:
            data["genres"] = [g.to_dict() for g in self.genres]
            data["studios"] = [s.to_dict() for s in self.studios]
            data["tags"] = [t.to_dict() for t in self.tags]
        
        return data


class Genre(Base):
    """Genre model"""
    
    __tablename__ = "genres"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    mal_id = Column(Integer, unique=True, nullable=True)
    description = Column(Text, nullable=True)
    
    # Relationships
    anime = relationship("Anime", secondary=anime_genres, back_populates="genres")
    
    def __repr__(self):
        return f"<Genre(id={self.id}, name='{self.name}')>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description
        }


class Studio(Base):
    """Animation studio model"""
    
    __tablename__ = "studios"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False, index=True)
    mal_id = Column(Integer, unique=True, nullable=True)
    established = Column(Integer, nullable=True)  # Year
    
    # Relationships
    anime = relationship("Anime", secondary=anime_studios, back_populates="studios")
    
    def __repr__(self):
        return f"<Studio(id={self.id}, name='{self.name}')>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "established": self.established
        }


class Tag(Base):
    """Tag model for atmospheric/aesthetic descriptors"""
    
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(String(50), nullable=True)  # aesthetic, emotional, narrative, etc.
    description = Column(Text, nullable=True)
    anilist_id = Column(Integer, unique=True, nullable=True)
    
    # Relationships
    anime = relationship("Anime", secondary=anime_tags, back_populates="tags")
    
    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}')>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "description": self.description
        }
