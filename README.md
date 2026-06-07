# AniVibe - Hybrid Anime Recommender Benchmark

AniVibe is a reproducible anime recommendation system that compares popularity,
content-based, collaborative filtering, and hybrid recommenders on anime metadata
and user-rating data. The project focuses on recommender-system fundamentals,
evaluation metrics, backend API design, and clear ML engineering documentation.

## Problem Statement

Given a user's historical anime ratings, rank unseen anime that the user is
likely to enjoy. The project is structured as an engineering portfolio artifact,
not as a production SaaS product.

The core technical goals are:

- define a clean anime and ratings data contract
- prepare deterministic train, validation, and test splits
- implement simple baselines before advanced models
- evaluate recommendations with recommender-system metrics
- keep the ML core reproducible without cloud services
- use the backend and frontend only after the recommender layer is credible

## Current Status

| Area | Status | Notes |
| --- | --- | --- |
| Offline data contract | Implemented | Canonical `anime`, `ratings`, and split files |
| Sample dataset | Implemented | Small fixture under `data/sample/` for reproducibility |
| Popularity baseline | Implemented | Cold-start and sanity-check baseline |
| Content-based baseline | Implemented | TF-IDF over metadata features |
| Collaborative filtering baseline | Implemented | Item-item rating-behavior baseline |
| Hybrid baseline | Implemented | Weighted blend of baseline scores |
| Offline evaluation | Implemented | Precision@K, Recall@K, NDCG@K, MAP@K, HitRate@K, coverage, diversity, latency |
| FastAPI backend | Existing, not yet cleaned | Next layer should expose a small recommender API |
| Next.js frontend | Existing, optional | Not part of the core portfolio proof yet |
| SBERT, CLIP, BERT4Rec, GNN | Planned or experimental | Kept on roadmap but not claimed as benchmarked |

## Quick Start

Use the lightweight benchmark environment if you only want to verify the core ML
work:

```bash
pip install -r requirements-benchmark.txt
python -m scripts.prepare_dataset --sample
python -m scripts.evaluate_recommenders --config configs/eval.yaml
python -m scripts.generate_report
```

Or with `make`:

```bash
make install-benchmark
make benchmark
```

Generated outputs are written to ignored local artifact paths:

- `data/processed/`
- `artifacts/evaluation/`
- `artifacts/reports/offline_benchmark.md`

## Sample Benchmark Results

These numbers come from the checked-in sample fixture. They prove the evaluation
pipeline works; they are not final research-quality claims.

| Model | Precision@10 | Recall@10 | NDCG@10 | MAP@10 | HitRate@10 | Coverage | Diversity | Mean Latency |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| content_based | 0.1000 | 1.0000 | 0.8025 | 0.7417 | 1.0000 | 0.8333 | 0.8024 | 2.60 ms |
| hybrid | 0.0875 | 0.8750 | 0.7413 | 0.6979 | 0.8750 | 0.8750 | 0.7848 | 1.26 ms |
| collaborative_filtering | 0.0500 | 0.5000 | 0.1526 | 0.0576 | 0.5000 | 0.9583 | 0.7720 | 0.05 ms |
| popularity | 0.0250 | 0.2500 | 0.0915 | 0.0451 | 0.2500 | 0.7500 | 0.7697 | 0.02 ms |

## Dataset

The benchmark uses two canonical CSV files:

- `anime.csv`: anime metadata such as title, synopsis, genres, studios, score,
  members, year, and image URL
- `ratings.csv`: anonymous `user_id`, `anime_id`, rating, and timestamp

`python -m scripts.prepare_dataset --sample` creates:

- `data/processed/anime.csv`
- `data/processed/ratings.csv`
- `data/processed/train.csv`
- `data/processed/validation.csv`
- `data/processed/test.csv`
- `data/processed/manifest.json`

See [docs/dataset_card.md](docs/dataset_card.md) for the full schema and split
strategy.

## Recommendation Approaches

| Model | Purpose |
| --- | --- |
| Popularity | Provides a cold-start and quality/popularity baseline |
| Content-based | Recommends anime similar to the user's highly rated metadata profile |
| Collaborative filtering | Uses item-item similarity from user-rating overlap |
| Hybrid | Combines popularity, content, and collaborative scores |

Advanced models remain on the roadmap, but they should be added only after they
can run through the same evaluation harness:

- matrix factorization/SVD
- SBERT semantic search
- CLIP visual search
- BERT4Rec sequential recommendation
- GNN recommendation
- LLM-based explanations

See [docs/model_card.md](docs/model_card.md).

## Evaluation Methodology

The default config is [configs/eval.yaml](configs/eval.yaml).

- split: deterministic leave-last-two-out per user
- relevant item: rating greater than or equal to `8.0`
- ranking cutoff: `K=10`
- reported metrics: Precision@K, Recall@K, NDCG@K, MAP@K, HitRate@K, coverage,
  diversity, and mean latency

This setup makes future models comparable because they must use the same data,
same split, same relevance threshold, and same metrics.

## Backend API Direction

The repository already contains a FastAPI backend under `app/`, but the public
portfolio path should be narrowed around the recommender engine. The next backend
layer should expose:

- `GET /health`
- `GET /models`
- `POST /recommend`
- `POST /similar-anime`
- `POST /evaluate`

Auth, social features, reviews, dashboards, and account management are not part
of the current portfolio proof.

## Project Structure

```text
AniVibe/
|-- recommender/              # Offline data, models, metrics, evaluation
|-- scripts/
|   |-- prepare_dataset.py    # Build canonical processed data and splits
|   |-- evaluate_recommenders.py
|   `-- generate_report.py
|-- configs/
|   `-- eval.yaml             # Reproducible benchmark config
|-- data/
|   `-- sample/               # Small checked-in reproducibility fixture
|-- docs/
|   |-- dataset_card.md
|   |-- model_card.md
|   `-- architecture.md
|-- tests/
|   `-- test_offline_recommender.py
|-- app/                      # Existing FastAPI backend
|-- frontend/                 # Existing Next.js frontend
`-- README.md
```

## Testing

Run the offline recommender tests:

```bash
pytest tests/test_offline_recommender.py -q
```

Run the default test suite:

```bash
pytest tests/ -q
```

Database-backed API tests are disabled by default. Set `RUN_DB_TESTS=1` when a
test database is available.

## Limitations

- The checked-in sample dataset is intentionally small.
- Real portfolio claims require running the same benchmark on a larger public
  ratings dataset.
- The existing backend still contains product/SaaS routes that should be
  cleaned in a later layer.
- The frontend is not the current proof of technical quality.
- Advanced models are roadmap items until they produce comparable metrics.

## Next Layer

The next recommended layer is the clean backend API:

1. expose the offline recommender interface through FastAPI
2. add request/response schemas for recommendation inputs and outputs
3. add `/models` with honest implementation statuses
4. add `/evaluate` as a local benchmark trigger or report reader
5. keep auth/social/frontend out of the main README path until the API is stable

## License

MIT. See [LICENSE](LICENSE).
