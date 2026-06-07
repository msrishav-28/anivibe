"""
API v1 routes
"""
from fastapi import APIRouter
from app.api.v1 import auth, users, anime, recommendations, watchlist, ratings, search, explain, reviews, analytics, atlas, social

api_router = APIRouter()

# Include all route modules
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(anime.router, prefix="/anime", tags=["anime"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(watchlist.router, prefix="/watchlist", tags=["watchlist"])
api_router.include_router(ratings.router, prefix="/ratings", tags=["ratings"])
api_router.include_router(explain.router, prefix="/explain", tags=["explainability"])
# New routes
# New routes
# Social router removed as per strategy
api_router.include_router(social.router, prefix="/social", tags=["social"])
# Note: api-client expects /anime/{id}/reviews. 
# FastAPI routers can be included multiple times or we just use global /reviews prefix 
# and the path inside reviews.py handles it.
# reviews.py has /anime/{id}/reviews. If prefix is /reviews, path becomes /reviews/anime/{id}/reviews. 
# We should include it without prefix or with empty prefix if paths are absolute?
# Or update reviews.py to not include /anime/{id} if prefix handles it.
# Let's include with empty prefix for maximum flexibility for now, as reviews.py defines full paths or compatible ones.
api_router.include_router(reviews.router, tags=["reviews"]) 
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
# api_router.include_router(atlas.router, prefix="/atlas", tags=["atlas"])
