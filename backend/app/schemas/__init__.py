"""
ClipEngine — Pydantic Schemas
Request/response models for API endpoints.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ── Auth ─────────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    name: str = Field(min_length=1, max_length=255)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    avatar_url: Optional[str] = None
    plan: str
    videos_used_this_period: int
    created_at: datetime

    class Config:
        from_attributes = True


# ── Video ────────────────────────────────────────────────────────────────────

class VideoCreateRequest(BaseModel):
    topic: str = Field(min_length=3, max_length=500)
    channel_type: str
    project_id: Optional[UUID] = None
    voice_id: Optional[str] = None
    skip_research: bool = False
    skip_voice: bool = False
    skip_captions: bool = False
    skip_thumbnail: bool = False
    custom_script: Optional[str] = None


class VideoBatchCreateRequest(BaseModel):
    topics: list[str] = Field(min_length=1, max_length=10)
    channel_type: str
    project_id: Optional[UUID] = None


class VideoResponse(BaseModel):
    id: UUID
    topic: str
    channel_type: str
    title: Optional[str] = None
    status: str
    is_watermarked: bool
    script_content: Optional[str] = None
    voiceover_url: Optional[str] = None
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration_seconds: Optional[float] = None
    youtube_video_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VideoListResponse(BaseModel):
    videos: list[VideoResponse]
    total: int
    page: int
    per_page: int


# ── Script ───────────────────────────────────────────────────────────────────

class ScriptUpdateRequest(BaseModel):
    content: str = Field(min_length=1)


class ScriptResponse(BaseModel):
    id: UUID
    video_id: UUID
    content: str
    version: int
    channel_type: str
    visual_cues: Optional[list] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScriptVersionResponse(BaseModel):
    version: int
    content: str
    created_at: str


# ── Job ──────────────────────────────────────────────────────────────────────

class JobResponse(BaseModel):
    id: UUID
    video_id: UUID
    status: str
    priority: str
    progress_pct: int
    current_step: Optional[str] = None
    current_step_detail: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class JobProgressWS(BaseModel):
    """WebSocket message for job progress updates."""
    job_id: str
    video_id: str
    status: str
    progress_pct: int
    current_step: str
    current_step_detail: str
    eta_seconds: Optional[int] = None


# ── Channel ──────────────────────────────────────────────────────────────────

class SystemChannelResponse(BaseModel):
    key: str
    name: str
    tone: str
    target_duration_seconds: int
    clip_sources: list[str]


class ChannelCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    tone: str
    format_guide: str
    target_duration_seconds: int = 55
    voice_id: Optional[str] = None
    clip_sources: list[str] = []
    stock_keywords: list[str] = []
    is_public: bool = False


class ChannelResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    tone: str
    format_guide: str
    target_duration_seconds: int
    is_public: bool
    uses_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# ── Billing ──────────────────────────────────────────────────────────────────

class PlanInfo(BaseModel):
    name: str
    price_monthly: int
    videos_per_month: int | str
    channels: str
    features: list[str]


class CheckoutRequest(BaseModel):
    plan: str  # creator, studio, enterprise
    success_url: str
    cancel_url: str


class CheckoutResponse(BaseModel):
    checkout_url: str


class UsageResponse(BaseModel):
    plan: str
    videos_used: int
    videos_limit: int | str
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None


# ── Project ──────────────────────────────────────────────────────────────────

class ProjectCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    default_channel: Optional[str] = None


class ProjectResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    default_channel: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ── Analytics ────────────────────────────────────────────────────────────────

class OverviewAnalytics(BaseModel):
    total_videos: int
    videos_this_month: int
    total_duration_minutes: float
    avg_generation_time_seconds: float
    channel_breakdown: dict[str, int]
    daily_videos: list[dict]  # [{date, count}]

