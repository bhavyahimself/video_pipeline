"""
ClipEngine — Analytics Endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.models.video import Video, VideoStatus
from app.schemas import OverviewAnalytics
from app.services.auth_service import get_current_user

router = APIRouter()


@router.get("/overview", response_model=OverviewAnalytics)
async def get_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get usage overview analytics."""
    # Total videos
    total_result = await db.execute(
        select(func.count(Video.id)).where(Video.user_id == current_user.id)
    )
    total_videos = total_result.scalar() or 0

    # Videos this month
    from datetime import datetime, timedelta
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    month_result = await db.execute(
        select(func.count(Video.id)).where(
            Video.user_id == current_user.id,
            Video.created_at >= month_start,
        )
    )
    videos_this_month = month_result.scalar() or 0

    # Total duration
    duration_result = await db.execute(
        select(func.sum(Video.duration_seconds)).where(
            Video.user_id == current_user.id,
            Video.status == VideoStatus.DONE,
        )
    )
    total_duration = (duration_result.scalar() or 0) / 60  # minutes

    # Channel breakdown
    channel_result = await db.execute(
        select(Video.channel_type, func.count(Video.id))
        .where(Video.user_id == current_user.id)
        .group_by(Video.channel_type)
    )
    channel_breakdown = {row[0]: row[1] for row in channel_result}

    return OverviewAnalytics(
        total_videos=total_videos,
        videos_this_month=videos_this_month,
        total_duration_minutes=round(total_duration, 1),
        avg_generation_time_seconds=0,  # TODO: compute from job data
        channel_breakdown=channel_breakdown,
        daily_videos=[],  # TODO: daily breakdown
    )

