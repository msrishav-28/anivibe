"""Ranking metrics for recommender-system evaluation."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable

import pandas as pd

from recommender.data import parse_pipe_list


@dataclass(frozen=True)
class UserRankingMetrics:
    """Per-user ranking metrics at K."""

    precision: float
    recall: float
    ndcg: float
    map: float
    hit_rate: float


def precision_at_k(recommended: list[int], relevant: set[int], k: int) -> float:
    if k <= 0:
        return 0.0
    return len(set(recommended[:k]) & relevant) / k


def recall_at_k(recommended: list[int], relevant: set[int], k: int) -> float:
    if not relevant:
        return 0.0
    return len(set(recommended[:k]) & relevant) / len(relevant)


def hit_rate_at_k(recommended: list[int], relevant: set[int], k: int) -> float:
    return 1.0 if set(recommended[:k]) & relevant else 0.0


def average_precision_at_k(recommended: list[int], relevant: set[int], k: int) -> float:
    if not relevant:
        return 0.0

    hits = 0
    score = 0.0
    for index, anime_id in enumerate(recommended[:k], start=1):
        if anime_id in relevant:
            hits += 1
            score += hits / index

    return score / min(len(relevant), k)


def ndcg_at_k(recommended: list[int], relevant: set[int], k: int) -> float:
    if not relevant:
        return 0.0

    dcg = 0.0
    for index, anime_id in enumerate(recommended[:k], start=1):
        if anime_id in relevant:
            dcg += 1.0 / math.log2(index + 1)

    ideal_hits = min(len(relevant), k)
    ideal_dcg = sum(1.0 / math.log2(index + 1) for index in range(1, ideal_hits + 1))
    return dcg / ideal_dcg if ideal_dcg else 0.0


def ranking_metrics(recommended: list[int], relevant: set[int], k: int) -> UserRankingMetrics:
    """Compute binary relevance ranking metrics for one user."""

    return UserRankingMetrics(
        precision=precision_at_k(recommended, relevant, k),
        recall=recall_at_k(recommended, relevant, k),
        ndcg=ndcg_at_k(recommended, relevant, k),
        map=average_precision_at_k(recommended, relevant, k),
        hit_rate=hit_rate_at_k(recommended, relevant, k),
    )


def catalog_coverage(recommendation_lists: Iterable[list[int]], catalog_size: int) -> float:
    """Fraction of catalog items recommended at least once."""

    if catalog_size <= 0:
        return 0.0
    unique_recommended = {
        anime_id
        for recommendation_list in recommendation_lists
        for anime_id in recommendation_list
    }
    return len(unique_recommended) / catalog_size


def genre_diversity(recommendation_lists: Iterable[list[int]], anime: pd.DataFrame) -> float:
    """Average pairwise genre dissimilarity across recommendation lists."""

    genre_lookup = {
        int(row.anime_id): set(parse_pipe_list(row.genres))
        for row in anime[["anime_id", "genres"]].itertuples(index=False)
    }

    diversities: list[float] = []
    for recommendation_list in recommendation_lists:
        pairs: list[float] = []
        items = list(dict.fromkeys(recommendation_list))
        for left_index in range(len(items)):
            for right_index in range(left_index + 1, len(items)):
                left = genre_lookup.get(items[left_index], set())
                right = genre_lookup.get(items[right_index], set())
                if not left and not right:
                    continue
                union = left | right
                intersection = left & right
                pairs.append(1.0 - (len(intersection) / len(union)))
        if pairs:
            diversities.append(sum(pairs) / len(pairs))

    return sum(diversities) / len(diversities) if diversities else 0.0
