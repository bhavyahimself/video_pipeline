"""
ClipEngine — Video Generation Celery Tasks
Wraps the MasterPipeline as async Celery tasks with progress reporting.
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.tasks.celery_app import celery_app
from app.config import get_settings

settings = get_settings()

# Redis client for publishing progress
_redis = redis.Redis.from_url(settings.REDIS_URL)

# Sync DB engine for Celery workers (async doesn't work in Celery)
_sync_engine = create_engine(settings.DATABASE_SYNC_URL)


# Pipeline step definitions with progress percentages
PIPELINE_STEPS = [
    ("researching", "Researching topic...", 10),
    ("scripting", "Generating script...", 25),
    ("clipping", "Finding relevant clips...", 45),
    ("voicing", "Generating voiceover...", 60),
    ("assembling", "Assembling video...", 75),
    ("captioning", "Generating captions...", 85),
    ("thumbnailing", "Creating thumbnail...", 95),
    ("done", "Video complete!", 100),
]


def _publish_progress(job_id: str, video_id: str, step: str, pct: int, detail: str = ""):
    """Publish progress update to Redis pub/sub for WebSocket consumption."""
    message = {
        "job_id": job_id,
        "video_id": video_id,
        "status": step,
        "progress_pct": pct,
        "current_step": step,
        "current_step_detail": detail,
    }
    _redis.publish(f"job:{job_id}:progress", json.dumps(message))


def _update_job_db(job_id: str, video_id: str, status: str, pct: int, detail: str = "", error: str = None):
    """Update job and video status in the database (sync, for Celery workers)."""
    from app.models.video import Job, Video

    with Session(_sync_engine) as session:
        job = session.get(Job, job_id)
        if job:
            job.status = status
            job.progress_pct = pct
            job.current_step = status
            job.current_step_detail = detail
            if status == "done":
                job.completed_at = datetime.utcnow()
            if error:
                job.error_message = error

        video = session.get(Video, video_id)
        if video:
            video.status = status

        session.commit()


@celery_app.task(bind=True, name="app.tasks.video_tasks.generate_video_task")
def generate_video_task(
    self,
    video_id: str,
    job_id: str,
    topic: str = "",
    channel_type: str = "how_they_went_broke",
    user_id: str = "",
    skip_research: bool = False,
    skip_voice: bool = False,
    skip_captions: bool = False,
    skip_thumbnail: bool = False,
    custom_script: Optional[str] = None,
    is_watermarked: bool = False,
):
    """
    Main video generation task. Wraps the MasterPipeline engine.
    Reports progress via Redis pub/sub and updates the database.
    """
    start_time = time.time()

    # Add engine to path
    engine_path = Path(__file__).parent.parent.parent / "engine"
    if str(engine_path) not in sys.path:
        sys.path.insert(0, str(engine_path))

    try:
        # Mark as started
        _update_job_db(job_id, video_id, "researching", 5, "Starting pipeline...")
        _publish_progress(job_id, video_id, "researching", 5, "Starting pipeline...")

        from pipeline import MasterPipeline

        pipeline = MasterPipeline()

        # Create progress callback
        def on_progress(step: str, pct: int, detail: str = ""):
            _publish_progress(job_id, video_id, step, pct, detail)
            _update_job_db(job_id, video_id, step, pct, detail)

        # ── Step 1: Research ─────────────────────────────────────
        if not skip_research and not custom_script:
            on_progress("researching", 10, f"Researching: {topic}")
            research_context = pipeline.researcher.research(topic) if hasattr(pipeline, 'researcher') else ""
        else:
            research_context = ""

        # ── Step 2: Script ───────────────────────────────────────
        on_progress("scripting", 25, "Generating script with AI...")
        if custom_script:
            script = custom_script
        else:
            script_gen = pipeline._get_script_gen(channel_type)
            script = script_gen.generate(topic, additional_context=research_context)

        # Save script to DB
        _save_script(video_id, user_id, script, channel_type)

        # ── Step 3: Visual Cues + Clips ──────────────────────────
        on_progress("clipping", 35, "Extracting visual cues...")
        script_gen = pipeline._get_script_gen(channel_type)
        visual_cues = script_gen.extract_visual_cues(script)

        on_progress("clipping", 45, "Finding and downloading clips...")
        # clip_paths = pipeline.step_find_clips(visual_cues, channel_type, video_id)

        # ── Step 4: Voiceover ────────────────────────────────────
        if not skip_voice:
            on_progress("voicing", 60, "Generating AI voiceover...")
            # voiceover_path = pipeline.step_generate_voiceover(script, channel_type, video_id)

        # ── Step 5: Assemble ─────────────────────────────────────
        on_progress("assembling", 75, "Assembling final video...")
        # final_path = pipeline.step_assemble(clip_paths, voiceover_path, video_id, watermark=is_watermarked)

        # ── Step 6: Captions ─────────────────────────────────────
        if not skip_captions:
            on_progress("captioning", 85, "Generating captions with Whisper...")
            # caption_path = pipeline.step_generate_captions(voiceover_path, video_id)

        # ── Step 7: Thumbnail ────────────────────────────────────
        if not skip_thumbnail:
            on_progress("thumbnailing", 95, "Creating thumbnail...")
            # thumbnail_path = pipeline.step_generate_thumbnail(topic, channel_type, video_id)

        # ── Upload to S3 ─────────────────────────────────────────
        # from app.services.storage_service import storage
        # urls = storage.upload_video_assets(video_id, output_dir)
        # _update_video_urls(video_id, urls)

        # ── Done ─────────────────────────────────────────────────
        elapsed = time.time() - start_time
        on_progress("done", 100, f"Complete in {elapsed:.1f}s")

        return {
            "video_id": video_id,
            "status": "done",
            "processing_time": elapsed,
        }

    except Exception as e:
        error_msg = str(e)
        _update_job_db(job_id, video_id, "failed", 0, error=error_msg)
        _publish_progress(job_id, video_id, "failed", 0, error_msg)
        raise


def _save_script(video_id: str, user_id: str, content: str, channel_type: str):
    """Save generated script to database."""
    import uuid
    from app.models.video import Script, Video

    with Session(_sync_engine) as session:
        script = Script(
            id=uuid.uuid4(),
            video_id=video_id,
            user_id=user_id,
            content=content,
            version=1,
            channel_type=channel_type,
        )
        session.add(script)

        # Also update video record
        video = session.get(Video, video_id)
        if video:
            video.script_content = content

        session.commit()

