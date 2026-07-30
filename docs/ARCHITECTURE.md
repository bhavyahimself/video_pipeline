# ClipEngine — Architecture Document

## Overview

ClipEngine is an AI-powered SaaS platform that automates YouTube Shorts production at scale. Users provide a topic and channel type; the platform handles research, scriptwriting, clip sourcing, voiceover, video assembly, captions, and thumbnails — delivering a publish-ready video in minutes.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND (Next.js 14)                  │
│  Landing │ Dashboard │ Wizard │ Editor │ Library │ Settings  │
│                 Tailwind CSS + shadcn/ui                     │
└──────────────────────┬──────────────────────────────────────┘
                       │ REST + WebSocket
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    API GATEWAY (FastAPI)                     │
│  Auth │ Videos │ Scripts │ Jobs │ Billing │ Analytics │ WS   │
├─────────────────────────────────────────────────────────────┤
│  Middleware: JWT Auth │ Rate Limit │ Plan Enforcement        │
└──────┬──────────────┬──────────────┬────────────────────────┘
       │              │              │
       ▼              ▼              ▼
┌──────────┐  ┌──────────────┐  ┌──────────────────────┐
│PostgreSQL│  │    Redis      │  │  S3 / MinIO          │
│ Users    │  │ Job queue     │  │ Videos, thumbnails,  │
│ Videos   │  │ Cache         │  │ voiceovers, clips    │
│ Scripts  │  │ WS pub/sub    │  │                      │
│ Billing  │  │ Rate limits   │  │                      │
└──────────┘  └──────┬───────┘  └──────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   CELERY WORKERS                            │
│                                                             │
│  ┌─────────┐  ┌─────────┐  ┌──────────┐  ┌─────────────┐  │
│  │Research │→ │ Script  │→ │ Clips    │→ │ Voice       │  │
│  │ Agent   │  │Generator│  │ Finder   │  │ Generator   │  │
│  └─────────┘  └─────────┘  └──────────┘  └─────────────┘  │
│                                                             │
│  ┌──────────────┐  ┌──────────┐  ┌────────────────────┐    │
│  │ Assembler    │→ │ Captions │→ │ Thumbnail Gen      │    │
│  │ (FFmpeg)     │  │ (Whisper)│  │ (Pillow)           │    │
│  └──────────────┘  └──────────┘  └────────────────────┘    │
│                                                             │
│  ENGINE (video_pipeline core — reused as library)           │
└─────────────────────────────────────────────────────────────┘
```

## Tech Stack

| Layer          | Technology                           | Why                                      |
|----------------|--------------------------------------|------------------------------------------|
| Frontend       | Next.js 14, Tailwind, shadcn/ui      | Fast SSR, great DX, composable UI        |
| API            | FastAPI (Python)                     | Async, fast, auto-docs, Python ecosystem |
| Auth           | JWT + OAuth (Google/GitHub)          | Industry standard, easy integration      |
| Database       | PostgreSQL                           | Reliable, JSONB for flexible metadata    |
| Cache/Queue    | Redis                                | Celery broker, caching, pub/sub for WS   |
| Task Queue     | Celery                               | Mature, supports priority queues         |
| Storage        | S3 / MinIO                           | Scalable file storage                    |
| Video Engine   | FFmpeg + MoviePy                     | Industry standard video processing       |
| AI             | OpenAI GPT-4, ElevenLabs, Whisper    | Best-in-class for each task              |
| Payments       | Stripe                               | Gold standard for SaaS billing           |
| Deployment     | Docker + Railway/Fly.io              | Easy, scalable, cost-effective           |
| Monitoring     | Sentry + Prometheus + Grafana        | Error tracking + metrics                 |

## Data Models

### Core Entities

```
User
├── id, email, name, avatar
├── auth_provider (local/google/github)
├── subscription_tier (free/creator/studio/enterprise)
├── stripe_customer_id
├── api_keys (encrypted)
└── created_at, updated_at

Project
├── id, user_id, name, description
├── default_channel
└── created_at

