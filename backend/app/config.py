"""
ClipEngine — Configuration
Centralized settings using Pydantic BaseSettings.
"""

from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ── App ──────────────────────────────────────────────────────────────
    APP_NAME: str = "ClipEngine"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

    # ── Database ─────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://clipengine:clipengine@localhost:5432/clipengine"
    DATABASE_SYNC_URL: str = "postgresql://clipengine:clipengine@localhost:5432/clipengine"

    # ── Redis ────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # ── Auth ─────────────────────────────────────────────────────────────
    JWT_SECRET: str = "jwt-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""

    # ── Storage (S3 / MinIO) ─────────────────────────────────────────────
    S3_ENDPOINT: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET: str = "clipengine"
    S3_REGION: str = "us-east-1"
    S3_PUBLIC_URL: str = "http://localhost:9000/clipengine"

    # ── Stripe ───────────────────────────────────────────────────────────
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRICE_CREATOR: str = ""  # price_xxx for Creator plan
    STRIPE_PRICE_STUDIO: str = ""   # price_xxx for Studio plan
    STRIPE_PRICE_ENTERPRISE: str = ""  # price_xxx for Enterprise plan

    # ── AI APIs ──────────────────────────────────────────────────────────
    OPENAI_API_KEY: str = ""
    ELEVENLABS_API_KEY: str = ""
    ELEVENLABS_DEFAULT_VOICE_ID: str = ""
    PEXELS_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    TWELVE_LABS_API_KEY: str = ""

    # ── YouTube ──────────────────────────────────────────────────────────
    YOUTUBE_API_KEY: str = ""
    YOUTUBE_CLIENT_ID: str = ""
    YOUTUBE_CLIENT_SECRET: str = ""

    # ── Reddit ───────────────────────────────────────────────────────────
    REDDIT_CLIENT_ID: str = ""
    REDDIT_CLIENT_SECRET: str = ""
    REDDIT_USER_AGENT: str = "clipengine/1.0"

    # ── Plan Limits ──────────────────────────────────────────────────────
    FREE_VIDEO_LIMIT: int = 3
    CREATOR_VIDEO_LIMIT: int = 30
    STUDIO_VIDEO_LIMIT: int = 999999  # effectively unlimited
    ENTERPRISE_VIDEO_LIMIT: int = 999999

    FREE_CHANNELS: list[str] = [
        "taylor_sabrina", "how_they_went_broke", "salary_transparent"
    ]

    # ── Rendering ────────────────────────────────────────────────────────
    MAX_CONCURRENT_FREE_JOBS: int = 1
    MAX_CONCURRENT_CREATOR_JOBS: int = 3
    MAX_CONCURRENT_STUDIO_JOBS: int = 5

    WATERMARK_TEXT: str = "Made with ClipEngine"
    WATERMARK_ENABLED_FOR_FREE: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()

