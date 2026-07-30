"""
ClipEngine — Database Models: User
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, String, DateTime, Boolean, Enum, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class PlanTier(str, PyEnum):
    FREE = "free"
    CREATOR = "creator"
    STUDIO = "studio"
    ENTERPRISE = "enterprise"


class AuthProvider(str, PyEnum):
    LOCAL = "local"
    GOOGLE = "google"
    GITHUB = "github"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    hashed_password = Column(String(255), nullable=True)  # Null for OAuth users
    auth_provider = Column(Enum(AuthProvider), default=AuthProvider.LOCAL)
    auth_provider_id = Column(String(255), nullable=True)

    # Subscription
    plan = Column(Enum(PlanTier), default=PlanTier.FREE, nullable=False)
    stripe_customer_id = Column(String(255), nullable=True)
    videos_used_this_period = Column(Integer, default=0)
    period_reset_date = Column(DateTime, nullable=True)

    # API Keys (encrypted)
    openai_api_key_encrypted = Column(Text, nullable=True)
    elevenlabs_api_key_encrypted = Column(Text, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    videos = relationship("Video", back_populates="user", lazy="dynamic")
    projects = relationship("Project", back_populates="user", lazy="dynamic")
    scripts = relationship("Script", back_populates="user", lazy="dynamic")
    subscriptions = relationship("Subscription", back_populates="user", lazy="dynamic")

