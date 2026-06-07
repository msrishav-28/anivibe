# Model Card

## Current Implemented Benchmark Models

| Model | Status | Purpose |
| --- | --- | --- |
| Popularity | Implemented baseline | Cold-start and sanity-check recommender |
| Content-based | Implemented baseline | Metadata similarity using title, synopsis, genres, studios, type, and year |
| Collaborative filtering | Implemented baseline | Item-item rating-behavior recommender |
| Hybrid | Implemented baseline | Weighted blend of popularity, content, and collaborative scores |

## Planned Model Roadmap

| Model | Status | Gate Before Claiming |
| --- | --- | --- |
| Matrix factorization/SVD | Planned next | Must run in the same evaluation harness |
| SBERT semantic search | Experimental existing service | Needs offline retrieval evaluation and documented fallback |
| CLIP visual search | Planned experimental | Needs real image embeddings and retrieval metrics |
| BERT4Rec | Planned research | Needs sequential split and comparison to simpler baselines |
| GNN recommender | Planned research | Needs graph construction, training script, and ablation against CF |
| LLM explanations | Optional explanation layer | Should explain recommendations, not replace ranking metrics |

## Evaluation Metrics

The benchmark reports:

- Precision@K
- Recall@K
- NDCG@K
- MAP@K
- HitRate@K
- catalog coverage
- genre diversity
- mean latency in milliseconds

The default config uses `K=10` and treats ratings greater than or equal to `8.0`
as relevant.

## Known Limitations

- The first baseline implementation optimizes clarity and reproducibility over
  large-scale performance.
- Popularity can dominate small datasets.
- Content-based recommendations depend heavily on metadata quality.
- Item-item collaborative filtering needs enough overlapping ratings to be
  useful.
- Hybrid weights are fixed in `configs/eval.yaml`; later work should tune them
  on validation data.
