# ClipEngine — 1-Month MVP Sprint Plan

## Sprint Overview
**Goal**: Launch a functional MVP with core video generation, user accounts, billing, and a polished UI. Users can sign up, pick a plan, create videos, and download/upload them.

**Team**: Solo founder or 2-3 person team
**Start Date**: March 10, 2026
**Launch Target**: April 7, 2026 (4 weeks)

---

## Week 1: Foundation (March 10 – March 16)

### Day 1-2: Monorepo Setup + Engine Integration
- [ ] Initialize monorepo structure (backend/, frontend/, docs/)
- [ ] Move video_pipeline into backend/engine/ 
- [ ] Refactor engine config to accept injected settings (not just env vars)
- [ ] Add progress_callback support to MasterPipeline.run()
- [ ] Add watermark param to VideoAssembler
- [ ] Create backend pyproject.toml with all dependencies
- [ ] Set up Docker Compose (Postgres, Redis, MinIO, API, Worker)

### Day 3-4: Database Models + Auth
- [ ] Create SQLAlchemy models: User, Video, Script, Job, Subscription, Channel, Project
- [ ] Set up Alembic migrations
- [ ] Implement JWT auth (register, login, refresh)
- [ ] Implement Google OAuth flow
- [ ] Create auth middleware
- [ ] Write seed script for test data

### Day 5-6: Celery + Core Video Task
- [ ] Configure Celery with Redis broker
- [ ] Create `generate_video` Celery task wrapping MasterPipeline
- [ ] Implement progress reporting (task updates Redis pub/sub)
- [ ] Create 3 priority queues (free, creator, priority)
- [ ] Set up S3/MinIO storage service (upload, download, presigned URLs)
- [ ] Test full pipeline: API call → Celery task → video in S3

### Day 7: Testing + Docker
- [ ] Write unit tests for auth, video creation, job tracking
- [ ] Test Docker Compose full stack
- [ ] Fix integration issues
- [ ] Document API with FastAPI auto-docs

**Week 1 Deliverable**: Working backend that takes a topic + channel → generates a video via Celery → stores in S3. JWT auth working.

---

## Week 2: API Completion + Frontend Shell (March 17 – March 23)

### Day 8-9: API Endpoints
- [ ] `POST/GET/DELETE /api/v1/videos` — Full CRUD
- [ ] `GET /api/v1/jobs/{id}` — Job status polling
- [ ] `WS /api/v1/ws/jobs/{id}` — WebSocket progress
- [ ] `GET/PUT /api/v1/scripts/{id}` — Script editing
- [ ] `GET /api/v1/scripts/{id}/versions` — Version history
- [ ] `POST /api/v1/scripts/{id}/regenerate` — AI regeneration
- [ ] `GET /api/v1/channels` — List available channels
- [ ] `GET /api/v1/billing/usage` — Usage stats

### Day 10-11: Frontend Foundation
- [ ] Initialize Next.js 14 project with App Router
- [ ] Install Tailwind CSS + shadcn/ui
- [ ] Create auth pages (login, register) with NextAuth.js
- [ ] Create dashboard layout (sidebar, top bar)
- [ ] Create API client library (Axios wrapper with JWT interceptor)
- [ ] Implement auth context + protected routes

### Day 12-13: Video Creator Wizard
- [ ] Step 1: Topic input with AI suggestions
- [ ] Step 2: Channel type selection (visual cards)
- [ ] Step 3: Customization (voice, duration, toggles)
- [ ] Step 4: Review & Generate
- [ ] Job progress page with animated step indicator
- [ ] WebSocket hook for real-time progress updates

### Day 14: Dashboard Home
- [ ] Usage meter component
- [ ] Recent videos grid with thumbnail previews
- [ ] Quick stats cards
- [ ] Quick create button
- [ ] Empty states for new users

**Week 2 Deliverable**: Users can register, log in, create a video through a wizard, watch real-time progress, and see it on their dashboard.

---

## Week 3: Features + Polish (March 24 – March 30)

### Day 15-16: Video Library + Player
- [ ] Video library page (grid/list, filters, search)
- [ ] Video preview page with custom player
- [ ] Download button (presigned S3 URL)
- [ ] Delete video flow
- [ ] Bulk select + batch delete

### Day 17-18: Script Editor + Channel Manager
- [ ] Script editor with Tiptap rich text
- [ ] Visual cue preview panel
- [ ] Version history dropdown
- [ ] Regenerate button
- [ ] Channel manager page (list all channels)
- [ ] Channel detail view with tone/voice preview

