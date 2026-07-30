"""
ClipEngine — WebSocket Endpoint
Real-time job progress streaming.
"""

import asyncio
import json

import redis.asyncio as aioredis
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.config import get_settings

router = APIRouter()
settings = get_settings()


@router.websocket("/jobs/{job_id}")
async def job_progress_ws(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint for real-time job progress.
    Subscribes to Redis pub/sub channel for the job and streams updates.
    """
    await websocket.accept()

    redis = aioredis.from_url(settings.REDIS_URL)
    pubsub = redis.pubsub()
    channel = f"job:{job_id}:progress"

    try:
        await pubsub.subscribe(channel)

        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message and message["type"] == "message":
                data = json.loads(message["data"])
                await websocket.send_json(data)

                # Close on completion
                if data.get("status") in ("done", "failed", "cancelled"):
                    break
            else:
                # Send heartbeat to keep connection alive
                try:
                    await websocket.send_json({"type": "heartbeat"})
                except Exception:
                    break

            await asyncio.sleep(0.5)

    except WebSocketDisconnect:
        pass
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.close()
        await redis.close()

