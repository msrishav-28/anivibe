"""
Pure Supabase configuration
"""
from typing import List, Optional
import os
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings - Supabase only"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"
    )
    
    # ==========================================
    # APPLICATION
    # ==========================================
    app_name: str = "AniVibe"
    app_version: str = "1.0.0"
    environment: str = Field(default="development")
    debug: bool = Field(default=True)
    api_v1_prefix: str = "/api/v1"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # ==========================================
    # SECURITY
    # ==========================================
    # ==========================================
    # SECURITY
    # ==========================================
    secret_key: str = Field(default_factory=lambda: os.getenv("SECRET_KEY", "insecure-development-key-change-me"), min_length=32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # ==========================================
    # SUPABASE (Single Source of Truth)
    # ==========================================
    supabase_url: str = Field(default_factory=lambda: os.getenv("SUPABASE_URL", ""), description="https://xxxxx.supabase.co")
    supabase_anon_key: str = Field(default_factory=lambda: os.getenv("SUPABASE_ANON_KEY", ""), description="Public anon key")
    supabase_service_key: str = Field(default_factory=lambda: os.getenv("SUPABASE_SERVICE_KEY", ""), description="Service role key (server only)")
    supabase_db_password: str = Field(default_factory=lambda: os.getenv("SUPABASE_DB_PASSWORD", ""), description="Database password")
    
    @property
    def database_url(self) -> str:
        """
        Supabase PostgreSQL connection via Pooler or Direct.
        """
        # If explicit DATABASE_URL is set (e.g. on Render), use it
        if os.getenv("DATABASE_URL"):
            return os.getenv("DATABASE_URL")
            
        project_ref = self.supabase_url.replace("https://", "").split(".")[0]
        
        # Session pooler (port 5432) for app connections
        # Prefer environment variable for host to avoid region lock
        db_host = os.getenv("SUPABASE_DB_HOST", "aws-0-ap-south-1.pooler.supabase.com")
        
        return (
            f"postgresql+asyncpg://postgres.{project_ref}:"
            f"{self.supabase_db_password}@"
            f"{db_host}:5432/postgres"
        )
    
    @property 
    def database_url_sync(self) -> str:
        """Synchronous connection for Alembic migrations"""
        if os.getenv("DATABASE_URL"):
            return os.getenv("DATABASE_URL").replace("+asyncpg", "")

        project_ref = self.supabase_url.replace("https://", "").split(".")[0]
        db_host = os.getenv("SUPABASE_DB_HOST", "aws-0-ap-south-1.pooler.supabase.com")
        
        # Transaction pooler (port 6543) for migrations
        return (
            f"postgresql://postgres.{project_ref}:"
            f"{self.supabase_db_password}@"
            f"{db_host}:6543/postgres"
        )
    
    # ==========================================
    # REDIS (Caching Only)
    # ==========================================
    redis_url_env: Optional[str] = Field(default_factory=lambda: os.getenv("REDIS_URL"), description="Redis Connection URL")
    
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: Optional[str] = None
    redis_db: int = 0
    cache_ttl: int = 3600  # 1 hour default
    
    @property
    def redis_url(self) -> str:
        if self.redis_url_env:
            return self.redis_url_env
            
        auth = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    # ==========================================
    # EXTERNAL APIs
    # ==========================================
    jikan_api_url: str = "https://api.jikan.moe/v4"
    anilist_api_url: str = "https://graphql.anilist.co"
    gemini_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY"))
    
    # OAuth
    mal_client_id: Optional[str] = Field(default_factory=lambda: os.getenv("MAL_CLIENT_ID"))
    mal_client_secret: Optional[str] = Field(default_factory=lambda: os.getenv("MAL_CLIENT_SECRET"))
    anilist_client_id: Optional[str] = Field(default_factory=lambda: os.getenv("ANILIST_CLIENT_ID"))
    anilist_client_secret: Optional[str] = Field(default_factory=lambda: os.getenv("ANILIST_CLIENT_SECRET"))
    
    # ==========================================
    # ML SERVICE (Separate Microservice)
    # ==========================================
    ml_service_url: str = Field(
        default_factory=lambda: os.getenv("ML_SERVICE_URL", "http://localhost:8080"),
        description="Modal/HuggingFace ML endpoint"
    )
    ml_service_timeout: int = 30
    
    # Feature Toggles (Enable progressively)
    enable_recommendations: bool = True
    enable_image_search: bool = Field(default=True)
    enable_gnn: bool = Field(default=False)
    enable_bert4rec: bool = Field(default=False)
    
    # ML Model Config
    use_gpu: bool = Field(default=False)
    model_cache_dir: str = "./models/cache"
    
    @property
    def device(self) -> str:
        """Auto-detect GPU availability"""
        if not self.use_gpu:
            return "cpu"
        
        try:
            import torch
            return "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            return "cpu"
    
    # Lightweight models (SBERT can run in main app)
    sbert_model_name: str = "all-MiniLM-L6-v2"  # 80MB only
    
    # Heavy models (CLIP, GNN) - offload to Modal
    clip_model_name: str = "ViT-B-32"
    
    # ==========================================
    # RATE LIMITING
    # ==========================================
    rate_limit_per_minute: int = 60
    rate_limit_burst: int = 20
    
    # ==========================================
    # LOGGING
    # ==========================================
    log_level: str = "INFO"
    log_file: str = "logs/anivibe.log"
    
    # ==========================================
    # CORS
    # ==========================================
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000", "https://anivibe.vercel.app"]
    )
    cors_allow_credentials: bool = True
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    # ==========================================
    # FILE STORAGE (Supabase Storage)
    # ==========================================
    supabase_storage_bucket: str = "anime-images"
    max_upload_size: int = 10485760  # 10MB
    
    # ==========================================
    # PROPERTIES
    # ==========================================
    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        return self.environment.lower() == "development"


# Global settings instance
settings = Settings()
