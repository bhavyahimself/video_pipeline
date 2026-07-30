"""
ClipEngine — Plan Enforcement Middleware
Enforces video quotas and feature access based on subscription tier.
"""

from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.user import User, PlanTier

settings = get_settings()

# Which channels each plan can access
PLAN_CHANNELS = {
    PlanTier.FREE: settings.FREE_CHANNELS,
    PlanTier.CREATOR: "all",
    PlanTier.STUDIO: "all",
    PlanTier.ENTERPRISE: "all",
}

# Video limits per plan
PLAN_VIDEO_LIMITS = {
    PlanTier.FREE: settings.FREE_VIDEO_LIMIT,
    PlanTier.CREATOR: settings.CREATOR_VIDEO_LIMIT,
    PlanTier.STUDIO: settings.STUDIO_VIDEO_LIMIT,
    PlanTier.ENTERPRISE: settings.ENTERPRISE_VIDEO_LIMIT,
}


async def enforce_video_quota(user: User, db: AsyncSession):
    """Check if user has remaining video quota for this billing period."""
    limit = PLAN_VIDEO_LIMITS.get(user.plan, 3)
    used = user.videos_used_this_period

    # Check period reset
    from datetime import datetime
    if user.period_reset_date and datetime.utcnow() > user.period_reset_date:
        user.videos_used_this_period = 0
        from datetime import timedelta
        user.period_reset_date = datetime.utcnow() + timedelta(days=30)
        used = 0

    if used >= limit:
        raise HTTPException(
            status_code=429,
            detail=f"Video quota exceeded. You've used {used}/{limit} videos this period. "
                   f"Upgrade your plan for more videos."
        )


def get_allowed_channels(plan: PlanTier) -> list[str] | str:
    """Get the list of channels allowed for a plan tier."""
    return PLAN_CHANNELS.get(plan, settings.FREE_CHANNELS)


def can_use_feature(user: User, feature: str) -> bool:
    """Check if a user's plan allows access to a specific feature."""
    feature_requirements = {
        "custom_channels": [PlanTier.STUDIO, PlanTier.ENTERPRISE],
        "batch_generation": [PlanTier.STUDIO, PlanTier.ENTERPRISE],
        "api_access": [PlanTier.STUDIO, PlanTier.ENTERPRISE],
        "team": [PlanTier.STUDIO, PlanTier.ENTERPRISE],
        "youtube_upload": [PlanTier.CREATOR, PlanTier.STUDIO, PlanTier.ENTERPRISE],
        "voice_selection": [PlanTier.CREATOR, PlanTier.STUDIO, PlanTier.ENTERPRISE],
        "ab_testing": [PlanTier.STUDIO, PlanTier.ENTERPRISE],
        "analytics_export": [PlanTier.STUDIO, PlanTier.ENTERPRISE],
        "white_label": [PlanTier.ENTERPRISE],
        "scheduled_publishing": [PlanTier.ENTERPRISE],
    }

    required_plans = feature_requirements.get(feature, [])
    return user.plan in required_plans

