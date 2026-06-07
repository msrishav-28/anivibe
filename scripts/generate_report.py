"""Generate a reviewer-readable benchmark report from evaluation artifacts."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate AniVibe benchmark report")
    parser.add_argument(
        "--metrics-json",
        type=Path,
        default=Path("artifacts/evaluation/metrics.json"),
    )
    parser.add_argument(
        "--samples-json",
        type=Path,
        default=Path("artifacts/evaluation/samples.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/reports/offline_benchmark.md"),
    )
    args = parser.parse_args()

    if not args.metrics_json.exists():
        raise FileNotFoundError(
            f"Missing {args.metrics_json}. Run python -m scripts.evaluate_recommenders first."
        )

    payload = json.loads(args.metrics_json.read_text(encoding="utf-8"))
    samples = (
        json.loads(args.samples_json.read_text(encoding="utf-8"))
        if args.samples_json.exists()
        else {}
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        build_report(payload=payload, samples=samples),
        encoding="utf-8",
    )
    print(f"Wrote benchmark report to {args.output}")


def build_report(payload: dict, samples: dict) -> str:
    dataset = payload.get("dataset", {})
    metrics = payload.get("metrics", [])
    generated_at = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines = [
        "# AniVibe Offline Recommender Benchmark",
        "",
        f"Generated: {generated_at}",
        "",
        "## Problem",
        "",
        "Rank anime recommendations for a user from anime metadata and historical ratings.",
        "This benchmark compares simple baselines before adding advanced models.",
        "",
        "## Dataset",
        "",
        f"- Anime: {dataset.get('anime_count', 'unknown')}",
        f"- Ratings: {dataset.get('rating_count', 'unknown')}",
        f"- Users: {dataset.get('user_count', 'unknown')}",
        f"- Split: {dataset.get('split_strategy', 'unknown')}",
        f"- Train ratings: {dataset.get('train_count', 'unknown')}",
        f"- Validation ratings: {dataset.get('validation_count', 'unknown')}",
        f"- Test ratings: {dataset.get('test_count', 'unknown')}",
        "",
        "## Results",
        "",
        _metrics_table(metrics),
        "",
        "## Sample Recommendations",
        "",
        _sample_summary(samples),
        "",
        "## Limitations",
        "",
        "- The checked-in sample data is intentionally small and exists for reproducibility tests.",
        "- Portfolio-grade claims require running the same benchmark on a larger public ratings dataset.",
        "- Advanced models should be added only after they beat or explainably differ from these baselines.",
        "",
    ]
    return "\n".join(lines)


def _metrics_table(metrics: list[dict]) -> str:
    if not metrics:
        return "No metrics found."

    columns = [
        "model",
        "precision_at_k",
        "recall_at_k",
        "ndcg_at_k",
        "map_at_k",
        "hit_rate_at_k",
        "coverage",
        "diversity",
        "mean_latency_ms",
    ]
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in metrics:
        values = []
        for column in columns:
            value = row.get(column, "")
            values.append(f"{value:.4f}" if isinstance(value, float) else str(value))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def _sample_summary(samples: dict) -> str:
    if not samples:
        return "No sample recommendations found."

    lines: list[str] = []
    for model_name, user_samples in samples.items():
        lines.append(f"### {model_name}")
        lines.append("")
        for sample in user_samples[:2]:
            titles = [
                rec["title"]
                for rec in sample.get("recommendations", [])[:5]
            ]
            lines.append(f"- `{sample.get('user_id')}`: {', '.join(titles)}")
        lines.append("")
    return "\n".join(lines).strip()


if __name__ == "__main__":
    main()
