"""Dataset preparation utilities for the offline recommender benchmark."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


REQUIRED_ANIME_COLUMNS = [
    "anime_id",
    "title",
    "synopsis",
    "genres",
    "studios",
    "type",
    "episodes",
    "score",
    "members",
    "year",
    "image_url",
]

REQUIRED_RATING_COLUMNS = ["user_id", "anime_id", "rating"]


@dataclass(frozen=True)
class DatasetBundle:
    """Canonical in-memory representation of the benchmark data."""

    anime: pd.DataFrame
    ratings: pd.DataFrame
    train: pd.DataFrame
    validation: pd.DataFrame
    test: pd.DataFrame
    manifest: dict[str, Any]


def load_anime_csv(path: str | Path) -> pd.DataFrame:
    """Load and validate canonical anime metadata."""

    anime = pd.read_csv(path)
    _require_columns(anime, REQUIRED_ANIME_COLUMNS, dataset_name="anime")

    anime = anime.copy()
    anime["anime_id"] = anime["anime_id"].astype(int)
    anime["title"] = anime["title"].fillna("").astype(str)
    anime["synopsis"] = anime["synopsis"].fillna("").astype(str)
    anime["genres"] = anime["genres"].fillna("").astype(str)
    anime["studios"] = anime["studios"].fillna("").astype(str)
    anime["type"] = anime["type"].fillna("Unknown").astype(str)
    anime["episodes"] = pd.to_numeric(anime["episodes"], errors="coerce").fillna(0).astype(int)
    anime["score"] = pd.to_numeric(anime["score"], errors="coerce").fillna(0.0).astype(float)
    anime["members"] = pd.to_numeric(anime["members"], errors="coerce").fillna(0).astype(int)
    anime["year"] = pd.to_numeric(anime["year"], errors="coerce").fillna(0).astype(int)
    anime["image_url"] = anime["image_url"].fillna("").astype(str)

    anime = anime.drop_duplicates(subset=["anime_id"], keep="first")
    anime = anime.sort_values("anime_id").reset_index(drop=True)
    return anime[REQUIRED_ANIME_COLUMNS]


def load_ratings_csv(path: str | Path) -> pd.DataFrame:
    """Load and validate canonical user-anime ratings."""

    ratings = pd.read_csv(path)
    _require_columns(ratings, REQUIRED_RATING_COLUMNS, dataset_name="ratings")

    ratings = ratings.copy()
    ratings["user_id"] = ratings["user_id"].fillna("").astype(str)
    ratings["anime_id"] = ratings["anime_id"].astype(int)
    ratings["rating"] = pd.to_numeric(ratings["rating"], errors="coerce")

    if "timestamp" not in ratings.columns:
        ratings["timestamp"] = pd.RangeIndex(start=1, stop=len(ratings) + 1)

    ratings["timestamp"] = ratings["timestamp"].fillna("").astype(str)
    ratings = ratings.dropna(subset=["rating"])
    ratings = ratings[(ratings["rating"] >= 0) & (ratings["rating"] <= 10)]
    ratings = ratings[ratings["user_id"].str.len() > 0]
    ratings = ratings.sort_values(["user_id", "timestamp", "anime_id"])
    ratings = ratings.drop_duplicates(subset=["user_id", "anime_id"], keep="last")
    return ratings[["user_id", "anime_id", "rating", "timestamp"]].reset_index(drop=True)


def prepare_dataset(
    anime_csv: str | Path,
    ratings_csv: str | Path,
    output_dir: str | Path,
    seed: int = 42,
    min_ratings_per_user: int = 3,
) -> DatasetBundle:
    """Prepare canonical processed data and deterministic benchmark splits."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    anime = load_anime_csv(anime_csv)
    ratings = load_ratings_csv(ratings_csv)
    ratings = ratings[ratings["anime_id"].isin(set(anime["anime_id"]))].reset_index(drop=True)

    train, validation, test = split_ratings(
        ratings=ratings,
        min_ratings_per_user=min_ratings_per_user,
    )

    anime.to_csv(output_path / "anime.csv", index=False)
    ratings.to_csv(output_path / "ratings.csv", index=False)
    train.to_csv(output_path / "train.csv", index=False)
    validation.to_csv(output_path / "validation.csv", index=False)
    test.to_csv(output_path / "test.csv", index=False)

    manifest = build_manifest(
        anime=anime,
        ratings=ratings,
        train=train,
        validation=validation,
        test=test,
        seed=seed,
        min_ratings_per_user=min_ratings_per_user,
    )
    (output_path / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    return DatasetBundle(
        anime=anime,
        ratings=ratings,
        train=train,
        validation=validation,
        test=test,
        manifest=manifest,
    )


def load_processed_dataset(processed_dir: str | Path) -> DatasetBundle:
    """Load a processed benchmark dataset produced by prepare_dataset."""

    processed_path = Path(processed_dir)
    anime = load_anime_csv(processed_path / "anime.csv")
    ratings = load_ratings_csv(processed_path / "ratings.csv")
    train = load_ratings_csv(processed_path / "train.csv")
    validation = load_ratings_csv(processed_path / "validation.csv")
    test = load_ratings_csv(processed_path / "test.csv")

    manifest_path = processed_path / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}

    return DatasetBundle(
        anime=anime,
        ratings=ratings,
        train=train,
        validation=validation,
        test=test,
        manifest=manifest,
    )


