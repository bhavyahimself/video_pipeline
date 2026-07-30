"""
ClipEngine — API v1 Router
"""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.videos import router as videos_router
from app.api.v1.scripts import router as scripts_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.channels import router as channels_router
from app.api.v1.billing import router as billing_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.websocket import router as ws_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
router.include_router(videos_router, prefix="/videos", tags=["Videos"])
router.include_router(scripts_router, prefix="/scripts", tags=["Scripts"])
router.include_router(jobs_router, prefix="/jobs", tags=["Jobs"])
router.include_router(channels_router, prefix="/channels", tags=["Channels"])
router.include_router(billing_router, prefix="/billing", tags=["Billing"])
router.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
router.include_router(ws_router, prefix="/ws", tags=["WebSocket"])

