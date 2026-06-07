"""Prepare canonical AniVibe benchmark data.

Usage:
    python -m scripts.prepare_dataset --sample
"""

from __future__ import annotations

import argparse
from pathlib import Path

from recommender.data import prepare_dataset


DEFAULT_SAMPLE_ANIME = Path("data/sample/anime.csv")
DEFAULT_SAMPLE_RATINGS = Path("data/sample/ratings.csv")
DEFAULT_OUTPUT_DIR = Path("data/processed")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare AniVibe benchmark data")
    parser.add_argument("--sample", action="store_true", help="Use the checked-in sample dataset")
    parser.add_argument("--anime-csv", type=Path, help="Path to raw anime metadata CSV")
    parser.add_argument("--ratings-csv", type=Path, help="Path to raw user ratings CSV")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--min-ratings-per-user", type=int, default=3)
    args = parser.parse_args()

    if args.sample:
        anime_csv = DEFAULT_SAMPLE_ANIME
        ratings_csv = DEFAULT_SAMPLE_RATINGS
    else:
        if not args.anime_csv or not args.ratings_csv:
            parser.error("Provide --sample or both --anime-csv and --ratings-csv")
        anime_csv = args.anime_csv
        ratings_csv = args.ratings_csv

    bundle = prepare_dataset(
        anime_csv=anime_csv,
        ratings_csv=ratings_csv,
        output_dir=args.output_dir,
        seed=args.seed,
        min_ratings_per_user=args.min_ratings_per_user,
    )

    manifest = bundle.manifest
    print("Prepared AniVibe benchmark dataset")
    print(f"  anime:      {manifest['anime_count']}")
    print(f"  ratings:    {manifest['rating_count']}")
    print(f"  users:      {manifest['user_count']}")
    print(f"  train:      {manifest['train_count']}")
    print(f"  validation: {manifest['validation_count']}")
    print(f"  test:       {manifest['test_count']}")
    print(f"  output:     {args.output_dir}")


if __name__ == "__main__":
    main()
