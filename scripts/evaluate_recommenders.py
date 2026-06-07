"""Run the offline recommender benchmark."""

from __future__ import annotations

import argparse
from pathlib import Path

from recommender.evaluation import run_evaluation


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate AniVibe recommender baselines")
    parser.add_argument("--config", type=Path, default=Path("configs/eval.yaml"))
    args = parser.parse_args()

    run = run_evaluation(args.config)
    print("AniVibe offline recommender benchmark")
    print(run.metrics.to_string(index=False))


if __name__ == "__main__":
    main()
