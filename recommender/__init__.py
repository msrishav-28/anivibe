"""Offline recommendation benchmark components for AniVibe.

This package is intentionally independent from FastAPI, Supabase, Redis, and
Modal so the core recommendation work can be reproduced from a clean clone.
"""

from recommender.data import DatasetBundle, load_processed_dataset, prepare_dataset
from recommender.evaluation import EvaluationRun, run_evaluation
from recommender.models import (
    CollaborativeFilteringRecommender,
    ContentBasedRecommender,
    HybridRecommender,
    PopularityRecommender,
)

__all__ = [
    "DatasetBundle",
    "EvaluationRun",
    "prepare_dataset",
    "load_processed_dataset",
    "run_evaluation",
    "PopularityRecommender",
    "ContentBasedRecommender",
    "CollaborativeFilteringRecommender",
    "HybridRecommender",
]
