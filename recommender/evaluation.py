"""Offline evaluation harness for AniVibe recommender baselines."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from recommender.data import DatasetBundle, load_processed_dataset
from recommender.metrics import catalog_coverage, genre_diversity, ranking_metrics
from recommender.models import BaseRecommender, build_default_models


@dataclass(frozen=True)
class EvaluationRun:
    """Result of one offline evaluation run."""

    metrics: pd.DataFrame
    sample_recommendations: dict[str, Any]
    config: dict[str, Any]


def run_evaluation(config_path: str | Path) -> EvaluationRun:
    """Run all enabled recommenders and persist comparison artifacts."""

    config = load_config(config_path)
    dataset = load_processed_dataset(config["data"]["processed_dir"])
    top_k = int(config.get("evaluation", {}).get("top_k", 10))
    relevant_threshold = float(config.get("evaluation", {}).get("relevant_threshold", 8.0))

    models = build_default_models(config)
    metric_rows: list[dict[str, Any]] = []
    sample_recommendations: dict[str, Any] = {}

    for model in models:
        model.fit(dataset.anime, dataset.train, relevant_threshold=relevant_threshold)
        metrics, samples = evaluate_model(
            model=model,
            dataset=dataset,
            top_k=top_k,
            relevant_threshold=relevant_threshold,
            sample_users=config.get("reporting", {}).get("sample_users", []),
        )
        metric_rows.append(metrics)
        sample_recommendations[model.name] = samples

    metrics_df = pd.DataFrame(metric_rows).sort_values(
        ["ndcg_at_k", "recall_at_k", "precision_at_k"],
        ascending=[False, False, False],
    )

    write_outputs(
        metrics=metrics_df,
        sample_recommendations=sample_recommendations,
        dataset=dataset,
        config=config,
    )

    return EvaluationRun(
        metrics=metrics_df,
        sample_recommendations=sample_recommendations,
        config=config,
    )


def evaluate_model(
    model: BaseRecommender,
    dataset: DatasetBundle,
    top_k: int,
    relevant_threshold: float,
    sample_users: list[str],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Evaluate one fitted model over held-out test ratings."""

    test_relevant = dataset.test[dataset.test["rating"] >= relevant_threshold]
    train_by_user = _items_by_user(dataset.train)
    validation_by_user = _items_by_user(dataset.validation)
    relevant_by_user = _items_by_user(test_relevant)

    user_metrics = []
    recommendation_lists: list[list[int]] = []
    latencies_ms: list[float] = []

    for user_id, relevant_items in relevant_by_user.items():
        known_items = train_by_user.get(user_id, set()) | validation_by_user.get(user_id, set())

        start = time.perf_counter()
        recommendations = model.recommend(
            user_id=user_id,
            known_items=known_items,
            top_k=top_k,
        )
        latencies_ms.append((time.perf_counter() - start) * 1000)

        recommended_ids = [rec.anime_id for rec in recommendations]
        recommendation_lists.append(recommended_ids)
        user_metrics.append(ranking_metrics(recommended_ids, relevant_items, top_k))

    samples = build_sample_recommendations(
        model=model,
        dataset=dataset,
        top_k=top_k,
        sample_users=sample_users,
        train_by_user=train_by_user,
        validation_by_user=validation_by_user,
    )

    if not user_metrics:
        return _empty_metrics(model.name, top_k), samples

    return {
        "model": model.name,
        "k": top_k,
        "evaluated_users": len(user_metrics),
        "precision_at_k": _mean([metric.precision for metric in user_metrics]),
        "recall_at_k": _mean([metric.recall for metric in user_metrics]),
        "ndcg_at_k": _mean([metric.ndcg for metric in user_metrics]),
        "map_at_k": _mean([metric.map for metric in user_metrics]),
        "hit_rate_at_k": _mean([metric.hit_rate for metric in user_metrics]),
        "coverage": catalog_coverage(recommendation_lists, catalog_size=len(dataset.anime)),
        "diversity": genre_diversity(recommendation_lists, dataset.anime),
        "mean_latency_ms": _mean(latencies_ms),
    }, samples