def split_ratings(
    ratings: pd.DataFrame,
    min_ratings_per_user: int = 3,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Use a deterministic leave-last-out split per user.

    For users with at least three interactions, the latest item is test, the
    second latest is validation, and earlier interactions are training data.
    Users with fewer ratings stay in training so they do not create impossible
    evaluation cases.
    """

    train_parts: list[pd.DataFrame] = []
    validation_parts: list[pd.DataFrame] = []
    test_parts: list[pd.DataFrame] = []

    ordered = ratings.sort_values(["user_id", "timestamp", "anime_id"]).reset_index(drop=True)
    for _, user_rows in ordered.groupby("user_id", sort=True):
        if len(user_rows) >= min_ratings_per_user:
            train_parts.append(user_rows.iloc[:-2])
            validation_parts.append(user_rows.iloc[-2:-1])
            test_parts.append(user_rows.iloc[-1:])
        else:
            train_parts.append(user_rows)

    columns = ["user_id", "anime_id", "rating", "timestamp"]
    train = _concat_or_empty(train_parts, columns)
    validation = _concat_or_empty(validation_parts, columns)
    test = _concat_or_empty(test_parts, columns)
    return train, validation, test


def build_manifest(
    anime: pd.DataFrame,
    ratings: pd.DataFrame,
    train: pd.DataFrame,
    validation: pd.DataFrame,
    test: pd.DataFrame,
    seed: int,
    min_ratings_per_user: int,
) -> dict[str, Any]:
    """Build a reproducibility manifest for the processed dataset."""

    return {
        "schema_version": "1.0",
        "seed": seed,
        "split_strategy": "leave_last_two_out_per_user",
        "min_ratings_per_user": min_ratings_per_user,
        "anime_count": int(len(anime)),
        "rating_count": int(len(ratings)),
        "user_count": int(ratings["user_id"].nunique()),
        "train_count": int(len(train)),
        "validation_count": int(len(validation)),
        "test_count": int(len(test)),
        "required_anime_columns": REQUIRED_ANIME_COLUMNS,
        "required_rating_columns": REQUIRED_RATING_COLUMNS + ["timestamp"],
    }


def parse_pipe_list(value: Any) -> list[str]:
    """Parse the pipe-delimited list fields used by canonical CSV files."""

    if value is None or pd.isna(value):
        return []
    return [part.strip() for part in str(value).split("|") if part.strip()]


def _require_columns(df: pd.DataFrame, columns: list[str], dataset_name: str) -> None:
    missing = [column for column in columns if column not in df.columns]
    if missing:
        raise ValueError(f"{dataset_name} dataset is missing required columns: {missing}")


def _concat_or_empty(parts: list[pd.DataFrame], columns: list[str]) -> pd.DataFrame:
    if not parts:
        return pd.DataFrame(columns=columns)
    return pd.concat(parts, ignore_index=True)[columns]
