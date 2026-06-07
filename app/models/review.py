"""
Review models
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Text, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    anime_id = Column(Integer, ForeignKey("anime.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200))
    content = Column(Text, nullable=False)
    rating = Column(Float)
    sentiment = Column(String(20))
    helpful_count = Column(Integer, default=0)
    is_spoiler = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("Profile", backref="reviews")
    anime = relationship("Anime")
    votes = relationship("ReviewVote", back_populates="review", cascade="all, delete-orphan")

class ReviewVote(Base):
    __tablename__ = "review_votes"
    
    review_id = Column(Integer, ForeignKey("reviews.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), primary_key=True)
    is_helpful = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    review = relationship("Review", back_populates="votes")
