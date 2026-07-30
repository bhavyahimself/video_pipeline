"""
ClipEngine — Script Endpoints
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.models.video import Script
from app.schemas import ScriptResponse, ScriptUpdateRequest, ScriptVersionResponse
from app.services.auth_service import get_current_user

router = APIRouter()


@router.get("/{script_id}", response_model=ScriptResponse)
async def get_script(
    script_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a script by ID."""
    result = await db.execute(
        select(Script).where(Script.id == script_id, Script.user_id == current_user.id)
    )
    script = result.scalar_one_or_none()
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    return script


@router.put("/{script_id}", response_model=ScriptResponse)
async def update_script(
    script_id: UUID,
    body: ScriptUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a script. Saves the old version to history."""
    result = await db.execute(
        select(Script).where(Script.id == script_id, Script.user_id == current_user.id)
    )
    script = result.scalar_one_or_none()
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")

    # Save current version to history
    version_entry = {
        "version": script.version,
        "content": script.content,
        "created_at": script.updated_at.isoformat() if script.updated_at else "",
    }
    history = script.version_history or []
    history.append(version_entry)
    script.version_history = history

    # Update to new content
    script.content = body.content
    script.version += 1

    await db.flush()
    return script


@router.get("/{script_id}/versions", response_model=list[ScriptVersionResponse])
async def get_script_versions(
    script_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all versions of a script."""
    result = await db.execute(
        select(Script).where(Script.id == script_id, Script.user_id == current_user.id)
    )
    script = result.scalar_one_or_none()
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")

    versions = []
    for entry in (script.version_history or []):
        versions.append(ScriptVersionResponse(**entry))

    # Add current version
    versions.append(ScriptVersionResponse(
        version=script.version,
        content=script.content,
        created_at=script.updated_at.isoformat() if script.updated_at else "",
    ))

    return versions


@router.post("/{script_id}/regenerate", response_model=ScriptResponse)
async def regenerate_script(
    script_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Regenerate a script using AI. Saves current as version."""
    result = await db.execute(
        select(Script).where(Script.id == script_id, Script.user_id == current_user.id)
    )
    script = result.scalar_one_or_none()
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")

    # Save current version
    history = script.version_history or []
    history.append({
        "version": script.version,
        "content": script.content,
        "created_at": script.updated_at.isoformat() if script.updated_at else "",
    })
    script.version_history = history

    # Regenerate using engine
    from app.services.video_service import regenerate_script_content
    new_content = await regenerate_script_content(
        topic=script.content[:200],  # Use beginning as topic hint
        channel_type=script.channel_type,
    )

    script.content = new_content
    script.version += 1
    await db.flush()

    return script

