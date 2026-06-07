"""
Analytics schemas
"""
from typing import Dict, List, Any
from pydantic import BaseModel

class GenreDistribution(BaseModel):
    genre: str
    count: int
    percentage: float
    color: str

class HeatmapData(BaseModel):
    date: str
    episodes: int
    hours: float

class AnalyticsStats(BaseModel):
    total_anime: int
    total_episodes: int
    total_watch_time: float
    average_rating: float
    completion_rate: float
    genres_distribution: Dict[str, int]
    top_studios: List[Dict[str, Any]]