### Day 19-20: Billing Integration
- [ ] Stripe product + price setup (4 tiers)
- [ ] `POST /api/v1/billing/checkout` → Stripe Checkout redirect
- [ ] `POST /api/v1/billing/portal` → Customer portal
- [ ] Stripe webhook handler (subscription events)
- [ ] Plan enforcement middleware (video quota check)
- [ ] Watermark logic for free tier
- [ ] Pricing page component
- [ ] Settings > Billing page

### Day 21: YouTube Upload + Polish
- [ ] YouTube OAuth connection in Settings
- [ ] "Upload to YouTube" button on video page
- [ ] YouTube upload service (Data API v3)
- [ ] UI polish pass (loading states, error states, transitions)
- [ ] Mobile responsiveness check

**Week 3 Deliverable**: Full feature set working. Users can manage videos, edit scripts, manage billing, and upload to YouTube.

---

## Week 4: Launch Prep (March 31 – April 6)

### Day 22-23: Landing Page + Marketing
- [ ] Hero section with animated pipeline demo
- [ ] Feature grid with icons
- [ ] Channel showcase carousel
- [ ] Pricing table with toggle (monthly/annual)
- [ ] FAQ section
- [ ] Footer
- [ ] SEO meta tags + OG images
- [ ] Blog post: "How I Automated YouTube Shorts Production"

### Day 24-25: Production Deployment
- [ ] Dockerfile optimization (multi-stage build)
- [ ] Production docker-compose with SSL
- [ ] Deploy to Railway (or Fly.io)
  - API server
  - Celery worker (with FFmpeg/Whisper)
  - PostgreSQL
  - Redis
  - MinIO → migrate to AWS S3
- [ ] Domain + DNS setup
- [ ] Environment variables configuration
- [ ] Health check endpoints

### Day 26-27: Monitoring + Security
- [ ] Sentry integration (backend + frontend)
- [ ] Basic Prometheus metrics
- [ ] Rate limiting verification
- [ ] Security audit (CORS, input validation, SQL injection)
- [ ] Stripe webhook testing
- [ ] Load testing (10 concurrent video generations)

### Day 28: Launch Day
- [ ] Seed 5 demo videos across different channels
- [ ] Record product demo video (using ClipEngine itself!)
- [ ] Submit to Product Hunt
- [ ] Post on Indie Hackers, Reddit (/r/SideProject, /r/SaaS)
- [ ] Tweet thread with demo GIFs
- [ ] Email launch to waitlist
- [ ] Monitor for issues, hotfix as needed

**Week 4 Deliverable**: Live product at clipengine.io with monitoring, billing, and initial users.

---

## Post-Launch (Week 5+)

### Immediate (Week 5-6)
- [ ] User feedback collection (in-app widget + Discord)
- [ ] Bug fixes from launch
- [ ] Performance optimization (generation speed)
- [ ] Batch generation feature
- [ ] Template marketplace foundation

### Short-term (Month 2-3)
- [ ] Team collaboration (Studio tier)
- [ ] Custom channel builder UI
- [ ] A/B thumbnail testing
- [ ] Analytics dashboard
- [ ] API documentation portal
- [ ] Mobile-optimized experience
- [ ] Affiliate program

### Medium-term (Month 4-6)
- [ ] Enterprise features (white-label, SSO)
- [ ] Scheduled publishing
- [ ] Multi-platform (TikTok, Instagram Reels)
- [ ] AI voice cloning
- [ ] Video remix/re-edit capability
- [ ] Integration marketplace (Zapier, Make)

---

## Resource Requirements

| Resource | Cost/Month | Notes |
|----------|-----------|-------|
| Railway/Fly.io (API + Workers) | $50-100 | Scales with usage |
| PostgreSQL (managed) | $15 | Railway included |
| Redis (managed) | $10 | Railway included |
| AWS S3 | $5-20 | Pay per GB stored |
| OpenAI API | $50-200 | Depends on volume |
| ElevenLabs | $22-99 | Depends on tier |
| Stripe | 2.9% + $0.30/txn | Per transaction |
| Domain + DNS | $15/year | clipengine.io |
| Sentry | Free tier | Up to 5K events |
| **Total** | **$170-460** | Before revenue |

## Revenue Projections (Conservative)

| Month | Free Users | Paid Users | MRR |
|-------|-----------|------------|-----|
| 1 | 200 | 20 | $1,200 |
| 2 | 600 | 60 | $3,600 |
| 3 | 1,500 | 150 | $9,000 |
| 4 | 3,000 | 300 | $18,000 |
| 5 | 5,000 | 500 | $30,000 |
| 6 | 8,000 | 800 | $48,000 |

*Assumes 10% free→paid conversion, $60 avg revenue per paid user (mix of tiers)*

