"""
Recommendation schemas for Supabase
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    """Recommendation request schema"""
    user_id: Optional[str] = Field(None, description="User UUID for personalized recommendations")
    top_k: int = Field(10, ge=1, le=50, description="Number of recommendations")
    method: str = Field("hybrid", description="Recommendation method (collaborative, content, hybrid)")
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional filters")
    exclude_watched: bool = Field(True, description="Exclude already watched anime")
    popularity_attenuation: float = Field(0.3, ge=0, le=1, description="Popularity attenuation factor")
    diversity_weight: float = Field(0.2, ge=0, le=1, description="Diversity weight")


class SemanticSearchRequest(BaseModel):
    """Semantic search request schema"""
    query: str = Field(..., description="Natural language search query")
    top_k: int = Field(10, ge=1, le=50)
    use_clip: bool = Field(True, description="Use CLIP for visual search")
    use_sbert: bool = Field(True, description="Use SBERT for text search")
    visual_weight: float = Field(0.4, ge=0, le=1, description="Weight for visual features")
    text_weight: float = Field(0.6, ge=0, le=1, description="Weight for text features")
    filters: Optional[Dict[str, Any]] = None


class SimilarAnimeRequest(BaseModel):
    """Similar anime request schema"""
    anime_id: int = Field(..., description="Anime ID to find similar to")
    top_k: int = Field(10, ge=1, le=50)
    method: str = Field("multimodal", description="Similarity method")


class ExplanationFeature(BaseModel):
    """Feature explanation schema"""
    feature_name: str
    importance: float
    value: Optional[str] = None


class RecommendationExplanation(BaseModel):
    """Recommendation explanation schema"""
    method: str
    confidence: float
    features: List[ExplanationFeature]
    reasoning: str


class RecommendationResponse(BaseModel):
    """Recommendation response schema"""
    anime_id: int
    anime: Dict[str, Any]
    score: float = Field(..., description="Recommendation score")
    rank: int = Field(..., description="Rank in recommendations")
    explanation: Optional[RecommendationExplanation] = None
    similarity_reasons: Optional[List[str]] = None


class RecommendationBatchResponse(BaseModel):
    """Batch recommendation response schema"""
    recommendations: List[RecommendationResponse]
    total: int
    method: str
    user_id: Optional[str] = None  # UUID as string
    execution_time_ms: float


class HiddenGemRequest(BaseModel):
    """Hidden gem discovery request schema"""
    user_id: Optional[str] = None  # UUID as string
    top_k: int = Field(10, ge=1, le=50)
    max_popularity: int = Field(50000, description="Maximum member count")
    min_score: float = Field(7.5, ge=0, le=10, description="Minimum score")
    genres: Optional[List[str]] = None
    tags: Optional[List[str]] = None


class MoodBasedRequest(BaseModel):
    """Mood-based recommendation request schema"""
    mood: str = Field(..., description="Mood or emotional state")
    top_k: int = Field(10, ge=1, le=50)
    user_id: Optional[str] = None  # UUID as string


class TasteProfileResponse(BaseModel):
    """User taste profile response schema"""
    user_id: str  # UUID as string
    dominant_genres: List[Dict[str, float]]
    favorite_studios: List[Dict[str, int]]
    average_score: float
    rating_distribution: Dict[str, int]
    preferred_types: Dict[str, int]
    watch_patterns: Dict[str, Any]
    genre_diversity_score: float
