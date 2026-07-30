"""
ClipEngine — Job Endpoints
Job status, cancel, retry.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.models.video import Job, VideoStatus
from app.schemas import JobResponse
from app.services.auth_service import get_current_user

router = APIRouter()


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get job status and progress."""
    result = await db.execute(
        select(Job).where(Job.id == job_id, Job.user_id == current_user.id)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/{job_id}/cancel")
async def cancel_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cancel a running or queued job."""
    result = await db.execute(
        select(Job).where(Job.id == job_id, Job.user_id == current_user.id)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status in (VideoStatus.DONE, VideoStatus.FAILED, VideoStatus.CANCELLED):
        raise HTTPException(status_code=400, detail="Job is already finished")

    # Revoke Celery task
    if job.celery_task_id:
        from app.tasks.celery_app import celery_app
        celery_app.control.revoke(job.celery_task_id, terminate=True)

    job.status = VideoStatus.CANCELLED
    await db.flush()

    return {"status": "cancelled", "job_id": str(job_id)}


@router.post("/{job_id}/retry", response_model=JobResponse)
async def retry_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retry a failed job."""
    result = await db.execute(
        select(Job).where(Job.id == job_id, Job.user_id == current_user.id)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != VideoStatus.FAILED:
        raise HTTPException(status_code=400, detail="Only failed jobs can be retried")

    # Re-queue the task
    job.status = VideoStatus.QUEUED
    job.progress_pct = 0
    job.current_step = "queued"
    job.error_message = None

    from app.tasks.video_tasks import generate_video_task
    task = generate_video_task.apply_async(
        kwargs={
            "video_id": str(job.video_id),
            "job_id": str(job.id),
        },
        queue=job.priority.value,
    )
    job.celery_task_id = task.id
    await db.flush()

    return job

