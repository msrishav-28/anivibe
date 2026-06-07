"""
Rating model for Supabase
"""
from datetime import datetime
from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Rating(Base):
    """User anime rating model"""
    
    __tablename__ = "ratings"
    __table_args__ = (
        UniqueConstraint('user_id', 'anime_id', name='unique_user_anime_rating'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys - user_id is UUID (Supabase auth.users)
    user_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id', ondelete='CASCADE'), nullable=False, index=True)
    anime_id = Column(Integer, ForeignKey('anime.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Rating
    score = Column(Float, nullable=False)  # 1-10 scale
    
    # Review
    review = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("Profile", back_populates="ratings")
    anime = relationship("Anime", back_populates="ratings")
    
    def __repr__(self):
        return f"<Rating(user_id={self.user_id}, anime_id={self.anime_id}, score={self.score})>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": str(self.user_id),
            "anime_id": self.anime_id,
            "score": self.score,
            "review": self.review,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
