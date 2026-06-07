from pathlib import Path

from recommender.data import REQUIRED_ANIME_COLUMNS, prepare_dataset
from recommender.evaluation import run_evaluation
from recommender.metrics import ranking_metrics
from recommender.models import (
    CollaborativeFilteringRecommender,
    ContentBasedRecommender,
    HybridRecommender,
    PopularityRecommender,
)


SAMPLE_ANIME = Path("data/sample/anime.csv")
SAMPLE_RATINGS = Path("data/sample/ratings.csv")


def test_prepare_dataset_creates_canonical_splits(tmp_path):
    bundle = prepare_dataset(
        anime_csv=SAMPLE_ANIME,
        ratings_csv=SAMPLE_RATINGS,
        output_dir=tmp_path / "processed",
    )

    assert list(bundle.anime.columns) == REQUIRED_ANIME_COLUMNS
    assert bundle.manifest["anime_count"] == 24
    assert bundle.manifest["rating_count"] == 72
    assert bundle.manifest["user_count"] == 8
    assert bundle.manifest["train_count"] == 56
    assert bundle.manifest["validation_count"] == 8
    assert bundle.manifest["test_count"] == 8
    assert (tmp_path / "processed" / "manifest.json").exists()


def test_baseline_models_recommend_unseen_items(tmp_path):
    bundle = prepare_dataset(
        anime_csv=SAMPLE_ANIME,
        ratings_csv=SAMPLE_RATINGS,
        output_dir=tmp_path / "processed",
    )
    known_items = set(bundle.train[bundle.train["user_id"] == "u001"]["anime_id"])
    known_items |= set(bundle.validation[bundle.validation["user_id"] == "u001"]["anime_id"])

    models = [
        PopularityRecommender(),
        ContentBasedRecommender(),
        CollaborativeFilteringRecommender(),
        HybridRecommender(),
    ]

    for model in models:
        model.fit(bundle.anime, bundle.train, relevant_threshold=8.0)
        recommendations = model.recommend("u001", known_items=known_items, top_k=5)
        assert recommendations
        assert len(recommendations) <= 5
        assert all(rec.anime_id not in known_items for rec in recommendations)
        assert all(rec.score >= 0 for rec in recommendations)


def test_ranking_metrics_for_known_relevance():
    metrics = ranking_metrics(
        recommended=[10, 20, 30, 40],
        relevant={20, 40},
        k=4,
    )

    assert metrics.precision == 0.5
    assert metrics.recall == 1.0
    assert metrics.hit_rate == 1.0
    assert 0 < metrics.ndcg <= 1.0
    assert 0 < metrics.map <= 1.0


def test_evaluation_writes_metrics_and_samples(tmp_path):
    processed_dir = tmp_path / "processed"
    output_dir = tmp_path / "artifacts"
    prepare_dataset(
        anime_csv=SAMPLE_ANIME,
        ratings_csv=SAMPLE_RATINGS,
        output_dir=processed_dir,
    )

    config_path = tmp_path / "eval.yaml"
    config_path.write_text(
        f"""
data:
  processed_dir: {processed_dir.as_posix()}
evaluation:
  top_k: 10
  relevant_threshold: 8.0
models:
  popularity:
    enabled: true
  content_based:
    enabled: true
  collaborative_filtering:
    enabled: true
  hybrid:
    enabled: true
reporting:
  sample_users:
    - u001
output:
  metrics_csv: {(output_dir / "metrics.csv").as_posix()}
  metrics_json: {(output_dir / "metrics.json").as_posix()}
  metrics_markdown: {(output_dir / "metrics.md").as_posix()}
  sample_recommendations_json: {(output_dir / "samples.json").as_posix()}
""",
        encoding="utf-8",
    )

    run = run_evaluation(config_path)

    assert set(run.metrics["model"]) == {
        "popularity",
        "content_based",
        "collaborative_filtering",
        "hybrid",
    }
    assert (output_dir / "metrics.csv").exists()
    assert (output_dir / "metrics.json").exists()
    assert (output_dir / "metrics.md").exists()
    assert (output_dir / "samples.json").exists()
