"""
ClipEngine — Database Models: Channel, Team, Template
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Boolean, Float, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY

from app.db.session import Base


class Channel(Base):
    """User-created custom channels (Studio+ only). System channels are in engine config."""
    __tablename__ = "channels"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    name = Column(String(255), nullable=False)
    slug = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    tone = Column(Text, nullable=False)
    format_guide = Column(Text, nullable=False)
    target_duration_seconds = Column(Integer, default=55)

    voice_id = Column(String(255), nullable=True)
    voice_stability = Column(Float, default=0.5)
    voice_similarity = Column(Float, default=0.75)

    clip_sources = Column(JSONB, default=list)
    stock_keywords = Column(JSONB, default=list)

    # Marketplace
    is_public = Column(Boolean, default=False)
    uses_count = Column(Integer, default=0)
    rating = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Team(Base):
    """Team workspaces for Studio+ plans."""
    __tablename__ = "teams"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class TeamMember(Base):
    __tablename__ = "team_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    role = Column(String(50), default="member")  # owner, admin, member, viewer
    invited_at = Column(DateTime, default=datetime.utcnow)
    accepted_at = Column(DateTime, nullable=True)


class Template(Base):
    """Reusable channel templates for marketplace."""
    __tablename__ = "templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    preview_thumbnail_url = Column(String(500), nullable=True)

    # Channel config snapshot
    channel_config = Column(JSONB, nullable=False)

    # Marketplace
    is_featured = Column(Boolean, default=False)
    downloads_count = Column(Integer, default=0)
    rating = Column(Float, nullable=True)
    price_cents = Column(Integer, default=0)  # 0 = free

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

