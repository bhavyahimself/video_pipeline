"""
ClipEngine — Video Endpoints
Create, list, get, delete videos. Triggers pipeline via Celery.
"""

from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.session import get_db
from app.models.user import User, PlanTier
from app.models.video import Video, VideoStatus, Job, JobPriority
from app.schemas import (
    VideoCreateRequest,
    VideoBatchCreateRequest,
    VideoResponse,
    VideoListResponse,
)
from app.services.auth_service import get_current_user
from app.middleware.plan_enforcement import enforce_video_quota, get_allowed_channels
from app.tasks.video_tasks import generate_video_task

router = APIRouter()
settings = get_settings()


def _get_job_priority(plan: PlanTier) -> JobPriority:
    if plan in (PlanTier.STUDIO, PlanTier.ENTERPRISE):
        return JobPriority.PRIORITY
    elif plan == PlanTier.CREATOR:
        return JobPriority.CREATOR
    return JobPriority.FREE


@router.post("", response_model=VideoResponse, status_code=status.HTTP_201_CREATED)
async def create_video(
    body: VideoCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new video. Queues the generation pipeline."""
    # Enforce quota
    await enforce_video_quota(current_user, db)

    # Enforce channel access
    allowed_channels = get_allowed_channels(current_user.plan)
    if body.channel_type not in allowed_channels and body.channel_type not in ["all"]:
        raise HTTPException(
            status_code=403,
            detail=f"Channel '{body.channel_type}' not available on your plan. Upgrade to access all channels."
        )

    # Determine watermark
    is_watermarked = current_user.plan == PlanTier.FREE and settings.WATERMARK_ENABLED_FOR_FREE

    # Create video record
    video = Video(
        user_id=current_user.id,
        project_id=body.project_id,
        topic=body.topic,
        channel_type=body.channel_type,
        status=VideoStatus.QUEUED,
        is_watermarked=is_watermarked,
        script_content=body.custom_script,
    )
    db.add(video)
    await db.flush()

    # Create job record
    priority = _get_job_priority(current_user.plan)
    job = Job(
        video_id=video.id,
        user_id=current_user.id,
        status=VideoStatus.QUEUED,
        priority=priority,
        progress_pct=0,
        current_step="queued",
    )
    db.add(job)
    await db.flush()

    # Increment usage
    current_user.videos_used_this_period += 1

    # Queue Celery task
    queue_name = priority.value  # "free", "creator", or "priority"
    task = generate_video_task.apply_async(
        kwargs={
            "video_id": str(video.id),
            "job_id": str(job.id),
            "topic": body.topic,
            "channel_type": body.channel_type,
            "user_id": str(current_user.id),
            "skip_research": body.skip_research,
            "skip_voice": body.skip_voice,
            "skip_captions": body.skip_captions,
            "skip_thumbnail": body.skip_thumbnail,
            "custom_script": body.custom_script,
            "is_watermarked": is_watermarked,
        },
        queue=queue_name,
    )

    # Update job with celery task ID
    job.celery_task_id = task.id
    await db.flush()

    return video


@router.get("", response_model=VideoListResponse)
async def list_videos(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    channel_type: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List user's videos with pagination and filters."""
    query = select(Video).where(Video.user_id == current_user.id)

    if channel_type:
        query = query.where(Video.channel_type == channel_type)
    if status_filter:
        query = query.where(Video.status == status_filter)

    query = query.order_by(Video.created_at.desc())

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    # Paginate
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    videos = result.scalars().all()

    return VideoListResponse(
        videos=[VideoResponse.model_validate(v) for v in videos],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get video details."""
    result = await db.execute(
        select(Video).where(Video.id == video_id, Video.user_id == current_user.id)
    )
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video


@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_video(
    video_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a video and its assets."""
    result = await db.execute(
        select(Video).where(Video.id == video_id, Video.user_id == current_user.id)
    )
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # TODO: Delete S3 assets
    await db.delete(video)


@router.post("/batch", response_model=list[VideoResponse], status_code=status.HTTP_201_CREATED)
async def batch_create_videos(
    body: VideoBatchCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Batch create videos. Studio+ only."""
    if current_user.plan not in (PlanTier.STUDIO, PlanTier.ENTERPRISE):
        raise HTTPException(status_code=403, detail="Batch creation requires Studio or Enterprise plan")

    videos = []
    for topic in body.topics:
        req = VideoCreateRequest(topic=topic, channel_type=body.channel_type, project_id=body.project_id)
        video = await create_video(req, db, current_user)
        videos.append(video)

    return videos

