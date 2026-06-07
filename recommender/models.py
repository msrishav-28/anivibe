"""Baseline recommender implementations for offline evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from recommender.data import parse_pipe_list


@dataclass(frozen=True)
class Recommendation:
    """A scored recommendation for one anime."""

    anime_id: int
    score: float


class BaseRecommender:
    """Common recommender interface used by the benchmark harness."""

    name = "base"
    status = "baseline"

    def fit(
        self,
        anime: pd.DataFrame,
        train_ratings: pd.DataFrame,
        relevant_threshold: float = 8.0,
    ) -> "BaseRecommender":
        raise NotImplementedError

    def recommend(
        self,
        user_id: str,
        known_items: Iterable[int],
        top_k: int = 10,
    ) -> list[Recommendation]:
        raise NotImplementedError


class PopularityRecommender(BaseRecommender):
    """Popularity/quality baseline using only global item statistics."""

    name = "popularity"

    def fit(
        self,
        anime: pd.DataFrame,
        train_ratings: pd.DataFrame,
        relevant_threshold: float = 8.0,
    ) -> "PopularityRecommender":
        self.anime = anime.copy()
        self.train_ratings = train_ratings.copy()

        stats = (
            train_ratings.groupby("anime_id")["rating"]
            .agg(["mean", "count"])
            .reset_index()
            .rename(columns={"mean": "rating_mean", "count": "rating_count"})
        )
        scored = anime[["anime_id", "score", "members"]].merge(stats, on="anime_id", how="left")
        scored["rating_mean"] = scored["rating_mean"].fillna(scored["score"]).fillna(0.0)
        scored["rating_count"] = scored["rating_count"].fillna(0.0)

        max_count = max(float(scored["rating_count"].max()), 1.0)
        max_members = max(float(scored["members"].max()), 1.0)
        quality = scored["rating_mean"] / 10.0
        confidence = np.log1p(scored["rating_count"]) / np.log1p(max_count)
        catalog_popularity = np.log1p(scored["members"]) / np.log1p(max_members)
        scored["model_score"] = (0.65 * quality) + (0.25 * confidence) + (0.10 * catalog_popularity)

        self.item_scores = {
            int(row.anime_id): float(row.model_score)
            for row in scored[["anime_id", "model_score"]].itertuples(index=False)
        }
        return self

    def recommend(
        self,
        user_id: str,
        known_items: Iterable[int],
        top_k: int = 10,
    ) -> list[Recommendation]:
        known = set(int(item) for item in known_items)
        ranked = [
            Recommendation(anime_id=anime_id, score=score)
            for anime_id, score in self.item_scores.items()
            if anime_id not in known
        ]
        return sorted(ranked, key=lambda rec: (-rec.score, rec.anime_id))[:top_k]


class ContentBasedRecommender(BaseRecommender):
    """TF-IDF metadata recommender built from anime content features."""

    name = "content_based"

    def fit(
        self,
        anime: pd.DataFrame,
        train_ratings: pd.DataFrame,
        relevant_threshold: float = 8.0,
    ) -> "ContentBasedRecommender":
        self.anime = anime.copy()
        self.train_ratings = train_ratings.copy()
        self.relevant_threshold = relevant_threshold
        self.item_ids = [int(anime_id) for anime_id in self.anime["anime_id"].tolist()]
        self.item_index = {anime_id: index for index, anime_id in enumerate(self.item_ids)}
        self.user_histories = _ratings_by_user(train_ratings)

        documents = [_feature_document(row) for _, row in self.anime.iterrows()]
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1)
        self.feature_matrix = self.vectorizer.fit_transform(documents)
        self.fallback = PopularityRecommender().fit(anime, train_ratings, relevant_threshold)
        return self

    def recommend(
        self,
        user_id: str,
        known_items: Iterable[int],
        top_k: int = 10,
    ) -> list[Recommendation]:
        history = self.user_histories.get(user_id, {})
        profile_items = [
            (anime_id, rating)
            for anime_id, rating in history.items()
            if anime_id in self.item_index and rating >= self.relevant_threshold
        ]

        if not profile_items:
            return self.fallback.recommend(user_id=user_id, known_items=known_items, top_k=top_k)

        item_indices = [self.item_index[anime_id] for anime_id, _ in profile_items]
        weights = np.array([rating / 10.0 for _, rating in profile_items], dtype=float)
        profile = self.feature_matrix[item_indices].multiply(weights[:, None]).sum(axis=0)
        profile = np.asarray(profile) / max(float(weights.sum()), 1e-12)
        similarities = cosine_similarity(profile, self.feature_matrix).ravel()

        known = set(int(item) for item in known_items)
        ranked = [
            Recommendation(anime_id=anime_id, score=float(similarities[index]))
            for anime_id, index in self.item_index.items()
            if anime_id not in known
        ]
        return sorted(ranked, key=lambda rec: (-rec.score, rec.anime_id))[:top_k]


class CollaborativeFilteringRecommender(BaseRecommender):
    """Item-item collaborative filtering baseline from user-rating behavior."""

    name = "collaborative_filtering"

    def fit(
        self,
        anime: pd.DataFrame,
        train_ratings: pd.DataFrame,
        relevant_threshold: float = 8.0,
    ) -> "CollaborativeFilteringRecommender":
        self.anime = anime.copy()
        self.train_ratings = train_ratings.copy()
        self.user_histories = _ratings_by_user(train_ratings)
        self.fallback = PopularityRecommender().fit(anime, train_ratings, relevant_threshold)

        if train_ratings.empty:
            self.item_ids = []
            self.item_index = {}
            self.item_similarity = np.zeros((0, 0))
            return self

        matrix = train_ratings.pivot_table(
            index="user_id",
            columns="anime_id",
            values="rating",
            aggfunc="mean",
            fill_value=0.0,
        )
        self.item_ids = [int(anime_id) for anime_id in matrix.columns.tolist()]
        self.item_index = {anime_id: index for index, anime_id in enumerate(self.item_ids)}
        item_user_matrix = matrix.T.to_numpy(dtype=float)
        self.item_similarity = cosine_similarity(item_user_matrix)
        np.fill_diagonal(self.item_similarity, 0.0)
        return self

    def recommend(
        self,
        user_id: str,
        known_items: Iterable[int],
        top_k: int = 10,
    ) -> list[Recommendation]:
        history = self.user_histories.get(user_id, {})
        rated_items = [
            (anime_id, rating)
            for anime_id, rating in history.items()
            if anime_id in self.item_index
        ]
        if not rated_items:
            return self.fallback.recommend(user_id=user_id, known_items=known_items, top_k=top_k)

        known = set(int(item) for item in known_items)
        ranked: list[Recommendation] = []

        for candidate_id in self.item_ids:
            if candidate_id in known:
                continue

            candidate_index = self.item_index[candidate_id]
            weighted_sum = 0.0
            similarity_sum = 0.0

            for rated_id, rating in rated_items:
                rated_index = self.item_index[rated_id]
                similarity = float(self.item_similarity[candidate_index, rated_index])
                if similarity <= 0:
                    continue
                weighted_sum += similarity * (rating / 10.0)
                similarity_sum += similarity

            if similarity_sum > 0:
                ranked.append(Recommendation(candidate_id, weighted_sum / similarity_sum))

        if len(ranked) < top_k:
            existing_ids = {rec.anime_id for rec in ranked}
            fallback = [
                rec
                for rec in self.fallback.recommend(user_id, known_items=known, top_k=len(self.anime))
                if rec.anime_id not in existing_ids
            ]
            ranked.extend(fallback)

        return sorted(ranked, key=lambda rec: (-rec.score, rec.anime_id))[:top_k]


class HybridRecommender(BaseRecommender):
    """Weighted hybrid of popularity, content-based, and collaborative baselines."""

    name = "hybrid"

    def __init__(
        self,
        popularity_weight: float = 0.20,
        content_weight: float = 0.40,
        collaborative_weight: float = 0.40,
    ) -> None:
        self.weights = {
            "popularity": popularity_weight,
            "content_based": content_weight,
            "collaborative_filtering": collaborative_weight,
        }

    def fit(
        self,
        anime: pd.DataFrame,
        train_ratings: pd.DataFrame,
        relevant_threshold: float = 8.0,
    ) -> "HybridRecommender":
        self.anime = anime.copy()
        self.components = {
            "popularity": PopularityRecommender().fit(anime, train_ratings, relevant_threshold),
            "content_based": ContentBasedRecommender().fit(anime, train_ratings, relevant_threshold),
            "collaborative_filtering": CollaborativeFilteringRecommender().fit(
                anime, train_ratings, relevant_threshold
            ),
        }
        return self

    def recommend(
        self,
        user_id: str,
        known_items: Iterable[int],
        top_k: int = 10,
    ) -> list[Recommendation]:
        catalog_size = len(self.anime)
        combined: dict[int, float] = {}

        for name, model in self.components.items():
            recs = model.recommend(user_id=user_id, known_items=known_items, top_k=catalog_size)
            if not recs:
                continue
            max_score = max(rec.score for rec in recs) or 1.0
            for rec in recs:
                normalized = rec.score / max_score
                combined[rec.anime_id] = combined.get(rec.anime_id, 0.0) + (
                    self.weights[name] * normalized
                )

        ranked = [
            Recommendation(anime_id=anime_id, score=score)
            for anime_id, score in combined.items()
        ]
        return sorted(ranked, key=lambda rec: (-rec.score, rec.anime_id))[:top_k]


MODEL_ROADMAP = [
    {
        "name": "popularity",
        "status": "implemented_baseline",
        "portfolio_role": "cold-start and sanity-check baseline",
    },
    {
        "name": "content_based",
        "status": "implemented_baseline",
        "portfolio_role": "metadata similarity and cold-start behavior",
    },
    {
        "name": "collaborative_filtering",
        "status": "implemented_baseline",
        "portfolio_role": "user-rating personalization baseline",
    },
    {
        "name": "hybrid",
        "status": "implemented_baseline",
        "portfolio_role": "weighted combination of baseline signals",
    },
    {
        "name": "matrix_factorization_svd",
        "status": "planned_next",
        "portfolio_role": "latent-factor benchmark against neighborhood methods",
    },
    {
        "name": "sbert_semantic_search",
        "status": "experimental_existing_service",
        "portfolio_role": "natural-language retrieval layer",
    },
    {
        "name": "clip_visual_search",
        "status": "planned_experimental",
        "portfolio_role": "multimodal retrieval layer",
    },
    {
        "name": "bert4rec",
        "status": "planned_research",
        "portfolio_role": "sequential recommendation benchmark",
    },
    {
        "name": "gnn_recommender",
        "status": "planned_research",
        "portfolio_role": "graph recommendation experiment",
    },
    {
        "name": "llm_explanations",
        "status": "optional_explanation_layer",
        "portfolio_role": "human-readable explanation layer, not core ranking proof",
    },
]


def build_default_models(config: dict | None = None) -> list[BaseRecommender]:
    """Build enabled baseline models from an evaluation config."""

    config = config or {}
    model_config = config.get("models", {})

    models: list[BaseRecommender] = []
    if model_config.get("popularity", {}).get("enabled", True):
        models.append(PopularityRecommender())
    if model_config.get("content_based", {}).get("enabled", True):
        models.append(ContentBasedRecommender())
    if model_config.get("collaborative_filtering", {}).get("enabled", True):
        models.append(CollaborativeFilteringRecommender())
    if model_config.get("hybrid", {}).get("enabled", True):
        hybrid_cfg = model_config.get("hybrid", {})
        weights = hybrid_cfg.get("weights", {})
        models.append(
            HybridRecommender(
                popularity_weight=float(weights.get("popularity", 0.20)),
                content_weight=float(weights.get("content_based", 0.40)),
                collaborative_weight=float(weights.get("collaborative_filtering", 0.40)),
            )
        )
    return models


def _ratings_by_user(ratings: pd.DataFrame) -> dict[str, dict[int, float]]:
    histories: dict[str, dict[int, float]] = {}
    for row in ratings[["user_id", "anime_id", "rating"]].itertuples(index=False):
        histories.setdefault(str(row.user_id), {})[int(row.anime_id)] = float(row.rating)
    return histories


def _feature_document(row: pd.Series) -> str:
    genres = " ".join(parse_pipe_list(row["genres"]))
    studios = " ".join(parse_pipe_list(row["studios"]))
    return " ".join(
        [
            str(row["title"]),
            str(row["synopsis"]),
            genres,
            studios,
            str(row["type"]),
            f"year_{int(row['year'])}" if int(row["year"]) else "",
        ]
    )
