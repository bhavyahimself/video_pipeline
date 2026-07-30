"""
ClipEngine — Channel Endpoints
List system channels, manage custom channels.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User, PlanTier
from app.models.channel import Channel
from app.schemas import SystemChannelResponse, ChannelCreateRequest, ChannelResponse
from app.services.auth_service import get_current_user

router = APIRouter()


# Import system channels from engine
SYSTEM_CHANNELS = None


def _get_system_channels():
    global SYSTEM_CHANNELS
    if SYSTEM_CHANNELS is None:
        import sys
        from pathlib import Path
        # Add engine to path
        engine_path = Path(__file__).parent.parent.parent.parent / "engine"
        sys.path.insert(0, str(engine_path))
        from config.settings import CHANNELS
        SYSTEM_CHANNELS = CHANNELS
    return SYSTEM_CHANNELS


@router.get("", response_model=list[SystemChannelResponse])
async def list_channels(current_user: User = Depends(get_current_user)):
    """List all available channels (system + user custom)."""
    channels = _get_system_channels()
    return [
        SystemChannelResponse(
            key=key,
            name=ch.name,
            tone=ch.tone,
            target_duration_seconds=ch.target_duration_seconds,
            clip_sources=ch.clip_sources,
        )
        for key, ch in channels.items()
    ]


@router.get("/custom", response_model=list[ChannelResponse])
async def list_custom_channels(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List user's custom channels (Studio+ only)."""
    result = await db.execute(
        select(Channel).where(Channel.user_id == current_user.id)
    )
    return result.scalars().all()


@router.post("/custom", response_model=ChannelResponse, status_code=status.HTTP_201_CREATED)
async def create_custom_channel(
    body: ChannelCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a custom channel. Studio+ only."""
    if current_user.plan not in (PlanTier.STUDIO, PlanTier.ENTERPRISE):
        raise HTTPException(
            status_code=403,
            detail="Custom channels require Studio or Enterprise plan"
        )

    # Generate slug
    slug = body.name.lower().replace(" ", "_").replace("-", "_")[:100]

    channel = Channel(
        user_id=current_user.id,
        name=body.name,
        slug=slug,
        tone=body.tone,
        format_guide=body.format_guide,
        target_duration_seconds=body.target_duration_seconds,
        voice_id=body.voice_id,
        clip_sources=body.clip_sources,
        stock_keywords=body.stock_keywords,
        is_public=body.is_public,
    )
    db.add(channel)
    await db.flush()

    return channel


@router.get("/marketplace", response_model=list[ChannelResponse])
async def marketplace_channels(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Browse public channels from the marketplace."""
    result = await db.execute(
        select(Channel).where(Channel.is_public == True).order_by(Channel.uses_count.desc())
    )
    return result.scalars().all()

