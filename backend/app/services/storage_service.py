"""
ClipEngine — Storage Service
S3/MinIO file upload, download, and presigned URL generation.
"""

import boto3
from botocore.config import Config as BotoConfig
from pathlib import Path
from typing import Optional

from app.config import get_settings

settings = get_settings()


class StorageService:
    """Manages file storage in S3-compatible storage (MinIO locally, S3 in prod)."""

    def __init__(self):
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = boto3.client(
                "s3",
                endpoint_url=settings.S3_ENDPOINT,
                aws_access_key_id=settings.S3_ACCESS_KEY,
                aws_secret_access_key=settings.S3_SECRET_KEY,
                region_name=settings.S3_REGION,
                config=BotoConfig(signature_version="s3v4"),
            )
            # Ensure bucket exists
            try:
                self._client.head_bucket(Bucket=settings.S3_BUCKET)
            except Exception:
                self._client.create_bucket(Bucket=settings.S3_BUCKET)
        return self._client

    def upload_file(self, local_path: str, s3_key: str, content_type: Optional[str] = None) -> str:
        """Upload a file to S3 and return the public URL."""
        extra_args = {}
        if content_type:
            extra_args["ContentType"] = content_type

        self.client.upload_file(local_path, settings.S3_BUCKET, s3_key, ExtraArgs=extra_args)
        return f"{settings.S3_PUBLIC_URL}/{s3_key}"

    def upload_bytes(self, data: bytes, s3_key: str, content_type: str = "application/octet-stream") -> str:
        """Upload bytes to S3."""
        self.client.put_object(
            Bucket=settings.S3_BUCKET,
            Key=s3_key,
            Body=data,
            ContentType=content_type,
        )
        return f"{settings.S3_PUBLIC_URL}/{s3_key}"

    def get_presigned_url(self, s3_key: str, expires_in: int = 3600) -> str:
        """Generate a presigned URL for downloading a file."""
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.S3_BUCKET, "Key": s3_key},
            ExpiresIn=expires_in,
        )

    def delete_file(self, s3_key: str):
        """Delete a file from S3."""
        self.client.delete_object(Bucket=settings.S3_BUCKET, Key=s3_key)

    def upload_video_assets(self, video_id: str, output_dir: str) -> dict:
        """Upload all video assets (video, thumbnail, voiceover, captions) to S3."""
        output = Path(output_dir)
        urls = {}

        asset_map = {
            "video": ("*.mp4", "video/mp4"),
            "thumbnail": ("*.png", "image/png"),
            "voiceover": ("*.mp3", "audio/mpeg"),
            "captions": ("*.srt", "text/plain"),
        }

        for asset_type, (pattern, content_type) in asset_map.items():
            files = list(output.glob(pattern))
            if files:
                local_path = str(files[0])
                s3_key = f"videos/{video_id}/{asset_type}/{files[0].name}"
                urls[asset_type] = self.upload_file(local_path, s3_key, content_type)

        return urls


# Singleton
storage = StorageService()