Video
├── id, project_id, user_id
├── topic, channel_type
├── status (queued/researching/scripting/clipping/voicing/assembling/captioning/thumbnailing/done/failed)
├── script_id
├── voiceover_url, video_url, thumbnail_url
├── metadata (duration, file_size, etc.)
├── is_watermarked
└── created_at

Script
├── id, video_id, user_id
├── content, version
├── visual_cues (JSONB)
├── channel_type
└── created_at

Job
├── id, video_id, user_id
├── celery_task_id
├── status, progress_pct, current_step
├── priority (free/creator/studio)
├── started_at, completed_at
├── error_message
└── created_at

Subscription
├── id, user_id
├── plan (free/creator/studio/enterprise)
├── stripe_subscription_id
├── status (active/cancelled/past_due)
├── current_period_start, current_period_end
├── videos_used_this_period
└── created_at

Channel (user-custom channels, Studio+ only)
├── id, user_id
├── name, tone, format_guide
├── voice_id, voice_settings
├── clip_sources, stock_keywords
└── is_public (for marketplace)

Team
├── id, owner_id, name
├── members [{user_id, role}]
└── created_at
```

## API Design

### Auth
- `POST /api/v1/auth/register` — Email registration
- `POST /api/v1/auth/login` — Email login → JWT
- `POST /api/v1/auth/refresh` — Refresh token
- `GET  /api/v1/auth/google` — Google OAuth redirect
- `GET  /api/v1/auth/github` — GitHub OAuth redirect
- `GET  /api/v1/auth/callback/{provider}` — OAuth callback

### Videos
- `POST   /api/v1/videos` — Create video (triggers pipeline)
- `GET    /api/v1/videos` — List user's videos
- `GET    /api/v1/videos/{id}` — Get video details
- `DELETE /api/v1/videos/{id}` — Delete video
- `POST   /api/v1/videos/batch` — Batch create (Studio+)
- `POST   /api/v1/videos/{id}/upload-youtube` — Upload to YouTube

### Scripts
- `GET    /api/v1/scripts/{id}` — Get script
- `PUT    /api/v1/scripts/{id}` — Update script
- `GET    /api/v1/scripts/{id}/versions` — Version history
- `POST   /api/v1/scripts/{id}/regenerate` — Regenerate with AI

### Jobs
- `GET    /api/v1/jobs/{id}` — Job status + progress
- `POST   /api/v1/jobs/{id}/cancel` — Cancel job
- `POST   /api/v1/jobs/{id}/retry` — Retry failed job
- `WS     /api/v1/ws/jobs/{id}` — Real-time progress

### Channels
- `GET    /api/v1/channels` — List all channels (system + user)
- `POST   /api/v1/channels` — Create custom channel (Studio+)
- `PUT    /api/v1/channels/{id}` — Update custom channel
- `GET    /api/v1/channels/marketplace` — Public templates

### Billing
- `GET    /api/v1/billing/plans` — Available plans
- `POST   /api/v1/billing/checkout` — Create Stripe checkout session
- `POST   /api/v1/billing/portal` — Stripe customer portal
- `POST   /api/v1/billing/webhook` — Stripe webhook handler
- `GET    /api/v1/billing/usage` — Current period usage

### Analytics
- `GET    /api/v1/analytics/overview` — Usage overview
- `GET    /api/v1/analytics/videos` — Per-video stats
- `GET    /api/v1/analytics/youtube` — YouTube stats (if connected)

## Queue Architecture

Three Celery queues with different worker allocations:

| Queue      | Plan Tiers          | Workers | Max Concurrent |
|------------|---------------------|---------|----------------|
| `free`     | Free                | 1       | 1              |
| `creator`  | Creator             | 3       | 3              |
| `priority` | Studio, Enterprise  | 5       | 5              |

## Security

- JWT tokens with 15min access / 7d refresh rotation
- API keys encrypted at rest (Fernet)
- Rate limiting per tier via Redis sliding window
- CORS restricted to frontend domain
- Stripe webhook signature verification
- S3 presigned URLs (no direct bucket access)
- Input sanitization on all script/channel text fields

