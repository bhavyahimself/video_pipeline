"""
ClipEngine — Database Models: Video, Project, Job
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, String, DateTime, Boolean, Float, Integer, Enum, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.session import Base


class VideoStatus(str, PyEnum):
    QUEUED = "queued"
    RESEARCHING = "researching"
    SCRIPTING = "scripting"
    CLIPPING = "clipping"
    VOICING = "voicing"
    ASSEMBLING = "assembling"
    CAPTIONING = "captioning"
    THUMBNAILING = "thumbnailing"
    DONE = "done"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobPriority(str, PyEnum):
    FREE = "free"
    CREATOR = "creator"
    PRIORITY = "priority"


class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    default_channel = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="projects")
    videos = relationship("Video", back_populates="project", lazy="dynamic")


class Video(Base):
    __tablename__ = "videos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)

    # Content
    topic = Column(String(500), nullable=False)
    channel_type = Column(String(100), nullable=False)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)

    # Status
    status = Column(Enum(VideoStatus), default=VideoStatus.QUEUED, nullable=False)
    is_watermarked = Column(Boolean, default=False)

    # Generated Assets (S3 URLs)
    script_content = Column(Text, nullable=True)
    voiceover_url = Column(String(500), nullable=True)
    video_url = Column(String(500), nullable=True)
    thumbnail_url = Column(String(500), nullable=True)
    caption_url = Column(String(500), nullable=True)

    # Metadata
    duration_seconds = Column(Float, nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    visual_cues = Column(JSONB, nullable=True)
    metadata = Column(JSONB, nullable=True)

    # YouTube
    youtube_video_id = Column(String(50), nullable=True)
    youtube_uploaded_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="videos")
    project = relationship("Project", back_populates="videos")
    script = relationship("Script", back_populates="video", uselist=False)
    job = relationship("Job", back_populates="video", uselist=False)


class Script(Base):
    __tablename__ = "scripts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    content = Column(Text, nullable=False)
    version = Column(Integer, default=1)
    channel_type = Column(String(100), nullable=False)
    visual_cues = Column(JSONB, nullable=True)

    # Version history stored as JSONB array
    version_history = Column(JSONB, default=list)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="scripts")
    video = relationship("Video", back_populates="script")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    celery_task_id = Column(String(255), nullable=True)
    status = Column(Enum(VideoStatus), default=VideoStatus.QUEUED, nullable=False)
    priority = Column(Enum(JobPriority), default=JobPriority.FREE, nullable=False)

    progress_pct = Column(Integer, default=0)
    current_step = Column(String(100), nullable=True)
    current_step_detail = Column(String(500), nullable=True)

    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    video = relationship("Video", back_populates="job")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    plan = Column(String(50), nullable=False)
    stripe_subscription_id = Column(String(255), nullable=True)
    stripe_price_id = Column(String(255), nullable=True)
    status = Column(String(50), default="active")  # active, cancelled, past_due, trialing

    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    cancel_at_period_end = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="subscriptions")