def build_sample_recommendations(
    model: BaseRecommender,
    dataset: DatasetBundle,
    top_k: int,
    sample_users: list[str],
    train_by_user: dict[str, set[int]],
    validation_by_user: dict[str, set[int]],
) -> list[dict[str, Any]]:
    """Generate human-readable recommendations for fixed sample users."""

    title_lookup = {
        int(row.anime_id): row.title
        for row in dataset.anime[["anime_id", "title"]].itertuples(index=False)
    }
    samples: list[dict[str, Any]] = []

    for user_id in sample_users:
        known_items = train_by_user.get(user_id, set()) | validation_by_user.get(user_id, set())
        recommendations = model.recommend(user_id=user_id, known_items=known_items, top_k=top_k)
        samples.append(
            {
                "user_id": user_id,
                "recommendations": [
                    {
                        "rank": index,
                        "anime_id": rec.anime_id,
                        "title": title_lookup.get(rec.anime_id, ""),
                        "score": round(float(rec.score), 6),
                    }
                    for index, rec in enumerate(recommendations, start=1)
                ],
            }
        )

    return samples


def write_outputs(
    metrics: pd.DataFrame,
    sample_recommendations: dict[str, Any],
    dataset: DatasetBundle,
    config: dict[str, Any],
) -> None:
    """Persist machine-readable and reviewer-readable evaluation artifacts."""

    output_config = config.get("output", {})
    metrics_csv = Path(output_config.get("metrics_csv", "artifacts/evaluation/metrics.csv"))
    metrics_json = Path(output_config.get("metrics_json", "artifacts/evaluation/metrics.json"))
    metrics_markdown = Path(
        output_config.get("metrics_markdown", "artifacts/evaluation/metrics.md")
    )
    samples_json = Path(
        output_config.get("sample_recommendations_json", "artifacts/evaluation/samples.json")
    )

    for path in [metrics_csv, metrics_json, metrics_markdown, samples_json]:
        path.parent.mkdir(parents=True, exist_ok=True)

    metrics.to_csv(metrics_csv, index=False)
    metrics_json.write_text(
        json.dumps(
            {
                "dataset": dataset.manifest,
                "metrics": metrics.to_dict(orient="records"),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    metrics_markdown.write_text(_dataframe_to_markdown(metrics), encoding="utf-8")
    samples_json.write_text(json.dumps(sample_recommendations, indent=2), encoding="utf-8")


def load_config(config_path: str | Path) -> dict[str, Any]:
    with Path(config_path).open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}

    config.setdefault("data", {})
    config["data"].setdefault("processed_dir", "data/processed")
    config.setdefault("evaluation", {})
    config["evaluation"].setdefault("top_k", 10)
    config["evaluation"].setdefault("relevant_threshold", 8.0)
    return config


def _items_by_user(ratings: pd.DataFrame) -> dict[str, set[int]]:
    items: dict[str, set[int]] = {}
    for row in ratings[["user_id", "anime_id"]].itertuples(index=False):
        items.setdefault(str(row.user_id), set()).add(int(row.anime_id))
    return items


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _dataframe_to_markdown(df: pd.DataFrame) -> str:
    headers = [str(column) for column in df.columns]
    rows = [
        [
            f"{value:.4f}" if isinstance(value, float) else str(value)
            for value in row
        ]
        for row in df.itertuples(index=False, name=None)
    ]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines) + "\n"


def _empty_metrics(model_name: str, top_k: int) -> dict[str, Any]:
    return {
        "model": model_name,
        "k": top_k,
        "evaluated_users": 0,
        "precision_at_k": 0.0,
        "recall_at_k": 0.0,
        "ndcg_at_k": 0.0,
        "map_at_k": 0.0,
        "hit_rate_at_k": 0.0,
        "coverage": 0.0,
        "diversity": 0.0,
        "mean_latency_ms": 0.0,
    }
