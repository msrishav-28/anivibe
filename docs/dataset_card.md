# Dataset Card

## Purpose

AniVibe uses anime metadata and user-anime ratings to evaluate recommendation
models. The first portfolio milestone is an offline benchmark that can run
without Supabase, Modal, auth, or the frontend.

## Canonical Schema

### `anime.csv`

Required columns:

| Column | Type | Description |
| --- | --- | --- |
| `anime_id` | integer | Stable internal anime identifier |
| `title` | string | Display title |
| `synopsis` | string | Short text description used by content models |
| `genres` | pipe-delimited string | Genre labels such as `Action|Drama` |
| `studios` | pipe-delimited string | Studio labels such as `MAPPA|Wit Studio` |
| `type` | string | TV, Movie, OVA, or other release type |
| `episodes` | integer | Episode count, `0` when unknown |
| `score` | float | Catalog-level score on a 0-10 scale |
| `members` | integer | Popularity proxy from catalog membership/count data |
| `year` | integer | Release year, `0` when unknown |
| `image_url` | string | Poster or cover URL |

### `ratings.csv`

Required columns:

| Column | Type | Description |
| --- | --- | --- |
| `user_id` | string | Anonymous profile identifier |
| `anime_id` | integer | Foreign key to `anime.csv` |
| `rating` | float | User rating on a 0-10 scale |
| `timestamp` | string | Ordering field for deterministic split generation |

## Included Sample Data

The repository includes a small sample dataset under `data/sample/` so a fresh
clone can run the benchmark immediately:

```bash
python -m scripts.prepare_dataset --sample
python -m scripts.evaluate_recommenders --config configs/eval.yaml
```

The sample data is not intended to support final model-quality claims. It is a
fixture for reproducibility, API shape, metrics validation, and tests.

## Split Strategy

The first benchmark uses deterministic leave-last-two-out splitting per user:

- latest interaction: test
- second latest interaction: validation
- earlier interactions: train

Users with too few interactions stay in training so they do not create invalid
evaluation cases.

## Limitations

- The checked-in sample is small and hand-curated for local reproducibility.
- Portfolio-grade results require the same pipeline on a larger public ratings
  dataset.
- Raw third-party datasets should not be committed unless their license allows
  redistribution.
- Missing values, duplicate anime IDs, duplicate ratings, and unknown catalog
  IDs must be handled during preparation before any model comparison is trusted.
